from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0005_development_subtitle_developer_amenities_website'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevelopmentsPageConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'hero_background',
                    models.ImageField(
                        blank=True,
                        help_text='Se muestra detrás del título en /desarrollos/. Recomendado: horizontal, alta resolución.',
                        null=True,
                        upload_to='developments/hero/',
                        verbose_name='Imagen de fondo (hero “Desarrollos únicos”)',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Configuración página desarrollos',
                'verbose_name_plural': 'Configuración página desarrollos',
            },
        ),
        migrations.AddField(
            model_name='development',
            name='product_type',
            field=models.CharField(
                choices=[
                    ('casa', 'Casa / residencial'),
                    ('depto', 'Departamento'),
                    ('mixto', 'Mixto'),
                    ('terreno', 'Terreno / lote'),
                ],
                default='mixto',
                help_text='Para filtrar en el listado público (casa, depto, etc.).',
                max_length=20,
                verbose_name='Tipo de producto',
            ),
        ),
    ]
