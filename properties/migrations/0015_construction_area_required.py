from decimal import Decimal

from django.db import migrations, models
import django.core.validators


def backfill_construction_area(apps, schema_editor):
    Property = apps.get_model('properties', 'Property')
    qs = Property.objects.filter(construction_area__isnull=True)
    for prop in qs.iterator():
        if prop.lot_area is not None and prop.lot_area > 0:
            prop.construction_area = prop.lot_area
        else:
            prop.construction_area = Decimal('1')
        prop.save(update_fields=['construction_area'])


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0014_property_image_main_unique_and_construction_index'),
    ]

    operations = [
        migrations.RunPython(backfill_construction_area, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='property',
            name='construction_area',
            field=models.DecimalField(
                decimal_places=2,
                help_text='Área construida en metros cuadrados (obligatorio)',
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name='Área de Construcción (m²)',
            ),
        ),
    ]
