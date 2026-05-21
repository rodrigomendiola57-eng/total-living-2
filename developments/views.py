import logging
from urllib.parse import quote_plus, urlencode
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.db.models import Case, IntegerField, Prefetch, Q, When
from django.db.utils import OperationalError, ProgrammingError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from contact.models import Contact
from contact.spam_protection import is_honeypot_triggered, ratelimit_contact
from properties.money import parse_coordinate, parse_mx_money
from properties.models import Amenity, AmenityCategory

from .db_compat import floorplan_table_ready
from .models import (
    Development,
    DevelopmentImage,
    DevelopmentUnitModel,
    DevelopmentUnitModelFloorPlan,
    DevelopmentUnitModelImage,
    DevelopmentsPageConfig,
)

logger = logging.getLogger(__name__)

# Campos añadidos en migración 0012: si la BD no está migrada, defer evita SELECT inexistente.
_UNIT_MODEL_OPTIONAL_TEXT_FIELDS = ('description', 'other_features_text')


def _get_unit_model_for_panel_edit(pk):
    """
    Carga modelo para edición en panel.
    Prueba variantes (con/sin prefetch de plantas, con/sin defer) ante esquemas viejos.
    """
    fp_p = None
    if floorplan_table_ready():
        fp_p = Prefetch(
            'floor_plans',
            queryset=DevelopmentUnitModelFloorPlan.objects.order_by('order', 'id'),
        )
    d_full = DevelopmentUnitModel.objects.select_related('development')
    d_def = d_full.defer(*_UNIT_MODEL_OPTIONAL_TEXT_FIELDS)
    candidates = []
    if fp_p is not None:
        candidates.append(d_full.prefetch_related(fp_p))
    candidates.append(d_full)
    if fp_p is not None:
        candidates.append(d_def.prefetch_related(fp_p))
    candidates.append(d_def)

    last_err = None
    for qs in candidates:
        try:
            return get_object_or_404(qs, pk=pk)
        except (ProgrammingError, OperationalError) as e:
            last_err = e
            continue
    if last_err is not None:
        raise last_err
    raise Http404()


def _quiz_whatsapp_me_base_url():
    raw = (getattr(settings, 'WHATSAPP_LEAD_NUMBER', '') or '').strip()
    digits = ''.join(c for c in raw if c.isdigit())
    if len(digits) < 10:
        return ''
    if not digits.startswith('52'):
        digits = '52' + digits.lstrip('0')
    return f'https://wa.me/{digits}'


def _developments_lead_contact_url(tipo: str) -> str:
    """URL de contacto con mensaje prearmado según tipo de producto (captación rápida)."""
    if tipo == 'casa':
        msg = 'Me interesan desarrollos de casas o residenciales en Querétaro.'
    elif tipo == 'depto':
        msg = 'Me interesan departamentos o desarrollos verticales en Querétaro.'
    elif tipo == 'terreno':
        msg = 'Me interesan terrenos o lotes en desarrollo en Querétaro.'
    elif tipo == 'mixto':
        msg = 'Me interesan desarrollos mixtos en Querétaro.'
    else:
        msg = 'Me interesa recibir información sobre desarrollos en Querétaro.'
    q = urlencode({'subject': 'Desarrollos Querétaro', 'message': msg})
    return f"{reverse('contact:contact')}?{q}"


def _parse_price_from_post(raw_value):
    """
    Normaliza precio desde panel (miles con coma o punto: 2.170.000, 2,170,000, etc.).
    """
    cleaned = (raw_value or '').strip()
    if not cleaned:
        return Decimal('0')
    value = parse_mx_money(cleaned)
    if value is None:
        raise ValueError('El precio desde no tiene un formato válido.')
    max_allowed = Decimal('9999999999.99')
    if abs(value) > max_allowed:
        raise ValueError('El precio desde es demasiado grande (máximo 9,999,999,999.99).')
    return value


def developments_list(request):
    """Vista pública para mostrar todos los desarrollos"""
    operation = request.GET.get('operation', 'all')
    tipo = (request.GET.get('tipo') or 'all').strip() or 'all'
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    search = request.GET.get('search', '')

    developments = Development.objects.filter(is_active=True).prefetch_related('images').order_by('-is_featured', '-created_at')

    if operation == 'venta':
        developments = developments.filter(operation_type__in=['venta', 'venta_renta'])
    elif operation == 'renta':
        developments = developments.filter(operation_type__in=['renta', 'venta_renta'])

    if tipo and tipo != 'all':
        developments = developments.filter(product_type=tipo)

    if city:
        developments = developments.filter(city__icontains=city)
    if precio_min:
        try:
            developments = developments.filter(price_from__gte=float(precio_min))
        except (ValueError, TypeError):
            pass
    if precio_max:
        try:
            developments = developments.filter(price_from__lte=float(precio_max))
        except (ValueError, TypeError):
            pass
    if search:
        developments = developments.filter(name__icontains=search)

    dev_list = list(developments)

    base_filter_q = {}
    if city:
        base_filter_q['ciudad'] = city
    if precio_min:
        base_filter_q['precio_min'] = precio_min
    if precio_max:
        base_filter_q['precio_max'] = precio_max
    if search:
        base_filter_q['search'] = search

    type_urls = {}
    for key in ('all', 'casa', 'depto', 'mixto', 'terreno'):
        q = {**base_filter_q}
        if key != 'all':
            q['tipo'] = key
        if operation != 'all':
            q['operation'] = operation
        type_urls[key] = f"{reverse('developments:list')}?{urlencode(q)}" if q else reverse('developments:list')

    operation_urls = {}
    for op in ('all', 'venta', 'renta'):
        q = {**base_filter_q}
        if tipo != 'all':
            q['tipo'] = tipo
        if op != 'all':
            q['operation'] = op
        operation_urls[op] = f"{reverse('developments:list')}?{urlencode(q)}" if q else reverse('developments:list')

    try:
        page_config = DevelopmentsPageConfig.load()
    except ProgrammingError:
        page_config = DevelopmentsPageConfig()

    context = {
        'developments': dev_list,
        'title': 'Desarrollos Exclusivos',
        'operation': operation,
        'tipo': tipo,
        'dev_count': len(dev_list),
        'featured_count': sum(1 for d in dev_list if d.is_featured),
        'current_filters': {
            'ciudad': city,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'search': search,
        },
        'type_urls': type_urls,
        'operation_urls': operation_urls,
        'lead_contact_url': _developments_lead_contact_url(tipo if tipo != 'all' else ''),
        'developments_page_config': page_config,
        'quiz_wa_base_url': _quiz_whatsapp_me_base_url(),
    }

    return render(request, 'developments/list.html', context)


