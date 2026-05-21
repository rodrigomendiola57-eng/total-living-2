# Generated migration for extended property fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        # Campos adicionales de medidas
        migrations.AddField(
            model_name='property',
            name='half_bathrooms',
            field=models.PositiveIntegerField(default=0, verbose_name='Medios Baños'),
        ),
        migrations.AddField(
            model_name='property',
            name='front_measure',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Medida de Frente (m)'),
        ),
        migrations.AddField(
            model_name='property',
            name='back_measure',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Medida de Fondo (m)'),
        ),
        migrations.AddField(
            model_name='property',
            name='rooms',
            field=models.PositiveIntegerField(default=0, verbose_name='Ambientes'),
        ),
        migrations.AddField(
            model_name='property',
            name='maintenance_fee',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cuota de Mantenimiento'),
        ),
        
        # Distribución (Boolean fields)
        migrations.AddField(model_name='property', name='has_sala', field=models.BooleanField(default=False, verbose_name='Sala')),
        migrations.AddField(model_name='property', name='has_comedor', field=models.BooleanField(default=False, verbose_name='Comedor')),
        migrations.AddField(model_name='property', name='has_cocina', field=models.BooleanField(default=False, verbose_name='Cocina Integral')),
        migrations.AddField(model_name='property', name='has_estudio', field=models.BooleanField(default=False, verbose_name='Estudio')),
        migrations.AddField(model_name='property', name='has_despensa', field=models.BooleanField(default=False, verbose_name='Despensa')),
        migrations.AddField(model_name='property', name='has_cuarto_tv', field=models.BooleanField(default=False, verbose_name='Cuarto TV')),
        migrations.AddField(model_name='property', name='has_gimnasio', field=models.BooleanField(default=False, verbose_name='Gimnasio')),
        migrations.AddField(model_name='property', name='has_balcon', field=models.BooleanField(default=False, verbose_name='Balcón')),
        migrations.AddField(model_name='property', name='has_jardin', field=models.BooleanField(default=False, verbose_name='Jardín')),
        migrations.AddField(model_name='property', name='has_patio', field=models.BooleanField(default=False, verbose_name='Patio Trasero')),
        migrations.AddField(model_name='property', name='has_roof_garden', field=models.BooleanField(default=False, verbose_name='Roof Garden')),
        migrations.AddField(model_name='property', name='has_area_lavado', field=models.BooleanField(default=False, verbose_name='Área de Lavado')),
        migrations.AddField(model_name='property', name='has_bodega', field=models.BooleanField(default=False, verbose_name='Bodega')),
        
        # Amenidades
        migrations.AddField(model_name='property', name='amenity_salon', field=models.BooleanField(default=False, verbose_name='Salón de Usos Múltiples')),
        migrations.AddField(model_name='property', name='amenity_vigilancia', field=models.BooleanField(default=False, verbose_name='Vigilancia 24/7')),
        migrations.AddField(model_name='property', name='amenity_acceso', field=models.BooleanField(default=False, verbose_name='Acceso Controlado')),
        migrations.AddField(model_name='property', name='amenity_areas_verdes', field=models.BooleanField(default=False, verbose_name='Áreas Verdes')),
        migrations.AddField(model_name='property', name='amenity_juegos', field=models.BooleanField(default=False, verbose_name='Juegos Infantiles')),
        migrations.AddField(model_name='property', name='amenity_gimnasio', field=models.BooleanField(default=False, verbose_name='Gimnasio')),
        migrations.AddField(model_name='property', name='amenity_alberca', field=models.BooleanField(default=False, verbose_name='Alberca')),
        migrations.AddField(model_name='property', name='amenity_cancha_futbol', field=models.BooleanField(default=False, verbose_name='Cancha de Fútbol')),
        migrations.AddField(model_name='property', name='amenity_cancha_tenis', field=models.BooleanField(default=False, verbose_name='Cancha de Tenis')),
        migrations.AddField(model_name='property', name='amenity_cancha_basket', field=models.BooleanField(default=False, verbose_name='Cancha de Basketball')),
        migrations.AddField(model_name='property', name='amenity_asadores', field=models.BooleanField(default=False, verbose_name='Zona de Asadores')),
        migrations.AddField(model_name='property', name='amenity_pet_friendly', field=models.BooleanField(default=False, verbose_name='Pet Friendly')),
        
        # Servicios
        migrations.AddField(model_name='property', name='service_agua', field=models.BooleanField(default=False, verbose_name='Agua')),
        migrations.AddField(model_name='property', name='service_drenaje', field=models.BooleanField(default=False, verbose_name='Drenaje')),
        migrations.AddField(model_name='property', name='service_luz', field=models.BooleanField(default=False, verbose_name='Luz')),
        migrations.AddField(model_name='property', name='service_gas', field=models.BooleanField(default=False, verbose_name='Gas Estacionario')),
        migrations.AddField(model_name='property', name='service_internet', field=models.BooleanField(default=False, verbose_name='Internet')),
        migrations.AddField(model_name='property', name='service_fibra', field=models.BooleanField(default=False, verbose_name='Fibra Óptica')),
        migrations.AddField(model_name='property', name='service_cable', field=models.BooleanField(default=False, verbose_name='TV Cable')),
        migrations.AddField(model_name='property', name='service_telefono', field=models.BooleanField(default=False, verbose_name='Línea Telefónica')),
        migrations.AddField(model_name='property', name='service_cisterna', field=models.BooleanField(default=False, verbose_name='Cisterna')),
        migrations.AddField(model_name='property', name='service_hidroneumatico', field=models.BooleanField(default=False, verbose_name='Hidroneumático')),
        migrations.AddField(model_name='property', name='service_aire', field=models.BooleanField(default=False, verbose_name='Aire Acondicionado')),
        migrations.AddField(model_name='property', name='service_boiler', field=models.BooleanField(default=False, verbose_name='Boiler')),
    ]
