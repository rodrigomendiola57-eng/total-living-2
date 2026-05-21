from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0004_alter_developmentimage_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='development',
            name='subtitle',
            field=models.CharField(
                blank=True,
                help_text='Ej. Residencial vertical · Zona norte de Querétaro',
                max_length=280,
                verbose_name='Subtítulo / tagline',
            ),
        ),
        migrations.AddField(
            model_name='development',
            name='developer_name',
            field=models.CharField(
                blank=True,
                help_text='Nombre comercial del desarrollador (opcional).',
                max_length=200,
                verbose_name='Desarrollador o promotora',
            ),
        ),
        migrations.AddField(
            model_name='development',
            name='amenities_text',
            field=models.TextField(
                blank=True,
                help_text='Una amenidad por línea (alberca, gimnasio, cowork, etc.).',
                verbose_name='Amenidades (lista)',
            ),
        ),
        migrations.AddField(
            model_name='development',
            name='website_url',
            field=models.URLField(
                blank=True,
                max_length=500,
                verbose_name='Sitio web del desarrollo',
            ),
        ),
    ]