QUIZ_AMBIENTE = {
    'urbano': 'Urbano / vibrante',
    'verde': 'Verde / relajado',
    'privado': 'Privado / residencial',
}
QUIZ_ESPACIO = {
    'pareja': 'Solo yo / pareja',
    'familia': 'Familia',
    'homeoffice': 'Home office ready',
}
QUIZ_TIEMPO = {
    'pronto': 'Lo antes posible',
    'plan': 'En 12–18 meses (planificación)',
}
QUIZ_MUST = {
    'rooftop': 'Rooftop privado',
    'pool': 'Alberca de autor',
    'concierge': 'Concierge 24/7',
    'pet': 'Pet friendly',
    'ev': 'Carga eléctrica',
}


@require_POST
@ratelimit_contact
def developments_quiz_lead(request):
    """Recibe el Smart Quiz de desarrollos y crea un Contact (JSON)."""
    if getattr(request, 'contact_rate_limited', False):
        return JsonResponse(
            {'ok': False, 'error': 'rate'},
            status=429,
        )

    if is_honeypot_triggered(request):
        return JsonResponse({'ok': True})

    name = (request.POST.get('name') or '').strip()
    whatsapp = (request.POST.get('whatsapp') or '').strip()
    ambiente = (request.POST.get('ambiente') or '').strip()
    espacio = (request.POST.get('espacio') or '').strip()
    tiempo = (request.POST.get('tiempo') or '').strip()
    raw_must = request.POST.getlist('must_have')

    wa_digits = ''.join(c for c in whatsapp if c.isdigit())
    if len(name) < 2:
        return JsonResponse({'ok': False, 'error': 'name'}, status=400)
    if len(wa_digits) < 10:
        return JsonResponse({'ok': False, 'error': 'whatsapp'}, status=400)
    if ambiente not in QUIZ_AMBIENTE:
        return JsonResponse({'ok': False, 'error': 'ambiente'}, status=400)
    if espacio not in QUIZ_ESPACIO:
        return JsonResponse({'ok': False, 'error': 'espacio'}, status=400)
    if tiempo not in QUIZ_TIEMPO:
        return JsonResponse({'ok': False, 'error': 'tiempo'}, status=400)

    must_clean = []
    for key in raw_must:
        k = (key or '').strip()
        if k in QUIZ_MUST and k not in must_clean:
            must_clean.append(k)
    if not must_clean or len(must_clean) > 3:
        return JsonResponse({'ok': False, 'error': 'must_have'}, status=400)

    must_labels = ', '.join(QUIZ_MUST[k] for k in must_clean)
    body = (
        f'[Quiz desarrollos — portafolio curado]\n\n'
        f'Nombre: {name}\n'
        f'WhatsApp: {whatsapp}\n\n'
        f'Ambiente: {QUIZ_AMBIENTE[ambiente]}\n'
        f'Imprescindibles: {must_labels}\n'
        f'Espacio: {QUIZ_ESPACIO[espacio]}\n'
        f'Tiempo: {QUIZ_TIEMPO[tiempo]}\n'
    )

    placeholder_email = getattr(
        settings,
        'QUIZ_LEAD_PLACEHOLDER_EMAIL',
        'quiz-desarrollos@totalliving.com',
    )

    try:
        Contact.objects.create(
            name=name[:100],
            email=placeholder_email[:255],
            phone=whatsapp[:20],
            subject='Quiz desarrollos · portafolio curado',
            message=body,
            property=None,
            status=Contact.STATUS_NEW,
            source='quiz_desarrollos',
        )
    except (OperationalError, ProgrammingError):
        logger.exception('Fallo de base de datos al guardar lead de quiz de desarrollos')
        return JsonResponse({'ok': False, 'error': 'server'}, status=500)

    wa_msg = (
        f'Hola, soy {name}. Completé el quiz de desarrollos en Total Living '
        f'y quiero recibir mi portafolio curado. Gracias.'
    )
    wa_href = ''
    base = _quiz_whatsapp_me_base_url()
    if base:
        wa_href = f'{base}?text={quote_plus(wa_msg)}'

    return JsonResponse({'ok': True, 'whatsapp_url': wa_href})

def redirect_legacy_development_detail(request, pk):
    development = get_object_or_404(Development, pk=pk)
    return redirect('developments:detail', development_slug=development.slug)


def redirect_legacy_unit_model(request, pk, model_slug):
    development = get_object_or_404(Development, pk=pk)
    return redirect(
        'developments:unit_model_detail',
        development_slug=development.slug,
        model_slug=model_slug,
    )


