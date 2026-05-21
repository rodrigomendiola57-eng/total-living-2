from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0015_construction_area_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='technical_sheet',
            field=models.FileField(
                blank=True,
                help_text='PDF o Word (.doc/.docx) subido por el equipo. Máximo 15 MB.',
                null=True,
                upload_to='properties/technical_sheets/%Y/%m/',
                verbose_name='Ficha técnica (archivo)',
            ),
        ),
    ]
