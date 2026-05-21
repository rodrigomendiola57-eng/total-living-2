"""
Carga datos de prueba: 5 propiedades en venta, 5 en renta, 5 desarrollos.
Sin imágenes (puedes subirlas después en admin/panel).

IMPORTANTE (Docker): la web usa PostgreSQL DENTRO del contenedor. Si ejecutaste este comando
solo en Windows con `python manage.py`, llenaste otra base (p. ej. SQLite), no la de Docker.
Solución: `docker compose exec web python manage.py seed_demo_catalog` o deja que docker-compose
ejecute el seed al arrancar (ver docker-compose.yml).

Uso:
  python manage.py seed_demo_catalog
  python manage.py seed_demo_catalog --clear   # borra solo filas con slugs catalogo-demo-*
"""

from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.core.management.base import BaseCommand
from django.utils import timezone

from properties.models import Property, PropertyOperation, PropertyProcess, PropertyStatus, PropertyType
from regions.models import Region


def _tiny_placeholder_image(name: str):
    """PNG pequeño en memoria (región requiere ImageField)."""
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError('Pillow es necesario para generar la imagen de región demo.') from None
    buf = BytesIO()
    Image.new('RGB', (120, 80), color=(230, 232, 235)).save(buf, format='PNG')
    buf.seek(0)
    from django.core.files.base import ContentFile

    return ContentFile(buf.read(), name=name)