def development_detail(request, development_slug):
    """Vista pública para mostrar el detalle de un desarrollo (URL por slug)."""
    base_qs = Development.objects.filter(is_active=True)
    unit_models_qs = (
        DevelopmentUnitModel.objects.filter(is_active=True)
        .defer(*_UNIT_MODEL_OPTIONAL_TEXT_FIELDS)
        .order_by('order', 'id')
    )
    try:
        development = get_object_or_404(
            base_qs.prefetch_related(Prefetch('unit_models', queryset=unit_models_qs)),
            slug=development_slug,
        )
        unit_models = list(development.unit_models.all())
    except ProgrammingError:
        development = get_object_or_404(base_qs, slug=development_slug)
        unit_models = []

    gallery_images = (
        development.images.exclude(category=DevelopmentImage.Category.PLANS)
        .order_by('-is_main', 'order', 'id')
    )
    plan_images = development.images.filter(category=DevelopmentImage.Category.PLANS).order_by(
        'order', 'id'
    )

    related_developments = Development.objects.filter(
        is_active=True,
    ).filter(
        Q(city=development.city) | Q(state=development.state)
    ).exclude(pk=development.pk).prefetch_related('images')[:4]

    try:
        page_config = DevelopmentsPageConfig.load()
    except ProgrammingError:
        page_config = DevelopmentsPageConfig()

    context = {
        'development': development,
        'images': gallery_images,
        'gallery_images': gallery_images,
        'plan_images': plan_images,
        'related_developments': related_developments,
        'unit_models': unit_models,
        'page_config': page_config,
    }

    return render(request, 'developments/detail.html', context)


def development_unit_detail(request, development_slug, model_slug):
    """Ficha del modelo (tipología); URL canónica por slugs de desarrollo y modelo."""
    development = get_object_or_404(Development, slug=development_slug, is_active=True)
    gallery_p = Prefetch(
        'gallery_images',
        queryset=DevelopmentUnitModelImage.objects.order_by('order', 'id'),
    )
    fp_p = None
    if floorplan_table_ready():
        fp_p = Prefetch(
            'floor_plans',
            queryset=DevelopmentUnitModelFloorPlan.objects.order_by('order', 'id'),
        )
    base = DevelopmentUnitModel.objects.filter(development=development, is_active=True)
    base_def = base.defer(*_UNIT_MODEL_OPTIONAL_TEXT_FIELDS)
    candidates = []
    if fp_p is not None:
        candidates.append(base.prefetch_related(gallery_p, fp_p))
    candidates.append(base.prefetch_related(gallery_p))
    if fp_p is not None:
        candidates.append(base_def.prefetch_related(gallery_p, fp_p))
    candidates.append(base_def.prefetch_related(gallery_p))

    unit_model = None
    last_err = None
    for qs in candidates:
        try:
            unit_model = get_object_or_404(qs, slug=model_slug)
            break
        except (ProgrammingError, OperationalError) as e:
            last_err = e
            continue
    if unit_model is None:
        raise Http404() from last_err

    um_description, um_other_lines = _safe_unit_model_text_for_template(unit_model)

    carousel_images = _build_unit_model_carousel(unit_model)

    try:
        display_price_from = unit_model.display_price_from()
    except (AttributeError, ValueError, TypeError, ArithmeticError):
        display_price_from = None

    try:
        page_config = DevelopmentsPageConfig.load()
    except ProgrammingError:
        page_config = DevelopmentsPageConfig()
    safe_plans = _safe_floor_plans_for_template(unit_model)
    return render(
        request,
        'developments/unit_model_detail.html',
        {
            'development': development,
            'unit_model': unit_model,
            'page_config': page_config,
            'carousel_images': carousel_images,
            'floor_plans': safe_plans,
            'floor_plans_ui': _floor_plans_ui_for_detail(safe_plans),
            'um_description': um_description,
            'um_other_lines': um_other_lines,
            'display_price_from': display_price_from,
            'unit_model_contact_url': _unit_model_contact_url(development, unit_model),
        },
    )


def _safe_unit_model_text_for_template(unit_model):
    """
    Lee descripción y viñetas sin romper el render si el esquema es viejo
    o los campos están defer() y la columna no existe.
    """
    description = ''
    other_lines = []
    try:
        description = (unit_model.description or '').strip()
    except (ProgrammingError, OperationalError, AttributeError):
        description = ''
    try:
        other_lines = unit_model.get_other_feature_lines()
    except (ProgrammingError, OperationalError, AttributeError):
        other_lines = []
    return description, other_lines


def _safe_floor_plans_for_template(unit_model):
    """Lista de dicts con URL segura (evita 500 si falta archivo en storage)."""
    if not floorplan_table_ready():
        return []
    try:
        rows = list(unit_model.floor_plans.all())
    except (ProgrammingError, OperationalError):
        return []
    out = []
    for fp in rows:
        try:
            out.append({'pk': fp.pk, 'label': fp.label, 'url': fp.image.url})
        except (ValueError, OSError, AttributeError):
            continue
    return out


def _floor_plan_default_letter(index_zero_based: int) -> str:
    """A, B, … Z, luego 27, 28 (por si hay muchas plantas)."""
    if 0 <= index_zero_based < 26:
        return chr(ord('A') + index_zero_based)
    return str(index_zero_based + 1)


def _unit_model_contact_url(development: Development, unit_model: DevelopmentUnitModel) -> str:
    """URL de contacto con asunto y mensaje prellenados para este modelo."""
    q = urlencode(
        {
            'subject': f'Modelo {unit_model.name} · {development.name}',
            'message': (
                f'Hola, quisiera información sobre el modelo «{unit_model.name}» '
                f'del desarrollo «{development.name}».'
            ),
        }
    )
    return f'{reverse("contact:contact")}?{q}'


