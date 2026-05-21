"""
Metadatos Open Graph / Twitter Card para fichas de propiedad (WhatsApp, Facebook, etc.).
"""
import re

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


def absolute_media_uri(path_or_url, request=None):
    """Convierte ruta relativa (/media/...) o URL relativa en URL absoluta https."""
    if not path_or_url:
        return ''
    raw = str(path_or_url).strip()
    if raw.startswith(('http://', 'https://')):
        return raw
    if not raw.startswith('/'):
        raw = '/' + raw
    base = getattr(settings, 'PUBLIC_SITE_URL', '').strip().rstrip('/')
    if base:
        return base + raw
    if request is not None:
        return request.build_absolute_uri(raw)
    return raw


def _plain_description(property_obj, max_len=200):
    text = re.sub(r'\s+', ' ', (property_obj.description or '').strip())
    if not text:
        location = property_obj.get_location_line_display()
        text = property_obj.title
        if location:
            text = f'{property_obj.title} — {location}'
    if len(text) > max_len:
        return text[: max_len - 3].rstrip() + '...'
    return text


def build_property_open_graph(property_obj, request):
    """
    Diccionario de metadatos para plantillas (Django autoescapa en HTML).
    """
    page_url = absolute_media_uri(property_obj.get_absolute_url(), request)
    main = property_obj.get_main_image()
    image_url = ''
    if main and main.image:
        image_url = absolute_media_uri(main.image.url, request)
    if not image_url:
        try:
            logo_path = staticfiles_storage.url('images/logo.png')
        except Exception:
            logo_path = '/static/images/logo.png'
        image_url = absolute_media_uri(logo_path, request)

    title = (property_obj.title or 'Propiedad').strip()
    description = _plain_description(property_obj)
    price = property_obj.get_price_display()
    site_name = 'Total Living'

    return {
        'title': title,
        'description': description,
        'url': page_url,
        'image': image_url,
        'site_name': site_name,
        'type': 'website',
        'price_display': price,
    }
