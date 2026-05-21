# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_property_google_maps_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='process',
            field=models.CharField(
                choices=[
                    ('en_busqueda', 'En Búsqueda'),
                    ('en_negociacion', 'En Negociación'),
                    ('en_proceso_legal', 'En Proceso Legal'),
                    ('en_escrituracion', 'En Escrituración'),
                    ('cerrado', 'Cerrado'),
                    ('cancelado', 'Cancelado'),
                    ('no_aplica', 'No Aplica')
                ],
                default='en_busqueda',
                help_text='Etapa actual en el proceso de venta/renta',
                max_length=30,
                verbose_name='Proceso/Etapa'
            ),
        ),
    ]
