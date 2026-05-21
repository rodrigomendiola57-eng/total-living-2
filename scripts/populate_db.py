import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from properties.models import Property
from django.utils import timezone

# Datos aleatorios
colonias_cdmx = ['Polanco', 'Condesa', 'Roma Norte', 'Coyoacán', 'Del Valle', 'Narvarte', 'Santa Fe', 'Lomas de Chapultepec', 'San Ángel', 'Pedregal']
estados = ['Ciudad de México', 'Estado de México', 'Jalisco', 'Nuevo León', 'Querétaro']
ciudades = ['Ciudad de México', 'Guadalajara', 'Monterrey', 'Querétaro', 'Puebla']

google_maps_url = 'https://maps.app.goo.gl/GJaimFEpta8N6NeP7'

# Limpiar propiedades existentes
Property.objects.all().delete()
print("Base de datos limpiada")

# Crear 5 casas
casas_data = [
    {
        'title': 'Hermosa Casa en Polanco con Jardín',
        'description': 'Espectacular casa de lujo en una de las mejores zonas de la ciudad. Cuenta con amplios espacios, acabados de primera calidad, jardín privado y excelente iluminación natural. Perfecta para familias que buscan confort y exclusividad.',
        'bedrooms': 4,
        'bathrooms': 3,
        'parking_spaces': 2,
        'price': Decimal('8500000.00'),
        'lot_area': Decimal('350.00'),
        'construction_area': Decimal('280.00'),
    },
    {
        'title': 'Casa Moderna en Coyoacán con Alberca',
        'description': 'Residencia contemporánea con diseño arquitectónico único. Incluye alberca, terraza amplia, cocina integral de lujo y sistema de domótica. Ubicada en zona tranquila y segura con excelente plusvalía.',
        'bedrooms': 5,
        'bathrooms': 4,
        'parking_spaces': 3,
        'price': Decimal('12000000.00'),
        'lot_area': Decimal('450.00'),
        'construction_area': Decimal('380.00'),
    },
    {
        'title': 'Casa Acogedora en Del Valle',
        'description': 'Casa familiar en excelente ubicación, cerca de escuelas, centros comerciales y transporte público. Espacios funcionales, jardín trasero y cochera techada. Ideal para familias que buscan comodidad y accesibilidad.',
        'bedrooms': 3,
        'bathrooms': 2,
        'parking_spaces': 2,
        'price': Decimal('5800000.00'),
        'lot_area': Decimal('200.00'),
        'construction_area': Decimal('180.00'),
    },
    {
        'title': 'Casa Residencial en Santa Fe',
        'description': 'Impresionante residencia en zona exclusiva de Santa Fe. Cuenta con amplias recámaras, estudio, gimnasio privado, roof garden y vista panorámica. Acabados de lujo y tecnología de punta en toda la propiedad.',
        'bedrooms': 6,
        'bathrooms': 5,
        'parking_spaces': 4,
        'price': Decimal('18500000.00'),
        'lot_area': Decimal('600.00'),
        'construction_area': Decimal('520.00'),
    },
    {
        'title': 'Casa Colonial en San Ángel',
        'description': 'Hermosa casa estilo colonial mexicano con detalles arquitectónicos únicos. Jardín maduro, fuente central, techos altos y espacios llenos de historia. Perfecta para amantes de la arquitectura tradicional.',
        'bedrooms': 4,
        'bathrooms': 3,
        'parking_spaces': 2,
        'price': Decimal('9200000.00'),
        'lot_area': Decimal('380.00'),
        'construction_area': Decimal('320.00'),
    },
]

print("\nCreando 5 casas...")
for i, data in enumerate(casas_data, 1):
    colonia = random.choice(colonias_cdmx)
    casa = Property.objects.create(
        title=data['title'],
        description=data['description'],
        property_type='casa',
        operation_type=random.choice(['venta', 'venta_renta']),
        status='disponible',
        price=data['price'],
        currency='MXN',
        address=f"Calle {random.randint(1, 100)} #{random.randint(1, 500)}, {colonia}",
        city='Ciudad de México',
        state='Ciudad de México',
        zip_code=f"{random.randint(1000, 9999):04d}",
        country='México',
        google_maps_url=google_maps_url,
        bedrooms=data['bedrooms'],
        bathrooms=data['bathrooms'],
        half_bathrooms=random.randint(0, 1),
        parking_spaces=data['parking_spaces'],
        construction_area=data['construction_area'],
        lot_area=data['lot_area'],
        floors=random.randint(1, 2),
        year_built=random.randint(2010, 2023),
        rooms=data['bedrooms'] + 2,
        maintenance_fee=Decimal(random.randint(1000, 3000)),
        # Distribución
        has_sala=True,
        has_comedor=True,
        has_cocina=True,
        has_estudio=random.choice([True, False]),
        has_despensa=True,
        has_cuarto_tv=random.choice([True, False]),
        has_gimnasio=random.choice([True, False]),
        has_balcon=random.choice([True, False]),
        has_jardin=True,
        has_patio=random.choice([True, False]),
        has_roof_garden=random.choice([True, False]),
        has_area_lavado=True,
        has_bodega=random.choice([True, False]),
        # Amenidades
        amenity_salon=random.choice([True, False]),
        amenity_vigilancia=True,
        amenity_acceso=True,
        amenity_areas_verdes=random.choice([True, False]),
        amenity_juegos=random.choice([True, False]),
        amenity_gimnasio=random.choice([True, False]),
        amenity_alberca=random.choice([True, False]),
        amenity_pet_friendly=random.choice([True, False]),
        # Servicios
        service_agua=True,
        service_drenaje=True,
        service_luz=True,
        service_gas=True,
        service_internet=True,
        service_fibra=random.choice([True, False]),
        service_cable=random.choice([True, False]),
        service_cisterna=random.choice([True, False]),
        service_aire=random.choice([True, False]),
        service_boiler=True,
        is_featured=(i <= 2),
        is_new=(i <= 3),
        published_at=timezone.now(),
    )
    print(f"[OK] Casa {i} creada: {casa.title}")