def _floor_plans_ui_for_detail(safe_rows: list) -> dict | None:
    """
    UI de plantas en ficha de modelo:
    - Una sola imagen: sin pestañas, encabezado «Planta A».
    - Dos o más: solo pestañas Planta A / Planta B (sin título genérico duplicado).
    """
    if not safe_rows:
        return None
    if len(safe_rows) == 1:
        r0 = safe_rows[0]
        return {'mode': 'single', 'url': r0['url'], 'pk': r0['pk']}
    tabs = []
    for i, r in enumerate(safe_rows):
        if i == 0:
            tab_label = 'Planta A'
        elif i == 1:
            tab_label = 'Planta B'
        else:
            tab_label = (r.get('label') or '').strip() or f'Planta {chr(ord("C") + i - 2)}'
        tabs.append({'tab_label': tab_label, 'url': r['url'], 'pk': r['pk']})
    return {'mode': 'tabs', 'tabs': tabs}


def _floor_plan_items_for_panel(unit_model):
    """Miniaturas de plantas para el formulario del panel (sin tocar .floor_plans en plantilla)."""
    if not unit_model or not unit_model.pk:
        return []
    if not floorplan_table_ready():
        return []
    try:
        rows = list(
            DevelopmentUnitModelFloorPlan.objects.filter(unit_model=unit_model).order_by(
                'order', 'id'
            )
        )
    except (ProgrammingError, OperationalError):
        return []
    out = []
    for fp in rows:
        try:
            out.append({'pk': fp.pk, 'label': fp.label, 'thumb_url': fp.image.url})
        except (ValueError, OSError, AttributeError):
            continue
    return out


def _build_unit_model_carousel(unit_model):
    """
    Carrusel público: primero imagen de tarjeta (si existe), luego galería sin duplicar URL.
    """
    carousel_images = []
    seen_urls = set()
    if unit_model.card_image:
        try:
            u = unit_model.card_image.url
            carousel_images.append(
                {
                    'url': u,
                    'alt': f'{unit_model.name} — imagen principal',
                }
            )
            seen_urls.add(u)
        except (ValueError, OSError, AttributeError):
            pass
    for gi in unit_model.gallery_images.all():
        try:
            u = gi.image.url
            if u in seen_urls:
                continue
            carousel_images.append(
                {
                    'url': u,
                    'alt': (gi.caption or '').strip() or f'{unit_model.name} — interior {gi.pk}',
                }
            )
            seen_urls.add(u)
        except (ValueError, OSError, AttributeError):
            continue
    if not carousel_images and unit_model.card_image:
        try:
            carousel_images.append(
                {'url': unit_model.card_image.url, 'alt': unit_model.name}
            )
        except (ValueError, OSError, AttributeError):
            pass
    return carousel_images


def _process_unit_model_floor_plans_post(request, unit_model):
    """Elimina plantas marcadas y añade nuevas (archivos + etiquetas por línea)."""
    if not floorplan_table_ready():
        return
    for fp_id in request.POST.getlist('delete_floor_plan'):
        if str(fp_id).isdigit():
            DevelopmentUnitModelFloorPlan.objects.filter(
                pk=int(fp_id), unit_model=unit_model
            ).delete()
    files = request.FILES.getlist('floor_plans')
    if not files:
        return
    labels_text = (request.POST.get('floor_plan_labels') or '').strip()
    label_lines = [ln.strip() for ln in labels_text.splitlines() if ln.strip()]
    agg = unit_model.floor_plans.aggregate(mx=models.Max('order'))
    max_order = agg['mx']
    if max_order is None:
        max_order = -1
    for idx, f in enumerate(files):
        label = (
            label_lines[idx]
            if idx < len(label_lines)
            else f'Planta {max_order + idx + 2}'
        )
        DevelopmentUnitModelFloorPlan.objects.create(
            unit_model=unit_model,
            image=f,
            label=(label or 'Planta')[:120],
            order=max_order + 1 + idx,
        )


def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_dev_cms(request):
    """CMS: textos públicos de /desarrollos/ y ficha + imagen hero del listado."""
    config = DevelopmentsPageConfig.load()
    if request.method == 'POST':
        config.smart_match_badge = (request.POST.get('smart_match_badge') or '').strip()[:80] or 'Smart match'
        config.smart_match_title = (request.POST.get('smart_match_title') or '').strip()[:300]
        config.smart_match_subtitle = (request.POST.get('smart_match_subtitle') or '').strip()[:400]
        config.catalog_section_title = (request.POST.get('catalog_section_title') or '').strip()[:200]
        config.cta_section_title = (request.POST.get('cta_section_title') or '').strip()[:300]
        config.detail_amenities_title = (request.POST.get('detail_amenities_title') or '').strip()[:200]
        config.detail_amenities_subtitle = (request.POST.get('detail_amenities_subtitle') or '').strip()
        config.detail_gallery_title = (request.POST.get('detail_gallery_title') or '').strip()[:200]
        config.detail_gallery_subtitle = (request.POST.get('detail_gallery_subtitle') or '').strip()
        config.detail_models_title = (request.POST.get('detail_models_title') or '').strip()[:120]

        if request.POST.get('clear_hero'):
            if config.hero_background:
                config.hero_background.delete(save=False)
            config.hero_background = None
        uploaded = request.FILES.get('hero_background')
        if uploaded:
            if config.hero_background:
                config.hero_background.delete(save=False)
            config.hero_background = uploaded

        config.save()
        messages.success(request, 'Configuración de textos e imagen hero guardada.')
        return redirect('developments:panel_cms')

    return render(request, 'developments/panel/cms.html', {
        'section': 'cms',
        'title': 'Textos y hero · Desarrollos',
        'config': config,
    })


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_developments(request):
    """Listado de desarrollos con filtros por ciudad y estatus de obra."""
    developments = Development.objects.all().prefetch_related('images').order_by('-is_featured', '-created_at')
    city_q = (request.GET.get('city') or '').strip()
    status_q = (request.GET.get('construction_status') or '').strip()
    if city_q:
        developments = developments.filter(city__icontains=city_q)
    if status_q and status_q in dict(Development.CONSTRUCTION_STATUS_CHOICES):
        developments = developments.filter(construction_status=status_q)

    cities = (
        Development.objects.order_by('city')
        .values_list('city', flat=True)
        .distinct()
    )

    return render(
        request,
        'developments/panel/list.html',
        {
            'section': 'developments',
            'developments': developments,
            'title': 'Gestión de desarrollos',
            'filter_city': city_q,
            'filter_status': status_q,
            'city_choices': cities,
            'construction_status_choices': Development.CONSTRUCTION_STATUS_CHOICES,
        },
    )

