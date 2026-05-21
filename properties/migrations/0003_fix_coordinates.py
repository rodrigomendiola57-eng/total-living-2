# Generated migration to fix invalid coordinates

from django.db import migrations

def fix_invalid_coordinates(apps, schema_editor):
    Property = apps.get_model('properties', 'Property')
    # Set all coordinates to NULL to avoid decimal errors
    Property.objects.all().update(latitude=None, longitude=None)

class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0002_add_extended_fields'),
    ]

    operations = [
        migrations.RunPython(fix_invalid_coordinates),
    ]
