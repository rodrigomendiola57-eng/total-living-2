from django.core.management.base import BaseCommand
from django.utils.text import slugify

from properties.models import InteriorFeature, Property, ServiceFeature


INTERIOR = [
    ('Sala', 'bi-house'), ('Comedor', 'bi-table'), ('Cocina Integral', 'bi-egg-fried'),
    ('Estudio', 'bi-journal-text'), ('Despensa', 'bi-box-seam'), ('Cuarto TV', 'bi-tv'),
    ('Gimnasio', 'bi-activity'), ('Balcón', 'bi-border-all'), ('Jardín', 'bi-flower3'),
    ('Patio', 'bi-grid'), ('Roof Garden', 'bi-building-up'), ('Área Lavado', 'bi-basket3'),
    ('Bodega', 'bi-box'),
]

SERVICES = [
    ('Agua', 'bi-droplet'), ('Drenaje', 'bi-diagram-3'), ('Luz', 'bi-lightbulb'),
    ('Gas Estacionario', 'bi-fire'), ('Internet', 'bi-wifi'), ('Fibra Óptica', 'bi-broadcast'),
    ('TV Cable', 'bi-tv'), ('Línea Telefónica', 'bi-telephone'), ('Cisterna', 'bi-droplet-fill'),
    ('Hidroneumático', 'bi-droplet-half'), ('Aire Acondicionado', 'bi-snow2'), ('Boiler', 'bi-thermometer-high'),
]

LEGACY_INTERIOR = {
    'has_sala': 'sala', 'has_comedor': 'comedor', 'has_cocina': 'cocina-integral',
    'has_estudio': 'estudio', 'has_despensa': 'despensa', 'has_cuarto_tv': 'cuarto-tv',
    'has_gimnasio': 'gimnasio', 'has_balcon': 'balcon', 'has_jardin': 'jardin',
    'has_patio': 'patio', 'has_roof_garden': 'roof-garden', 'has_area_lavado': 'area-lavado',
    'has_bodega': 'bodega',
}

LEGACY_SERVICES = {
    'service_agua': 'agua', 'service_drenaje': 'drenaje', 'service_luz': 'luz',
    'service_gas': 'gas-estacionario', 'service_internet': 'internet', 'service_fibra': 'fibra-optica',
    'service_cable': 'tv-cable', 'service_telefono': 'linea-telefonica', 'service_cisterna': 'cisterna',
    'service_hidroneumatico': 'hidroneumatico', 'service_aire': 'aire-acondicionado', 'service_boiler': 'boiler',
}


class Command(BaseCommand):
    help = 'Sincroniza catálogos normalizados de distribución/servicios y migra booleans legacy'

    def handle(self, *args, **options):
        for index, (name, icon) in enumerate(INTERIOR):
            InteriorFeature.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'icon': icon, 'sort_order': index, 'is_active': True},
            )

        for index, (name, icon) in enumerate(SERVICES):
            ServiceFeature.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'icon': icon, 'sort_order': index, 'is_active': True},
            )

        for prop in Property.objects.all():
            interior_ids = set(prop.interior_features.values_list('id', flat=True))
            for field_name, target_slug in LEGACY_INTERIOR.items():
                if getattr(prop, field_name, False):
                    feature = InteriorFeature.objects.filter(slug=target_slug, is_active=True).first()
                    if feature:
                        interior_ids.add(feature.id)
            prop.interior_features.set(InteriorFeature.objects.filter(id__in=interior_ids, is_active=True))

            service_ids = set(prop.service_features.values_list('id', flat=True))
            for field_name, target_slug in LEGACY_SERVICES.items():
                if getattr(prop, field_name, False):
                    feature = ServiceFeature.objects.filter(slug=target_slug, is_active=True).first()
                    if feature:
                        service_ids.add(feature.id)
            prop.service_features.set(ServiceFeature.objects.filter(id__in=service_ids, is_active=True))

        self.stdout.write(self.style.SUCCESS('Catálogos de distribución/servicios sincronizados y migrados desde legacy.'))
