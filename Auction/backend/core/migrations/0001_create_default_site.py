from django.db import migrations
from django.conf import settings

def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.create(
        id=settings.SITE_ID if hasattr(settings, 'SITE_ID') else 1,
        domain='localhost:8000',
        name='Auction Platform'
    )

class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(create_default_site),
    ] 