@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_development_add(request):
    """Agregar nuevo desarrollo"""
    amenity_catalog = Amenity.objects.filter(is_active=True).order_by('-priority_score', 'display_name')
    if request.method == 'POST':
        try:
            price_from_value = _parse_price_from_post(request.POST.get('price_from'))
            development = Development(
                name=request.POST.get('name'),
                subtitle=request.POST.get('subtitle', '').strip(),
                description=request.POST.get('description'),
                developer_name=request.POST.get('developer_name', '').strip(),
                amenities_text=request.POST.get('amenities_text', '').strip(),
                website_url=request.POST.get('website_url', '').strip(),
                location=request.POST.get('location'),
                latitude=parse_coordinate(request.POST.get('latitude')),
                longitude=parse_coordinate(request.POST.get('longitude')),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                google_maps_url=request.POST.get('google_maps_url', ''),
                operation_type=request.POST.get('operation_type'),
                product_type=request.POST.get('product_type') or 'mixto',
                construction_status=request.POST.get('construction_status') or 'preventa',
                levels=int(request.POST.get('levels') or 0),
                total_units=int(request.POST.get('total_units') or 0),
                available_units=int(request.POST.get('available_units') or 0),
                parking_spaces=int(request.POST.get('parking_spaces') or 0),
                total_m2=int(request.POST.get('total_m2') or 0),
                price_from=price_from_value,
                delivery_date=request.POST.get('delivery_date') or None,
                is_featured='is_featured' in request.POST,
                is_active='is_active' in request.POST,
            )
            slug_input = (request.POST.get('slug') or '').strip()[:220]
            if slug_input:
                development.slug = slug_input
            development.save()
            amenity_ids = request.POST.getlist('amenities')
            if amenity_ids:
                development.amenities.set(Amenity.objects.filter(pk__in=amenity_ids, is_active=True))
            
            # Agregar imágenes (portada = primera; el modelo sincroniza is_main vía category)
            images = request.FILES.getlist('images')
            for idx, image in enumerate(images):
                DevelopmentImage.objects.create(
                    development=development,
                    image=image,
                    category=(
                        DevelopmentImage.Category.COVER
                        if idx == 0
                        else DevelopmentImage.Category.GALLERY
                    ),
                    order=idx,
                )
            
            messages.success(request, f'Desarrollo "{development.name}" creado exitosamente.')
            return redirect('developments:panel_list')
        except ValueError as e:
            messages.error(request, str(e))
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al crear desarrollo')
            messages.error(request, f'Error de base de datos al crear desarrollo: {str(e)}')
    
    return render(request, 'developments/panel/add.html', {
        'section': 'developments',
        'title': 'Nuevo Desarrollo',
        'amenity_catalog': amenity_catalog,
    })

