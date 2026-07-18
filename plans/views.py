import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import QuestionnaireForm, FeedbackForm
from .models import QuestionnaireResponse, UserPlan, Feedback, StepCompletion
from .profile_logic import determine_profile, generate_plan
from .step_engine import offer_step, offer_choices, mark_done, today_progress, weekly_history
from .ai_companion import pick_opening_step
from . import apps


def home(request):
    return render(request, 'plans/home.html')


def privacy(request):
    return render(request, 'plans/privacy.html')


def _session_response(request):
    """The QuestionnaireResponse for this visitor.

    Logged-in (Google) users get their most recent response on any device; we
    also claim an anonymous session response on first login. Anonymous visitors
    fall back to the session-scoped response.
    """
    if request.user.is_authenticated:
        rid = request.session.get('response_id')
        if rid:
            QuestionnaireResponse.objects.filter(pk=rid, user__isnull=True).update(user=request.user)
        return request.user.questionnaire_responses.order_by('-created_at').first()
    rid = request.session.get('response_id')
    if not rid:
        return None
    return QuestionnaireResponse.objects.filter(pk=rid).first()


def questionnaire(request):
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            if request.user.is_authenticated:
                response.user = request.user
            response.save()
            profile_type = determine_profile(response)
            plan_data = generate_plan(response, profile_type)
            plan = UserPlan.objects.create(
                response=response,
                profile_type=profile_type,
                profile_description=plan_data['description'],
                nutrition_plan=plan_data['nutrition'],
                movement_plan=plan_data['movement'],
                habits_plan=plan_data['habits'],
                financial_habit=plan_data['financial'],
                social_plan=plan_data['social'],
            )
            # Remember this person for their daily ritual (no login in MVP),
            # then send them into the one-step ritual — not the old dashboard.
            request.session['response_id'] = response.pk
            distinct_id = str(request.user.pk) if request.user.is_authenticated else f'response-{response.pk}'
            if request.user.is_authenticated:
                apps.posthog_client.set(
                    distinct_id=distinct_id,
                    properties={'has_personalized_plan': True},
                )
            apps.posthog_client.capture(
                distinct_id=distinct_id,
                event='questionnaire_completed',
                properties={'profile_type': profile_type, 'authenticated': request.user.is_authenticated},
            )
            return redirect('ritual')
    else:
        # Prefill the name from the Google profile when signed in.
        initial = {}
        if request.user.is_authenticated and request.user.first_name:
            initial['first_name'] = request.user.first_name
        form = QuestionnaireForm(initial=initial)
    return render(request, 'plans/questionnaire.html', {'form': form})


def ritual(request):
    """The daily one-step ritual — the app's home after the interview."""
    response = _session_response(request)
    if response is None:
        return redirect('questionnaire')
    # AI companion writes a warm opening line (when enabled). Actions now come
    # from the ActionDef library (core habits + missions), scaled to the level.
    _, companion_message = pick_opening_step(response)
    from .daily import today_actions
    choices = today_actions(response)
    plan = getattr(response, 'plan', None)
    context = {
        'greeting_name': response.first_name or '',
        'initial_choices': json.dumps(choices, ensure_ascii=False),
        'companion_message': companion_message or '',
        'progress': json.dumps(today_progress(response)),
        'plan_id': plan.pk if plan else None,
        'response_id': response.pk,
    }
    return render(request, 'plans/ritual.html', context)


def _build_choices(response, first=None):
    """Up to 3 options; if ``first`` given (AI pick), it leads the list."""
    if first:
        rest = offer_choices(response, n=2, exclude=[first['text']])
        return [first] + rest
    return offer_choices(response, n=3)


@require_POST
def step_done(request):
    response = _session_response(request)
    if response is None:
        return JsonResponse({'error': 'no-session'}, status=400)
    slug = request.POST.get('action', '').strip()
    text = request.POST.get('text', '').strip()
    category = request.POST.get('category', '').strip()

    if slug:
        # New ActionDef flow. The web shell has no sensors, so a tap is a
        # trust-based completion (CONFIRMED); real sensor/timer/photo verification
        # happens on mobile via the /api/verify endpoints (verification.py).
        from .models import ActionDef, ActionLog, UserProgram
        from .progression import evaluate_level
        action = ActionDef.objects.filter(slug=slug).first()
        if action:
            today = timezone.localdate()
            ActionLog.objects.create(
                response=response, action=action, date=today,
                status=ActionLog.CONFIRMED, verification_type=action.verification_type,
            )
            # Bridge to StepCompletion so streak / tree / progress stay consistent.
            mark_done(response, text or action.title, category or action.category)
            # System-driven level check (no-op until the level's window elapses).
            program, _ = UserProgram.objects.get_or_create(response=response)
            evaluate_level(program, today)
            distinct_id = str(request.user.pk) if request.user.is_authenticated else f'response-{response.pk}'
            apps.posthog_client.capture(
                distinct_id=distinct_id,
                event='daily_action_completed',
                properties={
                    'action_slug': action.slug,
                    'category': action.category,
                    'verification_type': action.verification_type,
                    'current_level': program.current_level,
                },
            )
        from .daily import today_actions
        return JsonResponse({'choices': today_actions(response), 'progress': today_progress(response)})

    # Legacy fallback (old knowledge-base flow / existing tests).
    if text:
        mark_done(response, text, category)
    return JsonResponse({'choices': _build_choices(response), 'progress': today_progress(response)})


