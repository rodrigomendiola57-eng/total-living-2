# Etiqueta por defecto de planta: Planta A.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0013_developmentimage_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentunitmodelfloorplan',
            name='label',
            field=models.CharField(
                default='Planta A',
                help_text='Ej. Planta A, Planta B, Planta alta.',
                max_length=120,
                verbose_name='Etiqueta (pestaña)',
            ),
        ),
    ]
