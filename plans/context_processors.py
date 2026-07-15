from django.conf import settings


def google_flags(request):
    """Expose whether Google Sign-In is configured, for templates."""
    return {'google_enabled': settings.GOOGLE_OAUTH_ENABLED}