@require_POST
def step_swap(request):
    response = _session_response(request)
    if response is None:
        return JsonResponse({'error': 'no-session'}, status=400)
    exclude = [e for e in request.POST.getlist('exclude') if e]
    return JsonResponse({'next': offer_step(response, exclude=exclude),
                         'progress': today_progress(response)})


def progress(request):
    """Напредък — streak, weekly history, and recent completed steps."""
    response = _session_response(request)
    if response is None:
        return redirect('questionnaire')
    prog = today_progress(response)
    plan = getattr(response, 'plan', None)
    # Living tree: seeded per person, grows with total completed steps.
    seed = (request.user.email if request.user.is_authenticated and request.user.email
            else f'resp-{response.pk}')
    month = timezone.localdate().month
    season = ('spring' if month in (3, 4, 5) else 'summer' if month in (6, 7, 8)
              else 'autumn' if month in (9, 10, 11) else 'spring')
    # Living tree: system-driven level (never user-picked) + gentle inactivity health.
    from .tree_state import compute_tree_state
    tree = compute_tree_state(response)
    context = {
        'greeting_name': response.first_name or '',
        'streak': prog['streak'],
        'done_today': prog['done_today'],
        'total': response.step_completions.count(),
        'recent': response.step_completions.all()[:12],
        'plan_id': plan.pk if plan else None,
        'response_id': response.pk,
        'tree_seed': seed,
        'tree_season': season,
        'tree_level': tree['level'],
        'tree_health': tree['health'],
        'tree_dormant': 'true' if tree['dormant'] else 'false',
    }
    return render(request, 'plans/progress.html', context)


def profile(request):
    """Account profile — info, progress, and links to the standard auth actions."""
    if not request.user.is_authenticated:
        return redirect('account_login')
    resp = request.user.questionnaire_responses.order_by('-created_at').first()
    prog = today_progress(resp) if resp else {'done_today': 0, 'streak': 0}
    total = StepCompletion.objects.filter(response__user=request.user).count()
    has_google = request.user.socialaccount_set.filter(provider='google').exists()
    has_password = request.user.has_usable_password()
    plan = getattr(resp, 'plan', None) if resp else None
    return render(request, 'plans/profile.html', {
        'prog': prog, 'total': total, 'has_google': has_google,
        'has_password': has_password, 'plan_id': plan.pk if plan else None,
    })


def result(request, plan_id):
    plan = get_object_or_404(UserPlan, pk=plan_id)
    return render(request, 'plans/result.html', {'plan': plan})


def download_pdf(request, plan_id):
    plan = get_object_or_404(UserPlan, pk=plan_id)
    template = get_template('plans/pdf_plan.html')
    html_string = template.render({'plan': plan})

    try:
        from weasyprint import HTML
        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="1step_{plan_id}.pdf"'
        distinct_id = (
            str(request.user.pk) if request.user.is_authenticated else f'response-{plan.response_id}'
        )
        apps.posthog_client.capture(
            distinct_id=distinct_id,
            event='plan_downloaded',
            properties={'profile_type': plan.profile_type, 'authenticated': request.user.is_authenticated},
        )
        return response
    except ImportError:
        return HttpResponse(
            'WeasyPrint не е инсталиран. Моля, инсталирайте го с: pip install weasyprint',
            status=500,
        )


def feedback(request, response_id):
    questionnaire_response = get_object_or_404(QuestionnaireResponse, pk=response_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.response = questionnaire_response
            fb.save()
            distinct_id = (
                str(request.user.pk) if request.user.is_authenticated else f'response-{questionnaire_response.pk}'
            )
            apps.posthog_client.capture(
                distinct_id=distinct_id,
                event='feedback_submitted',
                properties={
                    'clarity_score': fb.clarity_score,
                    'usefulness_score': fb.usefulness_score,
                    'realistic_score': fb.realistic_score,
                    'would_use_again': fb.would_use_again,
                    'would_pay': fb.would_pay,
                    'suggested_price': fb.suggested_price or 'not_provided',
                },
            )
            return redirect('feedback_success')
    else:
        form = FeedbackForm()
    return render(request, 'plans/feedback.html', {
        'form': form,
        'response': questionnaire_response,
    })


def feedback_success(request):
    return render(request, 'plans/feedback_success.html')
