from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0006_homecontent_singleton_key_nosotroscontent_singleton_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='nosotroscontent',
            name='values_title',
            field=models.CharField(default='Valores Total Living', max_length=140),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='values_subtitle',
            field=models.CharField(
                default='Los principios que guían cada decisión.',
                max_length=260,
            ),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_1_icon',
            field=models.CharField(default='bi-heart', max_length=48),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_1_title',
            field=models.CharField(default='Pasión por el Servicio', max_length=140),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_1_text',
            field=models.CharField(
                default='Cada interacción importa: escuchamos, respondemos y acompañamos con energía y cercanía.',
                max_length=400,
            ),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_2_icon',
            field=models.CharField(default='bi-shield-check', max_length=48),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_2_title',
            field=models.CharField(default='Integridad', max_length=140),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_2_text',
            field=models.CharField(
                default='Transparencia y criterio profesional en cada paso, sin atajos ni promesas vacías.',
                max_length=400,
            ),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_3_icon',
            field=models.CharField(default='bi-people', max_length=48),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_3_title',
            field=models.CharField(default='Trabajo en Equipo', max_length=140),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_3_text',
            field=models.CharField(
                default='Coordinación real entre especialistas para que tu operación avance con orden.',
                max_length=400,
            ),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_4_icon',
            field=models.CharField(default='bi-globe2', max_length=48),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_4_title',
            field=models.CharField(default='Responsabilidad Social', max_length=140),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_4_text',
            field=models.CharField(
                default='Contribuimos con prácticas conscientes y relaciones de respeto con clientes y comunidad.',
                max_length=400,
            ),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_5_icon',
            field=models.CharField(default='bi-gem', max_length=48),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_5_title',
            field=models.CharField(default='Imagen Impecable', max_length=140),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='value_5_text',
            field=models.CharField(
                default='Presentación, comunicación y estándares que reflejan la calidad de Total Living.',
                max_length=400,
            ),
        ),
    ]
