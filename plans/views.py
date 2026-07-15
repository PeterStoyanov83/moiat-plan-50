import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views.decorators.http import require_POST

from .forms import QuestionnaireForm, FeedbackForm
from .models import QuestionnaireResponse, UserPlan, Feedback
from .profile_logic import determine_profile, generate_plan
from .step_engine import offer_step, mark_done, today_progress, weekly_history


def home(request):
    return render(request, 'plans/home.html')


def privacy(request):
    return render(request, 'plans/privacy.html')


def _session_response(request):
    """The QuestionnaireResponse tied to this browser session, or None."""
    rid = request.session.get('response_id')
    if not rid:
        return None
    return QuestionnaireResponse.objects.filter(pk=rid).first()


def questionnaire(request):
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            response = form.save()
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
            return redirect('ritual')
    else:
        form = QuestionnaireForm()
    return render(request, 'plans/questionnaire.html', {'form': form})


def ritual(request):
    """The daily one-step ritual — the app's home after the interview."""
    response = _session_response(request)
    if response is None:
        return redirect('questionnaire')
    step = offer_step(response)
    plan = getattr(response, 'plan', None)
    context = {
        'greeting_name': response.first_name or '',
        'initial_step': json.dumps(step, ensure_ascii=False),
        'progress': json.dumps(today_progress(response)),
        'plan_id': plan.pk if plan else None,
        'response_id': response.pk,
    }
    return render(request, 'plans/ritual.html', context)


@require_POST
def step_done(request):
    response = _session_response(request)
    if response is None:
        return JsonResponse({'error': 'no-session'}, status=400)
    text = request.POST.get('text', '').strip()
    category = request.POST.get('category', '').strip()
    if text:
        mark_done(response, text, category)
    return JsonResponse({'next': offer_step(response), 'progress': today_progress(response)})


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
    history = weekly_history(response)
    plan = getattr(response, 'plan', None)
    context = {
        'greeting_name': response.first_name or '',
        'streak': prog['streak'],
        'done_today': prog['done_today'],
        'total': response.step_completions.count(),
        'history': history,
        'max_count': max([h['count'] for h in history] + [1]),
        'recent': response.step_completions.all()[:12],
        'plan_id': plan.pk if plan else None,
        'response_id': response.pk,
    }
    return render(request, 'plans/progress.html', context)


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
            return redirect('feedback_success')
    else:
        form = FeedbackForm()
    return render(request, 'plans/feedback.html', {
        'form': form,
        'response': questionnaire_response,
    })


def feedback_success(request):
    return render(request, 'plans/feedback_success.html')