@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_development_edit(request, pk):
    """Editar desarrollo"""
    development = get_object_or_404(Development, pk=pk)
    amenity_catalog = Amenity.objects.filter(is_active=True).order_by('-priority_score', 'display_name')
    
    if request.method == 'POST':
        try:
            price_from_value = _parse_price_from_post(request.POST.get('price_from'))
            development.name = request.POST.get('name')
            slug_input = (request.POST.get('slug') or '').strip()[:220]
            if slug_input:
                development.slug = slug_input
            elif request.POST.get('regenerate_slug'):
                development.slug = ''
            development.subtitle = request.POST.get('subtitle', '').strip()
            development.description = request.POST.get('description')
            development.developer_name = request.POST.get('developer_name', '').strip()
            development.amenities_text = request.POST.get('amenities_text', '').strip()
            development.website_url = request.POST.get('website_url', '').strip()
            development.location = request.POST.get('location')
            development.latitude = parse_coordinate(request.POST.get('latitude'))
            development.longitude = parse_coordinate(request.POST.get('longitude'))
            development.city = request.POST.get('city')
            development.state = request.POST.get('state')
            development.google_maps_url = request.POST.get('google_maps_url', '')
            development.operation_type = request.POST.get('operation_type')
            development.product_type = request.POST.get('product_type') or 'mixto'
            development.construction_status = request.POST.get('construction_status') or 'preventa'
            development.levels = int(request.POST.get('levels') or 0)
            development.total_units = int(request.POST.get('total_units') or 0)
            development.available_units = int(request.POST.get('available_units') or 0)
            development.parking_spaces = int(request.POST.get('parking_spaces') or 0)
            development.total_m2 = int(request.POST.get('total_m2') or 0)
            development.price_from = price_from_value
            development.delivery_date = request.POST.get('delivery_date') or None
            development.is_featured = 'is_featured' in request.POST
            development.is_active = 'is_active' in request.POST
            development.save()
            amenity_ids = request.POST.getlist('amenities')
            development.amenities.set(Amenity.objects.filter(pk__in=amenity_ids, is_active=True))
            
            # Agregar nuevas imágenes (si aún no hay portada, la primera del lote la cubre)
            images = request.FILES.getlist('images')
            if images:
                current_count = development.images.count()
                has_cover = development.images.filter(
                    Q(category=DevelopmentImage.Category.COVER) | Q(is_main=True)
                ).exists()
                for idx, image in enumerate(images):
                    if not has_cover and idx == 0:
                        cat = DevelopmentImage.Category.COVER
                        has_cover = True
                    else:
                        cat = DevelopmentImage.Category.GALLERY
                    DevelopmentImage.objects.create(
                        development=development,
                        image=image,
                        category=cat,
                        order=current_count + idx,
                    )
            
            messages.success(request, f'Desarrollo "{development.name}" actualizado exitosamente.')
            return redirect('developments:panel_list')
        except ValueError as e:
            messages.error(request, str(e))
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al actualizar desarrollo %s', pk)
            messages.error(request, f'Error de base de datos al actualizar desarrollo: {str(e)}')
    
    context = {
        'section': 'developments',
        'development': development,
        'title': 'Editar Desarrollo',
        'amenity_catalog': amenity_catalog,
        'selected_amenity_ids': set(development.amenities.values_list('id', flat=True)),
    }
    
    return render(request, 'developments/panel/edit.html', context)

@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_development_delete(request, pk):
    """Eliminar desarrollo"""
    development = get_object_or_404(Development, pk=pk)
    
    if request.method == 'POST':
        name = development.name
        development.delete()
        messages.success(request, f'Desarrollo "{name}" eliminado exitosamente.')
        return redirect('developments:panel_list')
    
    context = {
        'section': 'developments',
        'development': development,
        'title': 'Eliminar Desarrollo',
    }
    
    return render(request, 'developments/panel/delete.html', context)

@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_development_images(request, pk):
    """Gestionar imágenes del desarrollo (categorías, portada, borrado con archivo)."""
    development = get_object_or_404(Development, pk=pk)
    valid_upload_cats = {
        DevelopmentImage.Category.COVER,
        DevelopmentImage.Category.GALLERY,
        DevelopmentImage.Category.PLANS,
    }

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upload':
            files = request.FILES.getlist('images')
            if not files:
                messages.warning(request, 'No se seleccionaron imágenes.')
                return redirect('developments:panel_images', pk=pk)

            raw_cat = (request.POST.get('upload_category') or '').strip()
            upload_category = raw_cat if raw_cat in valid_upload_cats else DevelopmentImage.Category.GALLERY

            has_cover = development.images.filter(
                Q(category=DevelopmentImage.Category.COVER) | Q(is_main=True)
            ).exists()
            current_count = development.images.count()
            n = len(files)

            for idx, image_file in enumerate(files):
                if upload_category == DevelopmentImage.Category.PLANS:
                    cat = DevelopmentImage.Category.PLANS
                elif upload_category == DevelopmentImage.Category.COVER:
                    cat = (
                        DevelopmentImage.Category.COVER
                        if idx == 0
                        else DevelopmentImage.Category.GALLERY
                    )
                else:
                    if not has_cover and idx == 0:
                        cat = DevelopmentImage.Category.COVER
                        has_cover = True
                    else:
                        cat = DevelopmentImage.Category.GALLERY

                DevelopmentImage.objects.create(
                    development=development,
                    image=image_file,
                    category=cat,
                    order=current_count + idx,
                )

            messages.success(request, f'{n} imagen(es) agregada(s) exitosamente.')
            return redirect('developments:panel_images', pk=pk)

        if action == 'delete':
            try:
                image_id = int(request.POST.get('image_id') or 0)
            except (TypeError, ValueError):
                messages.error(request, 'Identificador de imagen no válido.')
                return redirect('developments:panel_images', pk=pk)
            image = get_object_or_404(DevelopmentImage, pk=image_id, development=development)
            try:
                if image.image and image.image.name:
                    image.image.delete(save=False)
            except (OSError, ValueError, AttributeError) as exc:
                messages.warning(
                    request,
                    f'No se pudo eliminar el archivo en almacenamiento: {exc}',
                )
            image.delete()
            messages.success(request, 'Imagen eliminada del desarrollo.')
            return redirect('developments:panel_images', pk=pk)

        if action == 'set_main':
            try:
                image_id = int(request.POST.get('image_id') or 0)
            except (TypeError, ValueError):
                messages.error(request, 'Identificador de imagen no válido.')
                return redirect('developments:panel_images', pk=pk)
            image = get_object_or_404(DevelopmentImage, pk=image_id, development=development)
            image.category = DevelopmentImage.Category.COVER
            image.save()
            messages.success(request, 'Imagen principal actualizada.')
            return redirect('developments:panel_images', pk=pk)

        return redirect('developments:panel_images', pk=pk)

    images_qs = development.images.annotate(
        _panel_cat_sort=Case(
            When(category=DevelopmentImage.Category.COVER, then=0),
            When(category=DevelopmentImage.Category.GALLERY, then=1),
            When(category=DevelopmentImage.Category.PLANS, then=2),
            default=3,
            output_field=IntegerField(),
        ),
    ).order_by('-is_main', '_panel_cat_sort', 'order', 'id')

    context = {
        'section': 'developments',
        'development': development,
        'images': images_qs,
        'title': f'Imágenes de {development.name}',
        'upload_category_choices': DevelopmentImage.Category.choices,
    }

    return render(request, 'developments/panel/images.html', context)


