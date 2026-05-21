# Categoría de imagen (portada / galería / planos) y datos desde is_main.

from django.db import migrations, models


def forwards_category_from_is_main(apps, schema_editor):
    DevelopmentImage = apps.get_model('developments', 'DevelopmentImage')
    DevelopmentImage.objects.filter(is_main=True).update(category='cover')


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0012_unit_model_description_floorplans'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentimage',
            name='category',
            field=models.CharField(
                choices=[
                    ('cover', 'Imagen principal (portada)'),
                    ('gallery', 'Galería general'),
                    ('plans', 'Planos / amenidades'),
                ],
                default='gallery',
                help_text='Portada: hero del desarrollo. Galería: mosaico principal. Planos: sección aparte.',
                max_length=16,
                verbose_name='Categoría',
            ),
        ),
        migrations.RunPython(forwards_category_from_is_main, migrations.RunPython.noop),
    ]
