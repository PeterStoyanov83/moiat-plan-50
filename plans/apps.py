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
