from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from developments.models import Development
from properties.models import Amenity, AmenityAlias, Property


LEGACY_BOOLEAN_MAP = {
    'amenity_salon': 'lounge',
    'amenity_vigilancia': 'seguridad-24-7',
    'amenity_acceso': 'acceso-controlado',
    'amenity_areas_verdes': 'areas-verdes',
    'amenity_juegos': 'juegos-infantiles',
    'amenity_gimnasio': 'gimnasio',
    'amenity_alberca': 'alberca',
    'amenity_cancha_futbol': 'cancha-futbol',
    'amenity_cancha_tenis': 'cancha-tenis',
    'amenity_cancha_basket': 'cancha-basketball',
    'amenity_asadores': 'asadores',
    'amenity_pet_friendly': 'pet-friendly',
}


def resolve_amenity(raw_name: str):
    if not raw_name:
        return None
    raw = raw_name.strip()
    slug = slugify(raw)
    amenity = Amenity.objects.filter(slug=slug, is_active=True).first()
    if amenity:
        return amenity
    alias = AmenityAlias.objects.filter(alias_slug=slug).select_related('amenity').first()
    if alias:
        return alias.amenity
    return Amenity.objects.filter(display_name__iexact=raw, is_active=True).first()


class Command(BaseCommand):
    help = 'Migra amenidades legacy (booleans y texto) al catálogo normalizado'

    @transaction.atomic
    def handle(self, *args, **options):
        linked_properties = 0
        linked_developments = 0

        for prop in Property.objects.all():
            selected = set(prop.amenities.values_list('id', flat=True))
            for field_name, target_slug in LEGACY_BOOLEAN_MAP.items():
                if getattr(prop, field_name, False):
                    amenity = Amenity.objects.filter(slug=target_slug).first()
                    if amenity:
                        selected.add(amenity.id)
            if selected:
                prop.amenities.set(Amenity.objects.filter(id__in=selected, is_active=True))
                linked_properties += 1

        for dev in Development.objects.all():
            selected = set(dev.amenities.values_list('id', flat=True))
            for line in dev.get_amenity_lines():
                amenity = resolve_amenity(line)
                if amenity:
                    selected.add(amenity.id)
            if selected:
                dev.amenities.set(Amenity.objects.filter(id__in=selected, is_active=True))
                linked_developments += 1

        self.stdout.write(self.style.SUCCESS(
            f'Migración legacy completa. Propiedades actualizadas: {linked_properties}, desarrollos actualizados: {linked_developments}.'
        ))
