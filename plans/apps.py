import atexit
import os

from django.apps import AppConfig
from posthog import Posthog


posthog_client = None


class PlansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plans'
    verbose_name = 'Планове'

    def ready(self):
        global posthog_client
        if posthog_client is None:
            # Analytics is optional: when the key is absent (local dev, tests, or
            # prod before it's configured) the client runs disabled — capture/set
            # become safe no-ops instead of crashing app startup.
            api_key = os.environ.get('POSTHOG_API_KEY')
            posthog_client = Posthog(
                project_api_key=api_key or 'phc_disabled',
                host=os.environ.get('POSTHOG_HOST', 'https://eu.i.posthog.com'),
                enable_exception_autocapture=bool(api_key),
                disabled=not api_key,
            )
            atexit.register(posthog_client.shutdown)
            self._connect_allauth_signals()

    @staticmethod
    def _connect_allauth_signals():
        from django.dispatch import receiver
        from allauth.account.signals import user_signed_up, user_logged_in

        @receiver(user_signed_up)
        def on_user_signed_up(request, user, **kwargs):
            distinct_id = str(user.pk)
            posthog_client.set(
                distinct_id=distinct_id,
                properties={
                    'has_google': user.socialaccount_set.filter(provider='google').exists(),
                    'has_password': user.has_usable_password(),
                },
            )
            posthog_client.capture(
                distinct_id=distinct_id,
                event='user_signed_up',
                properties={
                    'signup_method': 'google' if not user.has_usable_password() else 'email',
                },
            )

        @receiver(user_logged_in)
        def on_user_logged_in(request, user, **kwargs):
            distinct_id = str(user.pk)
            posthog_client.set(
                distinct_id=distinct_id,
                properties={
                    'has_google': user.socialaccount_set.filter(provider='google').exists(),
                    'has_password': user.has_usable_password(),
                },
            )
            posthog_client.capture(
                distinct_id=distinct_id,
                event='user_logged_in',
                properties={
                    'login_method': 'google' if not user.has_usable_password() else 'email',
                },
            )
