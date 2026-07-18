from django.conf import settings


def google_flags(request):
    """Expose whether Google Sign-In is configured, for templates."""
    return {'google_enabled': settings.GOOGLE_OAUTH_ENABLED}


def nav_context(request):
    """Provide the current visitor's plan id to every template.

    Lets the shared bottom nav show the „Пълен план" tab on all pages without
    each view having to pass it. Mirrors views._session_response (logged-in user's
    latest response, else the session-scoped one). Never raises on template render.
    """
    from .models import QuestionnaireResponse
    plan_id = None
    try:
        response = None
        if request.user.is_authenticated:
            response = request.user.questionnaire_responses.order_by('-created_at').first()
        else:
            rid = request.session.get('response_id')
            if rid:
                response = QuestionnaireResponse.objects.filter(pk=rid).first()
        if response is not None:
            plan = getattr(response, 'plan', None)
            plan_id = plan.pk if plan else None
    except Exception:
        plan_id = None
    return {'nav_plan_id': plan_id}