def _parse_optional_price_from_post(raw_value):
    cleaned = (raw_value or '').strip()
    if not cleaned:
        return None
    return _parse_price_from_post(raw_value)


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_unit_models_list(request):
    qs = (
        DevelopmentUnitModel.objects.select_related('development')
        .defer(*_UNIT_MODEL_OPTIONAL_TEXT_FIELDS)
        .order_by('development__name', 'order', 'id')
    )
    dev_filter = request.GET.get('development_id')
    fid = int(dev_filter) if (dev_filter and str(dev_filter).isdigit()) else None
    if fid:
        qs = qs.filter(development_id=fid)
    return render(
        request,
        'developments/panel/unit_models_list.html',
        {
            'section': 'models',
            'title': 'Modelos / prototipos',
            'unit_models': qs,
            'developments': Development.objects.order_by('name'),
            'filter_development_id': fid,
        },
    )


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_unit_model_add(request):
    developments = Development.objects.order_by('name')
    if request.method == 'POST':
        try:
            dev_id = int(request.POST.get('development_id') or 0)
            development = get_object_or_404(Development, pk=dev_id)
            bathrooms_raw = (request.POST.get('bathrooms') or '0').replace(',', '.')
            bathrooms = Decimal(bathrooms_raw)
            cm_raw = (request.POST.get('construction_m2') or '').strip().replace(',', '')
            construction_m2 = Decimal(cm_raw) if cm_raw else None
            um = DevelopmentUnitModel(
                development=development,
                name=(request.POST.get('name') or '').strip()[:120],
                slug=(request.POST.get('slug') or '').strip()[:130],
                order=int(request.POST.get('order') or 0),
                bedrooms=int(request.POST.get('bedrooms') or 0),
                bathrooms=bathrooms,
                construction_m2=construction_m2,
                price_from=_parse_optional_price_from_post(request.POST.get('price_from')),
                description=(request.POST.get('description') or '').strip(),
                other_features_text=(request.POST.get('other_features_text') or '').strip(),
                is_active='is_active' in request.POST,
            )
            card = request.FILES.get('card_image')
            if card:
                um.card_image = card
            um.save()
            gallery = request.FILES.getlist('gallery')
            start = um.gallery_images.count()
            for idx, f in enumerate(gallery):
                DevelopmentUnitModelImage.objects.create(
                    unit_model=um, image=f, order=start + idx
                )
            _process_unit_model_floor_plans_post(request, um)
            messages.success(request, f'Modelo "{um.name}" creado.')
            return redirect('developments:panel_unit_models')
        except (ValueError, TypeError, ArithmeticError) as e:
            messages.error(request, f'Error de validación en modelo: {str(e)}')
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al crear modelo de desarrollo')
            messages.error(request, f'Error de base de datos en modelo: {str(e)}')
    return render(
        request,
        'developments/panel/unit_model_form.html',
        {
            'section': 'models',
            'title': 'Agregar modelo',
            'developments': developments,
            'unit_model': None,
            'floor_plans_supported': floorplan_table_ready(),
            'floor_plan_items': [],
        },
    )


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_unit_model_edit(request, pk):
    try:
        um = _get_unit_model_for_panel_edit(pk)
    except (ProgrammingError, OperationalError):
        messages.error(
            request,
            'No se pudo leer la tabla de modelos. Verifica la base de datos y ejecuta: python manage.py migrate',
        )
        return redirect('developments:panel_list')
    developments = Development.objects.order_by('name')
    floor_plan_items = _floor_plan_items_for_panel(um)
    if request.method == 'POST':
        try:
            dev_id = int(request.POST.get('development_id') or 0)
            development = get_object_or_404(Development, pk=dev_id)
            bathrooms_raw = (request.POST.get('bathrooms') or '0').replace(',', '.')
            bathrooms = Decimal(bathrooms_raw)
            cm_raw = (request.POST.get('construction_m2') or '').strip().replace(',', '')
            construction_m2 = Decimal(cm_raw) if cm_raw else None
            um.development = development
            um.name = (request.POST.get('name') or '').strip()[:120]
            slug_in = (request.POST.get('slug') or '').strip()[:130]
            if slug_in:
                um.slug = slug_in
            elif request.POST.get('regenerate_slug'):
                um.slug = ''
            um.order = int(request.POST.get('order') or 0)
            um.bedrooms = int(request.POST.get('bedrooms') or 0)
            um.bathrooms = bathrooms
            um.construction_m2 = construction_m2
            um.price_from = _parse_optional_price_from_post(request.POST.get('price_from'))
            um.description = (request.POST.get('description') or '').strip()
            um.other_features_text = (request.POST.get('other_features_text') or '').strip()
            um.is_active = 'is_active' in request.POST
            card = request.FILES.get('card_image')
            if card:
                um.card_image = card
            um.save()
            _process_unit_model_floor_plans_post(request, um)
            gallery = request.FILES.getlist('gallery')
            start = um.gallery_images.count()
            for idx, f in enumerate(gallery):
                DevelopmentUnitModelImage.objects.create(
                    unit_model=um, image=f, order=start + idx
                )
            messages.success(request, 'Modelo actualizado.')
            return redirect('developments:panel_unit_models')
        except (ValueError, TypeError, ArithmeticError) as e:
            messages.error(request, f'Error de validación en modelo: {str(e)}')
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al editar modelo %s', pk)
            messages.error(request, f'Error de base de datos en modelo: {str(e)}')
    return render(
        request,
        'developments/panel/unit_model_form.html',
        {
            'section': 'models',
            'title': f'Editar modelo · {um.name}',
            'developments': developments,
            'unit_model': um,
            'floor_plans_supported': floorplan_table_ready(),
            'floor_plan_items': floor_plan_items,
        },
    )


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_unit_model_images(request, pk):
    um = get_object_or_404(DevelopmentUnitModel.objects.select_related('development'), pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'upload':
            files = request.FILES.getlist('images')
            if files:
                start = um.gallery_images.count()
                for idx, f in enumerate(files):
                    DevelopmentUnitModelImage.objects.create(
                        unit_model=um, image=f, order=start + idx
                    )
                messages.success(request, f'{len(files)} imagen(es) agregadas.')
            else:
                messages.warning(request, 'No se seleccionaron imágenes.')
        elif action == 'delete':
            img = get_object_or_404(
                DevelopmentUnitModelImage, pk=request.POST.get('image_id'), unit_model=um
            )
            img.delete()
            messages.success(request, 'Imagen eliminada.')
        elif action == 'reorder':
            img = get_object_or_404(
                DevelopmentUnitModelImage,
                pk=request.POST.get('image_id'),
                unit_model=um,
            )
            key = f'order_{img.pk}'
            if key in request.POST:
                try:
                    img.order = int(request.POST.get(key))
                    img.save(update_fields=['order'])
                except (TypeError, ValueError):
                    pass
            messages.success(request, 'Orden actualizado.')
        return redirect('developments:panel_unit_model_images', pk=pk)
    return render(
        request,
        'developments/panel/unit_model_images.html',
        {
            'section': 'models',
            'title': f'Galería · {um.name}',
            'unit_model': um,
            'images': um.gallery_images.all().order_by('order', 'id'),
        },
    )


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_amenity_list(request):
    return render(
        request,
        'developments/panel/amenities_list.html',
        {
            'section': 'amenities',
            'title': 'Catálogo de amenidades',
            'amenities': Amenity.objects.select_related('category').order_by('category__sort_order', '-priority_score', 'display_name'),
        },
    )


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_amenity_add(request):
    if request.method == 'POST':
        code = (request.POST.get('code') or '').strip().lower().replace(' ', '-')
        if not code:
            code = slugify(request.POST.get('name') or '')[:50] or 'amenidad'
        base = code
        n = 1
        while Amenity.objects.filter(slug=code).exists():
            code = f'{base}-{n}'
            n += 1
        category_id = request.POST.get('category_id')
        category = AmenityCategory.objects.filter(pk=category_id).first() or AmenityCategory.objects.order_by('sort_order', 'name').first()
        if not category:
            category = AmenityCategory.objects.create(
                name='General',
                slug='general',
                icon='bi-grid-1x2',
                description='Amenidades generales',
                sort_order=999,
            )
        name = (request.POST.get('name') or '').strip()[:120]
        Amenity.objects.create(
            name=name,
            display_name=(request.POST.get('display_name') or name).strip()[:120],
            slug=code[:140],
            category=category,
            icon=(request.POST.get('icon') or 'bi-check2-circle').strip()[:40],
            description=(request.POST.get('description') or '').strip(),
            priority_score=int(request.POST.get('priority_score') or 0),
            is_premium='is_premium' in request.POST,
            is_active='is_active' in request.POST,
        )
        messages.success(request, 'Amenidad creada.')
        return redirect('developments:panel_amenities')
    return render(
        request,
        'developments/panel/amenity_form.html',
        {
            'section': 'amenities',
            'title': 'Nueva amenidad',
            'amenity': None,
            'categories': AmenityCategory.objects.order_by('sort_order', 'name'),
        },
    )


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_amenity_edit(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    if request.method == 'POST':
        new_slug = (request.POST.get('code') or '').strip().lower()[:140]
        if new_slug and new_slug != amenity.slug:
            if not Amenity.objects.filter(slug=new_slug).exclude(pk=pk).exists():
                amenity.slug = new_slug
        name = (request.POST.get('name') or '').strip()[:120]
        amenity.name = name
        amenity.display_name = (request.POST.get('display_name') or name).strip()[:120]
        amenity.icon = (request.POST.get('icon') or 'bi-check2-circle').strip()[:40]
        amenity.description = (request.POST.get('description') or '').strip()
        amenity.priority_score = int(request.POST.get('priority_score') or 0)
        amenity.is_premium = 'is_premium' in request.POST
        category_id = request.POST.get('category_id')
        category = AmenityCategory.objects.filter(pk=category_id).first()
        if category:
            amenity.category = category
        amenity.is_active = 'is_active' in request.POST
        amenity.save()
        messages.success(request, 'Amenidad actualizada.')
        return redirect('developments:panel_amenities')
    return render(
        request,
        'developments/panel/amenity_form.html',
        {
            'section': 'amenities',
            'title': 'Editar amenidad',
            'amenity': amenity,
            'categories': AmenityCategory.objects.order_by('sort_order', 'name'),
        },
    )


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def panel_amenity_delete(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    if request.method == 'POST':
        amenity.delete()
        messages.success(request, 'Amenidad eliminada.')
        return redirect('developments:panel_amenities')
    return render(
        request,
        'developments/panel/amenity_delete.html',
        {'section': 'amenities', 'title': 'Eliminar amenidad', 'amenity': amenity},
    )

