from django.conf import settings


def map_tiles(request):
    """Expose map tile provider config to templates."""
    return {
        'MAP_TILES': {
            'url': getattr(settings, 'MAP_TILE_URL', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
            'attribution': getattr(settings, 'MAP_TILE_ATTRIBUTION', '&copy; OpenStreetMap contributors'),
            'subdomains': getattr(settings, 'MAP_TILE_SUBDOMAINS', 'abc'),
            'max_zoom': getattr(settings, 'MAP_TILE_MAX_ZOOM', 19),
        }
    }


def public_site(request):
    """Base HTTPS del sitio para enlaces canónicos (compartir, etc.)."""
    return {'PUBLIC_SITE_URL': getattr(settings, 'PUBLIC_SITE_URL', '')}


def property_catalog(request):
    """
    Catálogo global de tipos/operaciones para mantener consistencia
    entre panel, filtros públicos y formularios.
    """
    from properties.models import PropertyOperation, PropertyType

    return {
        'property_types_catalog': PropertyType.choices,
        'property_operations_catalog': PropertyOperation.choices,
    }
