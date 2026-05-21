from django.db import migrations


def copy_area_to_construction(apps, schema_editor):
    Property = apps.get_model('properties', 'Property')
    for prop in Property.objects.filter(construction_area__isnull=True).exclude(area__isnull=True):
        prop.construction_area = prop.area
        prop.save(update_fields=['construction_area'])


class Migration(migrations.Migration):
    dependencies = [
        ('properties', '0012_remove_property_amenity_acceso_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_area_to_construction, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='property',
            name='area',
        ),
    ]

