from django.conf import settings
from django.db import migrations


def set_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    domain = getattr(settings, 'RAILWAY_PUBLIC_DOMAIN', '') or 'web-production-e3b54.up.railway.app'
    Site.objects.update_or_create(
        pk=getattr(settings, 'SITE_ID', 1),
        defaults={'domain': domain, 'name': '1Step'},
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('plans', '0005_questionnaireresponse_user'),
        ('sites', '0002_alter_domain_unique'),
    ]
    operations = [migrations.RunPython(set_site, noop)]