class Command(BaseCommand):
    help = 'Inserta 5 propiedades en venta, 5 en renta y 5 desarrollos (datos de prueba, sin fotos).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina propiedades y desarrollos creados por este comando (slugs catalogo-demo-*).',
        )

    def handle(self, *args, **options):
        from developments.models import Development

        if options['clear']:
            n_p = Property.objects.filter(slug__startswith='catalogo-demo-').delete()[0]
            n_d = Development.objects.filter(slug__startswith='catalogo-demo-desarrollo-').delete()[0]
            self.stdout.write(self.style.WARNING(f'Eliminadas {n_p} propiedades y {n_d} desarrollos demo.'))
            return

        region, _ = Region.objects.get_or_create(
            slug='queretaro-demo',
            defaults={
                'name': 'Querétaro (demo)',
                'description': 'Región de ejemplo para pruebas del catálogo.',
                'highlights': 'Centro histórico, Zona industrial, Corredor Bernardo Quintana',
                'growth_level': 'alto',
                'order': 0,
                'is_active': True,
            },
        )
        if not region.image:
            region.image.save('region-demo.png', _tiny_placeholder_image('region-demo.png'), save=True)

        now = timezone.now()
        base_kw = {
            'description': 'Propiedad de demostración para pruebas. Puedes editar texto e imágenes en el panel.',
            'property_type': PropertyType.CASA,
            'status': PropertyStatus.DISPONIBLE,
            'process': PropertyProcess.NO_APLICA,
            'currency': 'MXN',
            'city': 'Querétaro',
            'state': 'Querétaro',
            'zip_code': '76000',
            'country': 'México',
            'region': region,
            'google_maps_url': 'https://maps.app.goo.gl/example',
            'bedrooms': 3,
            'bathrooms': 2,
            'half_bathrooms': 1,
            'parking_spaces': 2,
            'area': Decimal('185.00'),
            'construction_area': Decimal('165.00'),
            'lot_area': Decimal('200.00'),
            'floors': 2,
            'year_built': 2021,
            'rooms': 5,
            'has_sala': True,
            'has_comedor': True,
            'has_cocina': True,
            'published_at': now,
        }

        ventas = [
            ('catalogo-demo-venta-1', 'Casa en venta · Juriquilla', 'Av. Paseo Juriquilla 101', Decimal('4850000.00')),
            ('catalogo-demo-venta-2', 'Departamento en venta · El Refugio', 'Calle Refugio 220', Decimal('3250000.00')),
            ('catalogo-demo-venta-3', 'Casa en venta · Zibatá', 'Boulevard Zibatá 45', Decimal('6200000.00')),
            ('catalogo-demo-venta-4', 'Casa en venta · Centro sur', 'Calle Pasteur 88', Decimal('2890000.00')),
            ('catalogo-demo-venta-5', 'Terreno en venta · Huimilpan', 'Carretera a Huimilpan km 12', Decimal('1950000.00')),
        ]

        rentas = [
            ('catalogo-demo-renta-1', 'Departamento en renta · Milenio III', 'Av. Milenio 300', Decimal('14500.00')),
            ('catalogo-demo-renta-2', 'Casa en renta · Alamos', 'Calle Alamos 14', Decimal('22000.00')),
            ('catalogo-demo-renta-3', 'Departamento en renta · Centro', 'And. 5 de Mayo 50', Decimal('9800.00')),
            ('catalogo-demo-renta-4', 'Oficina en renta · Centro sur', 'Av. Universidad 402', Decimal('18500.00')),
            ('catalogo-demo-renta-5', 'Departamento en renta · El Campanario', 'P.º del Campanario 9', Decimal('17500.00')),
        ]

        for i, (slug, title, address, price) in enumerate(ventas, start=1):
            pt = PropertyType.TERRENO if 'Terreno' in title else (
                PropertyType.DEPARTAMENTO if 'Departamento' in title else PropertyType.CASA
            )
            terreno_kw = {}
            if pt == PropertyType.TERRENO:
                terreno_kw = {
                    'bedrooms': 0,
                    'bathrooms': 0,
                    'half_bathrooms': 0,
                    'parking_spaces': 0,
                    'rooms': 0,
                    'construction_area': None,
                }
            obj, created = Property.objects.update_or_create(
                slug=slug,
                defaults={
                    **base_kw,
                    **terreno_kw,
                    'title': title,
                    'address': address,
                    'price': price,
                    'operation_type': PropertyOperation.VENTA,
                    'property_type': pt,
                    'is_featured': i <= 3,
                    'latitude': Decimal('20.5881') + Decimal(str(i * 2)) / Decimal('10000'),
                    'longitude': Decimal('-100.3881') + Decimal(str(i * 2)) / Decimal('10000'),
                },
            )
            self.stdout.write(f"{'+' if created else '~'} Propiedad venta: {obj.title}")

        for i, (slug, title, address, price) in enumerate(rentas, start=1):
            pt = PropertyType.OFICINA if 'Oficina' in title else (
                PropertyType.DEPARTAMENTO if 'Departamento' in title else PropertyType.CASA
            )
            obj, created = Property.objects.update_or_create(
                slug=slug,
                defaults={
                    **base_kw,
                    'title': title,
                    'address': address,
                    'price': price,
                    'operation_type': PropertyOperation.RENTA,
                    'property_type': pt,
                    'is_featured': i == 1,
                    'latitude': Decimal('20.5920') + Decimal(str(i * 2)) / Decimal('10000'),
                    'longitude': Decimal('-100.3820') + Decimal(str(i * 2)) / Decimal('10000'),
                },
            )
            self.stdout.write(f"{'+' if created else '~'} Propiedad renta: {obj.title}")

        desarrollos = [
            (
                'catalogo-demo-desarrollo-1',
                'Torre Alameda Living',
                'Vertical de departamentos cerca de servicios y avenidas principales.',
                'preventa',
                'depto',
                'venta',
                Decimal('3200000.00'),
                18,
                42,
            ),
            (
                'catalogo-demo-desarrollo-2',
                'Residencial Los Encinos',
                'Casas en privada con áreas comunes y acceso controlado.',
                'construccion',
                'casa',
                'venta',
                Decimal('4100000.00'),
                2,
                24,
            ),
            (
                'catalogo-demo-desarrollo-3',
                'Vitta Park Querétaro',
                'Desarrollo mixto con amenidades y espacios verdes.',
                'entrega_inmediata',
                'mixto',
                'venta_renta',
                Decimal('2850000.00'),
                8,
                15,
            ),
            (
                'catalogo-demo-desarrollo-4',
                'Lotes Valle Dorado',
                'Terrenos habitacionales con servicios subterráneos.',
                'preventa',
                'terreno',
                'venta',
                Decimal('890000.00'),
                1,
                32,
            ),
            (
                'catalogo-demo-desarrollo-5',
                'Renta Corporativa BQ',
                'Torre de suites y departamentos en renta corporativa.',
                'entrega_inmediata',
                'depto',
                'renta',
                Decimal('18500.00'),
                12,
                30,
            ),
        ]

        delivery = date.today() + timedelta(days=180)
        for i, row in enumerate(desarrollos):
            slug, name, desc, estatus, producto, op, price_from, levels, units = row
            obj, created = Development.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': desc,
                    'subtitle': 'Proyecto de demostración · Querétaro',
                    'developer_name': 'Promotora Demo S.A. de C.V.',
                    'amenities_text': 'Alberca\nGimnasio\nSalón de eventos\nCowork',
                    'location': f'Zona demo {i + 1} · Querétaro',
                    'city': 'Querétaro',
                    'state': 'Querétaro',
                    'operation_type': op,
                    'product_type': producto,
                    'construction_status': estatus,
                    'levels': levels,
                    'total_units': units,
                    'available_units': max(1, units // 2),
                    'parking_spaces': 1 + (i % 3),
                    'total_m2': 1200 + i * 400,
                    'price_from': price_from,
                    'delivery_date': delivery,
                    'is_active': True,
                    'is_featured': i < 2,
                },
            )
            self.stdout.write(f"{'+' if created else '~'} Desarrollo: {obj.name}")

        self.stdout.write(self.style.SUCCESS('Listo. Sin fotos: súbelas desde el admin o el panel.'))
