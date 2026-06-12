import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moiat_plan_50.settings')
application = get_wsgi_application()
