from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0001_initial'),
        ('properties', '0007_carouselslide'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='region',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='properties',
                to='regions.region',
                verbose_name='Región',
            ),
        ),
    ]
