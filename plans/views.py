from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template

from .forms import QuestionnaireForm, FeedbackForm
from .models import QuestionnaireResponse, UserPlan, Feedback
from .profile_logic import determine_profile, generate_plan


def home(request):
    return render(request, 'plans/home.html')


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
            return redirect('result', plan_id=plan.pk)
    else:
        form = QuestionnaireForm()
    return render(request, 'plans/questionnaire.html', {'form': form})


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
        response['Content-Disposition'] = f'attachment; filename="moiat_plan_50_{plan_id}.pdf"'
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
