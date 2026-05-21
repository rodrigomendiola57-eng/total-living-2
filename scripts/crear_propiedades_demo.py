"""
Script para crear propiedades de demostración
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from properties.models import Property
from decimal import Decimal

def crear_propiedades_demo():
    """Crear propiedades de demostración"""
    
    propiedades = [
        {
            'title': 'Casa Moderna en Zona Residencial',
            'description': 'Hermosa casa moderna con acabados de lujo, amplio jardín y excelente ubicación en zona residencial premium.',
            'property_type': 'casa',
            'operation_type': 'venta',
            'price': Decimal('3500000.00'),
            'address': 'Av. Principal 123',
            'city': 'Monterrey',
            'state': 'Nuevo León',
            'bedrooms': 4,
            'bathrooms': 3,
            'parking_spaces': 2,
            'construction_area': Decimal('250.00'),
            'is_featured': True,
        },
        {
            'title': 'Departamento Céntrico Amueblado',
            'description': 'Departamento completamente amueblado en el corazón de la ciudad, cerca de todo.',
            'property_type': 'departamento',
            'operation_type': 'renta',
            'price': Decimal('15000.00'),
            'address': 'Calle Centro 456',
            'city': 'Guadalajara',
            'state': 'Jalisco',
            'bedrooms': 2,
            'bathrooms': 2,
            'parking_spaces': 1,
            'construction_area': Decimal('85.00'),
            'is_new': True,
        },
        {
            'title': 'Terreno Comercial en Avenida Principal',
            'description': 'Excelente terreno comercial con alta plusvalía, ideal para desarrollo.',
            'property_type': 'terreno',
            'operation_type': 'venta',
            'price': Decimal('2800000.00'),
            'address': 'Av. Comercial 789',
            'city': 'Ciudad de México',
            'state': 'CDMX',
            'bedrooms': 0,
            'bathrooms': 0,
            'parking_spaces': 0,
            'construction_area': Decimal('500.00'),
        },
        {
            'title': 'Local Comercial en Plaza',
            'description': 'Local comercial en plaza de alto tráfico, excelente para negocio.',
            'property_type': 'local',
            'operation_type': 'renta',
            'price': Decimal('25000.00'),
            'address': 'Plaza Comercial 321',
            'city': 'Monterrey',
            'state': 'Nuevo León',
            'bedrooms': 0,
            'bathrooms': 2,
            'parking_spaces': 3,
            'construction_area': Decimal('120.00'),
        },
        {
            'title': 'Casa de Playa con Vista al Mar',
            'description': 'Increíble casa frente al mar, perfecta para vacaciones o inversión.',
            'property_type': 'casa',
            'operation_type': 'venta',
            'price': Decimal('5500000.00'),
            'address': 'Costera Miguel Alemán 555',
            'city': 'Acapulco',
            'state': 'Guerrero',
            'bedrooms': 5,
            'bathrooms': 4,
            'parking_spaces': 3,
            'construction_area': Decimal('350.00'),
            'is_featured': True,
        },
        {
            'title': 'Oficina Ejecutiva Torre Corporativa',
            'description': 'Oficina moderna en torre corporativa AAA, lista para usar.',
            'property_type': 'oficina',
            'operation_type': 'renta',
            'price': Decimal('35000.00'),
            'address': 'Torre Corporativa 100',
            'city': 'Ciudad de México',
            'state': 'CDMX',
            'bedrooms': 0,
            'bathrooms': 2,
            'parking_spaces': 2,
            'construction_area': Decimal('150.00'),
        },
    ]
    
    print("Creando propiedades de demostración...")
    print("=" * 50)
    
    for prop_data in propiedades:
        property_obj, created = Property.objects.get_or_create(
            title=prop_data['title'],
            defaults=prop_data
        )
        
        if created:
            print(f"[+] Creada: {property_obj.title}")
        else:
            print(f"[*] Ya existe: {property_obj.title}")
    
    print("=" * 50)
    total = Property.objects.count()
    print(f"\nTotal de propiedades en la base de datos: {total}")
    print("\nListo! Ahora puedes ver tu frontend en http://127.0.0.1:8080/")

if __name__ == '__main__':
    crear_propiedades_demo()
