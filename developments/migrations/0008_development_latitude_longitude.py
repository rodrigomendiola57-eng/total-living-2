from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0007_developmentamenity_development_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='development',
            name='latitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text='Coordenada GPS para centrar el mapa.',
                max_digits=9,
                null=True,
                verbose_name='Latitud',
            ),
        ),
        migrations.AddField(
            model_name='development',
            name='longitude',
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text='Coordenada GPS para centrar el mapa.',
                max_digits=9,
                null=True,
                verbose_name='Longitud',
            ),
        ),
    ]