# Crear 5 departamentos
depas_data = [
    {
        'title': 'Departamento Moderno en Roma Norte',
        'description': 'Departamento contemporáneo en el corazón de la Roma Norte. Acabados de lujo, balcón con vista, cocina equipada y excelente iluminación. A pasos de restaurantes, cafés y vida cultural.',
        'bedrooms': 2,
        'bathrooms': 2,
        'parking_spaces': 1,
        'price': Decimal('4200000.00'),
        'construction_area': Decimal('95.00'),
    },
    {
        'title': 'Penthouse en Condesa con Roof Garden',
        'description': 'Espectacular penthouse con roof garden privado y vista panorámica. Diseño arquitectónico único, espacios amplios y acabados premium. Incluye 2 cajones de estacionamiento y bodega.',
        'bedrooms': 3,
        'bathrooms': 3,
        'parking_spaces': 2,
        'price': Decimal('7800000.00'),
        'construction_area': Decimal('180.00'),
    },
    {
        'title': 'Departamento Familiar en Narvarte',
        'description': 'Amplio departamento ideal para familias. Tres recámaras con closet, sala-comedor espaciosa, cocina integral y balcón. Edificio con amenidades completas y excelente ubicación.',
        'bedrooms': 3,
        'bathrooms': 2,
        'parking_spaces': 1,
        'price': Decimal('3500000.00'),
        'construction_area': Decimal('110.00'),
    },
    {
        'title': 'Loft Minimalista en Polanco',
        'description': 'Loft de diseño minimalista con doble altura y ventanales amplios. Perfecto para profesionistas o parejas jóvenes. Ubicación premium con acceso a las mejores zonas de la ciudad.',
        'bedrooms': 1,
        'bathrooms': 1,
        'parking_spaces': 1,
        'price': Decimal('3800000.00'),
        'construction_area': Decimal('75.00'),
    },
    {
        'title': 'Departamento de Lujo en Santa Fe',
        'description': 'Departamento de lujo en torre corporativa de Santa Fe. Vista espectacular, acabados de primera, cocina italiana, domótica completa y amenidades de clase mundial. Seguridad 24/7.',
        'bedrooms': 3,
        'bathrooms': 3,
        'parking_spaces': 2,
        'price': Decimal('9500000.00'),
        'construction_area': Decimal('165.00'),
    },
]

print("\nCreando 5 departamentos...")
for i, data in enumerate(depas_data, 1):
    colonia = random.choice(colonias_cdmx)
    depa = Property.objects.create(
        title=data['title'],
        description=data['description'],
        property_type='departamento',
        operation_type=random.choice(['venta', 'renta', 'venta_renta']),
        status='disponible',
        price=data['price'],
        currency='MXN',
        address=f"Avenida {random.choice(['Insurgentes', 'Reforma', 'Universidad', 'Revolución'])} #{random.randint(100, 999)}, {colonia}",
        city='Ciudad de México',
        state='Ciudad de México',
        zip_code=f"{random.randint(1000, 9999):04d}",
        country='México',
        google_maps_url=google_maps_url,
        bedrooms=data['bedrooms'],
        bathrooms=data['bathrooms'],
        half_bathrooms=random.randint(0, 1),
        parking_spaces=data['parking_spaces'],
        construction_area=data['construction_area'],
        lot_area=None,
        floors=1,
        year_built=random.randint(2015, 2024),
        rooms=data['bedrooms'] + 1,
        maintenance_fee=Decimal(random.randint(2000, 5000)),
        # Distribución
        has_sala=True,
        has_comedor=True,
        has_cocina=True,
        has_estudio=random.choice([True, False]),
        has_despensa=random.choice([True, False]),
        has_cuarto_tv=random.choice([True, False]),
        has_balcon=random.choice([True, False]),
        has_roof_garden=(i == 2),
        has_area_lavado=True,
        has_bodega=random.choice([True, False]),
        # Amenidades
        amenity_salon=True,
        amenity_vigilancia=True,
        amenity_acceso=True,
        amenity_areas_verdes=random.choice([True, False]),
        amenity_juegos=random.choice([True, False]),
        amenity_gimnasio=True,
        amenity_alberca=random.choice([True, False]),
        amenity_pet_friendly=random.choice([True, False]),
        # Servicios
        service_agua=True,
        service_drenaje=True,
        service_luz=True,
        service_gas=random.choice([True, False]),
        service_internet=True,
        service_fibra=True,
        service_cable=random.choice([True, False]),
        service_cisterna=True,
        service_hidroneumatico=True,
        service_aire=random.choice([True, False]),
        service_boiler=True,
        is_featured=(i <= 2),
        is_new=(i <= 3),
        published_at=timezone.now(),
    )
    print(f"[OK] Departamento {i} creado: {depa.title}")

print(f"\n[EXITO] Base de datos poblada exitosamente!")
print(f"Total propiedades: {Property.objects.count()}")
print(f"Casas: {Property.objects.filter(property_type='casa').count()}")
print(f"Departamentos: {Property.objects.filter(property_type='departamento').count()}")
