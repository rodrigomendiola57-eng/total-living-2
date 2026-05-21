# Descripción, otras características y plantas arquitectónicas por modelo.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0011_development_slug_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentunitmodel',
            name='description',
            field=models.TextField(
                blank=True,
                help_text='Texto breve junto a la ficha (opcional).',
                verbose_name='Descripción',
            ),
        ),
        migrations.AddField(
            model_name='developmentunitmodel',
            name='other_features_text',
            field=models.TextField(
                blank=True,
                help_text='Una viñeta por línea (ej. Jardín, Área de lavado, 2 cajones).',
                verbose_name='Otras características',
            ),
        ),
        migrations.CreateModel(
            name='DevelopmentUnitModelFloorPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'image',
                    models.ImageField(
                        upload_to='developments/unit_models/floor_plans/',
                        verbose_name='Imagen de planta',
                    ),
                ),
                (
                    'label',
                    models.CharField(
                        default='Planta',
                        help_text='Ej. Planta baja, Nivel 2.',
                        max_length=120,
                        verbose_name='Etiqueta (pestaña)',
                    ),
                ),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                (
                    'unit_model',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='floor_plans',
                        to='developments.developmentunitmodel',
                        verbose_name='Modelo',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Planta arquitectónica',
                'verbose_name_plural': 'Plantas arquitectónicas',
                'ordering': ['order', 'id'],
            },
        ),
    ]
