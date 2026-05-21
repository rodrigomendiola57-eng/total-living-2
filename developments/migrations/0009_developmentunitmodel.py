# Generated manually for DevelopmentUnitModel

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0008_development_latitude_longitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevelopmentUnitModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Nombre del modelo')),
                ('slug', models.SlugField(max_length=130, verbose_name='Slug (URL)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('bedrooms', models.PositiveSmallIntegerField(default=0, verbose_name='Recámaras')),
                ('bathrooms', models.DecimalField(decimal_places=1, default=0, max_digits=4, verbose_name='Baños', help_text='Ej. 2 o 2.5')),
                ('construction_m2', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='M² de construcción')),
                ('price_from', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Precio desde', help_text='Opcional; si está vacío se puede mostrar el precio del desarrollo.')),
                ('card_image', models.ImageField(blank=True, null=True, upload_to='developments/unit_models/', verbose_name='Imagen (tarjeta)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('development', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_models', to='developments.development', verbose_name='Desarrollo')),
            ],
            options={
                'verbose_name': 'Modelo de unidad',
                'verbose_name_plural': 'Modelos de unidad',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='developmentunitmodel',
            constraint=models.UniqueConstraint(fields=('development', 'slug'), name='developments_unitmodel_dev_slug_uniq'),
        ),
    ]
