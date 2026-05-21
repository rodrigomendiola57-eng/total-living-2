import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from decimal import Decimal
from django.db.utils import OperationalError, ProgrammingError
from django.utils.text import slugify
from .models import (
    Amenity,
    AmenityAlias,
    InteriorFeature,
    Property,
    PropertyFeature,
    PropertyImage,
    PropertyOperation,
    PropertyType,
    ServiceFeature,
)
from .money import parse_coordinate, parse_decimal_value, parse_mx_money
from .forms import PropertyForm, PropertyImageForm
from regions.models import Region

logger = logging.getLogger(__name__)


def amenities_api(request):
    """
    API simple de catálogo de amenidades con búsqueda por nombre/alias.
    """
    query = (request.GET.get('q') or '').strip()
    qs = Amenity.objects.filter(is_active=True).select_related('category')
    if query:
        q_slug = slugify(query)
        alias_ids = AmenityAlias.objects.filter(alias_slug__icontains=q_slug).values_list('amenity_id', flat=True)
        qs = qs.filter(
            Q(display_name__icontains=query) |
            Q(name__icontains=query) |
            Q(slug__icontains=q_slug) |
            Q(id__in=alias_ids)
        )
    qs = qs.order_by('category__sort_order', '-priority_score', 'display_name')[:120]
    return JsonResponse(
        {
            'results': [
                {
                    'id': str(a.id),
                    'slug': a.slug,
                    'name': a.display_name,
                    'category': a.category.name,
                    'icon': a.icon_class,
                    'is_premium': a.is_premium,
                }
                for a in qs
            ]
        }
    )


def _to_decimal(raw):
    return parse_decimal_value(raw)


def _to_int(raw):
    if raw is None:
        return None
    raw = str(raw).strip()
    if not raw:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def properties_map(request):
    """Mapa público con todas las propiedades disponibles que tengan coordenadas."""
    props = Property.objects.filter(
        status='disponible',
        latitude__isnull=False,
        longitude__isnull=False,
    ).only('id', 'title', 'latitude', 'longitude', 'slug')
    markers = []
    for p in props:
        markers.append({
            'id': p.pk,
            'title': p.title,
            'lat': float(p.latitude),
            'lng': float(p.longitude),
            'url': p.get_absolute_url(),
            'price': p.get_price_display(),
        })
    return render(request, 'properties/map.html', {'map_markers': markers})


def property_list(request):
    """Vista para listar todas las propiedades"""

    # Obtener todas las propiedades disponibles
    properties = Property.objects.filter(status='disponible').prefetch_related('images').order_by('-created_at')
    
    # Filtros básicos
    property_type = request.GET.get('tipo', '')
    operation_type = request.GET.get('operacion', '')
    state = request.GET.get('estado', '')
    city = request.GET.get('ciudad', '')  # Mantener para compatibilidad
    region = request.GET.get('region', '')
    
    # Filtros avanzados
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    recamaras = request.GET.get('recamaras', '')
    banos = request.GET.get('banos', '')
    medios_banos = request.GET.get('medios_banos', '')
    estacionamiento = request.GET.get('estacionamiento', '')
    area_min = request.GET.get('area_min', '')
    area_max = request.GET.get('area_max', '')
    area_construccion_min = request.GET.get('area_construccion_min', '')
    area_construccion_max = request.GET.get('area_construccion_max', '')
    area_terreno_min = request.GET.get('area_terreno_min', '')
    area_terreno_max = request.GET.get('area_terreno_max', '')
    niveles = request.GET.get('niveles', '')
    year_built_min = request.GET.get('year_built_min', '')
    year_built_max = request.GET.get('year_built_max', '')
    ambientes = request.GET.get('ambientes', '')
    cuota_mantenimiento_max = request.GET.get('cuota_mantenimiento_max', '')
    
    # Aplicar filtros básicos
    if property_type:
        properties = properties.filter(property_type=property_type)
    if operation_type:
        properties = properties.filter(operation_type=operation_type)
    if state:
        properties = properties.filter(state__icontains=state)
    elif city:  # Mantener compatibilidad con búsquedas antiguas
        properties = properties.filter(city__icontains=city)
    if region:
        region_obj = Region.objects.filter(slug=region, is_active=True).first()
        if region_obj:
            properties = properties.filter(region=region_obj)
        else:
            # Compatibilidad con filtros antiguos por texto
            properties = properties.filter(Q(address__icontains=region) | Q(city__icontains=region))
    
    # Aplicar filtros de precio
    if precio_min:
        min_price = _to_decimal(precio_min)
        if min_price is not None:
            properties = properties.filter(price__gte=min_price)
    if precio_max:
        max_price = _to_decimal(precio_max)
        if max_price is not None:
            properties = properties.filter(price__lte=max_price)
    
    # Aplicar filtros de características
    if recamaras:
        try:
            properties = properties.filter(bedrooms__gte=int(recamaras))
        except (ValueError, TypeError):
            pass
    if banos:
        try:
            properties = properties.filter(bathrooms__gte=int(banos))
        except (ValueError, TypeError):
            pass
    if medios_banos:
        try:
            properties = properties.filter(half_bathrooms__gte=int(medios_banos))
        except (ValueError, TypeError):
            pass
    if estacionamiento:
        try:
            properties = properties.filter(parking_spaces__gte=int(estacionamiento))
        except (ValueError, TypeError):
            pass
    if ambientes:
        try:
            properties = properties.filter(rooms__gte=int(ambientes))
        except (ValueError, TypeError):
            pass
    
    # Aplicar filtros de área
    if area_min:
        parsed_area_min = _to_decimal(area_min)
        if parsed_area_min is not None:
            properties = properties.filter(construction_area__gte=parsed_area_min)
    if area_max:
        parsed_area_max = _to_decimal(area_max)
        if parsed_area_max is not None:
            properties = properties.filter(construction_area__lte=parsed_area_max)
    if area_construccion_min:
        parsed_construction_min = _to_decimal(area_construccion_min)
        if parsed_construction_min is not None:
            properties = properties.filter(construction_area__gte=parsed_construction_min)
    if area_construccion_max:
        parsed_construction_max = _to_decimal(area_construccion_max)
        if parsed_construction_max is not None:
            properties = properties.filter(construction_area__lte=parsed_construction_max)
    if area_terreno_min:
        parsed_lot_min = _to_decimal(area_terreno_min)
        if parsed_lot_min is not None:
            properties = properties.filter(lot_area__gte=parsed_lot_min)
    if area_terreno_max:
        parsed_lot_max = _to_decimal(area_terreno_max)
        if parsed_lot_max is not None:
            properties = properties.filter(lot_area__lte=parsed_lot_max)
    
    # Aplicar filtros adicionales
    if niveles:
        try:
            properties = properties.filter(floors__gte=int(niveles))
        except (ValueError, TypeError):
            pass
    if year_built_min:
        try:
            properties = properties.filter(year_built__gte=int(year_built_min))
        except (ValueError, TypeError):
            pass
    if year_built_max:
        try:
            properties = properties.filter(year_built__lte=int(year_built_max))
        except (ValueError, TypeError):
            pass
    if cuota_mantenimiento_max:
        maintenance_fee_max = _to_decimal(cuota_mantenimiento_max)
        if maintenance_fee_max is not None:
            properties = properties.filter(maintenance_fee__lte=maintenance_fee_max)
    
    # Paginación
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener tipos y operaciones para filtros
    property_types = PropertyType.choices
    operation_types = PropertyOperation.choices
    
    context = {
        'properties': page_obj,
        'property_types': property_types,
        'operation_types': operation_types,
        'current_filters': {
            'tipo': property_type,
            'operacion': operation_type,
            'ciudad': city,
            'region': region,
        }
    }
    
    return render(request, 'properties/list.html', context)


def departamentos_list(request):
    """Vista para listar solo departamentos en venta"""
    from properties.models import PropertyType, PropertyOperation
    
    # Filtrar solo departamentos disponibles para venta
    properties = Property.objects.filter(
        status='disponible',
        property_type='departamento',
        operation_type__in=['venta', 'venta_renta']
    ).prefetch_related('images')
    
    # Aplicar filtros adicionales
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    recamaras = request.GET.get('recamaras', '')
    banos = request.GET.get('banos', '')
    
    if city:
        properties = properties.filter(city__icontains=city)
    if precio_min:
        parsed_min = _to_decimal(precio_min)
        if parsed_min is not None:
            properties = properties.filter(price__gte=parsed_min)
    if precio_max:
        parsed_max = _to_decimal(precio_max)
        if parsed_max is not None:
            properties = properties.filter(price__lte=parsed_max)
    if recamaras:
        properties = properties.filter(bedrooms__gte=recamaras)
    if banos:
        properties = properties.filter(bathrooms__gte=banos)
    
    properties = properties.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Departamentos en Venta',
        'subtitle': 'Encuentra el departamento perfecto para ti',
    }
    
    return render(request, 'properties/departamentos.html', context)


def comprar_todas_list(request):
    """Vista para listar todas las propiedades en venta."""
    base_properties = Property.objects.filter(
        status='disponible',
        operation_type__in=['venta', 'venta_renta']
    ).prefetch_related('images')
    properties = base_properties

    # Filtros principales
    operation_type = request.GET.get('operacion', 'venta')
    property_type = request.GET.get('tipo', '')
    city = request.GET.get('ciudad', '')
    state = request.GET.get('estado', '')
    region_slug = request.GET.get('region', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    sort_by = request.GET.get('orden', 'reciente')
    view_mode = request.GET.get('vista', 'lista')
    recamaras = request.GET.get('recamaras', '')
    banos = request.GET.get('banos', '')
    estacionamientos = request.GET.get('estacionamientos', '')
    construccion_min = request.GET.get('construccion_min', '')
    construccion_max = request.GET.get('construccion_max', '')
    terreno_min = request.GET.get('terreno_min', '')
    terreno_max = request.GET.get('terreno_max', '')
    antiguedad = request.GET.get('antiguedad', '')
    amueblado = request.GET.get('amueblado', '')
    estudio = request.GET.get('estudio', '')

    # Filtros nuevos normalizados (slug)
    amenity_slug = request.GET.get('amenity_slug', '').strip()
    service_slug = request.GET.get('service_slug', '').strip()
    interior_slug = request.GET.get('interior_slug', '').strip()

    # Tipo de operación
    if operation_type == 'renta':
        properties = Property.objects.filter(
            status='disponible',
            operation_type__in=['renta', 'venta_renta']
        ).prefetch_related('images')
        base_properties = properties
    elif operation_type == 'remate':
        properties = properties.filter(
            Q(title__icontains='remate') | Q(description__icontains='remate')
        )
    else:
        operation_type = 'venta'

    # Tipo de propiedad (incluye agrupadores para UI extendida)
    if property_type == 'residencial':
        properties = properties.filter(property_type__in=['casa', 'departamento', 'terreno', 'rancho'])
    elif property_type == 'comercial':
        properties = properties.filter(property_type__in=['local', 'oficina', 'bodega'])
    elif property_type == 'industrial':
        properties = properties.filter(property_type='bodega')
    elif property_type:
        properties = properties.filter(property_type=property_type)

    if city:
        properties = properties.filter(
            Q(city__icontains=city) |
            Q(address__icontains=city) |
            Q(region__name__icontains=city)
        )
    if state:
        properties = properties.filter(state__icontains=state)
    if region_slug:
        selected_region = Region.objects.filter(slug=region_slug, is_active=True).first()
        if selected_region:
            properties = properties.filter(region=selected_region)
        else:
            properties = properties.filter(
                Q(region__name__icontains=region_slug) |
                Q(address__icontains=region_slug) |
                Q(city__icontains=region_slug)
            )
    if precio_min:
        parsed_price_min = _to_decimal(precio_min)
        if parsed_price_min is not None:
            properties = properties.filter(price__gte=parsed_price_min)
    if precio_max:
        parsed_price_max = _to_decimal(precio_max)
        if parsed_price_max is not None:
            properties = properties.filter(price__lte=parsed_price_max)
    if recamaras:
        properties = properties.filter(bedrooms__gte=recamaras)
    if banos:
        properties = properties.filter(bathrooms__gte=banos)
    if estacionamientos:
        properties = properties.filter(parking_spaces__gte=estacionamientos)
    if construccion_min:
        parsed_construction_min = _to_decimal(construccion_min)
        if parsed_construction_min is not None:
            properties = properties.filter(construction_area__gte=parsed_construction_min)
    if construccion_max:
        parsed_construction_max = _to_decimal(construccion_max)
        if parsed_construction_max is not None:
            properties = properties.filter(construction_area__lte=parsed_construction_max)
    if terreno_min:
        parsed_lot_min = _to_decimal(terreno_min)
        if parsed_lot_min is not None:
            properties = properties.filter(lot_area__gte=parsed_lot_min)
    if terreno_max:
        parsed_lot_max = _to_decimal(terreno_max)
        if parsed_lot_max is not None:
            properties = properties.filter(lot_area__lte=parsed_lot_max)

    # Antigüedad por rangos de año de construcción
    current_year = timezone.now().year
    if antiguedad == '0_5':
        properties = properties.filter(year_built__gte=current_year - 5)
    elif antiguedad == '5_10':
        properties = properties.filter(year_built__gte=current_year - 10, year_built__lt=current_year - 5)
    elif antiguedad == '10_20':
        properties = properties.filter(year_built__gte=current_year - 20, year_built__lt=current_year - 10)
    elif antiguedad == '20_plus':
        properties = properties.filter(year_built__lt=current_year - 20)

    # Estudio (compatibilidad con filtro legacy)
    if estudio:
        properties = properties.filter(interior_features__slug='estudio')

    # "Amueblado" (aproximación por texto)
    if amueblado == 'si':
        properties = properties.filter(
            Q(title__icontains='amueblad') | Q(description__icontains='amueblad')
        )
    elif amueblado == 'no':
        properties = properties.exclude(
            Q(title__icontains='amueblad') | Q(description__icontains='amueblad')
        )

    # Amenidades / servicios / distribución (catálogo normalizado)
    if amenity_slug:
        properties = properties.filter(amenities__slug=amenity_slug)
    if service_slug:
        properties = properties.filter(service_features__slug=service_slug)
    if interior_slug:
        properties = properties.filter(interior_features__slug=interior_slug)

    if sort_by == 'precio_menor':
        properties = properties.order_by('price', '-created_at')
    elif sort_by == 'precio_mayor':
        properties = properties.order_by('-price', '-created_at')
    else:
        sort_by = 'reciente'
        properties = properties.order_by('-created_at')

    properties = properties.distinct()

    # Marcadores del mapa para resultados filtrados (sin limitar por paginación)
    map_markers = []
    for prop in properties:
        if prop.latitude is None or prop.longitude is None:
            continue
        main_image = prop.get_main_image()
        map_markers.append({
            'id': prop.pk,
            'title': prop.title,
            'lat': float(prop.latitude),
            'lng': float(prop.longitude),
            'url': prop.get_absolute_url(),
            'price': prop.get_price_display(),
            'image': main_image.image.url if main_image and main_image.image else '',
        })

    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    available_cities = list(
        base_properties.exclude(city__isnull=True).exclude(city__exact='')
        .order_by('city').values_list('city', flat=True).distinct()
    )
    mexico_states = [
        'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Chiapas',
        'Chihuahua', 'Ciudad de México', 'Coahuila', 'Colima', 'Durango',
        'Estado de México', 'Guanajuato', 'Guerrero', 'Hidalgo', 'Jalisco',
        'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla',
        'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa', 'Sonora',
        'Tabasco', 'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas'
    ]
    db_states = list(
        base_properties.exclude(state__isnull=True).exclude(state__exact='')
        .order_by('state').values_list('state', flat=True).distinct()
    )
    available_states = sorted(set(mexico_states + db_states))
    available_region_ids = list(
        base_properties.exclude(region__isnull=True).values_list('region_id', flat=True).distinct()
    )
    available_regions = Region.objects.filter(
        is_active=True,
        id__in=available_region_ids
    ).order_by('name')
    available_amenity_filters = Amenity.objects.filter(is_active=True).select_related('category').order_by('category__sort_order', 'display_name')
    available_service_filters = ServiceFeature.objects.filter(is_active=True).order_by('sort_order', 'name')
    available_interior_filters = InteriorFeature.objects.filter(is_active=True).order_by('sort_order', 'name')

    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Propiedades en Venta',
        'subtitle': 'Explora casas, departamentos, terrenos, locales y más',
        'icon': 'grid-3x3-gap',
        'available_cities': available_cities,
        'available_states': available_states,
        'available_regions': available_regions,
        'property_types': PropertyType.choices,
        'available_amenity_filters': available_amenity_filters,
        'available_service_filters': available_service_filters,
        'available_interior_filters': available_interior_filters,
        'current_filters': {
            'tipo': property_type,
            'operacion': operation_type,
            'ciudad': city,
            'estado': state,
            'region': region_slug,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'orden': sort_by,
            'vista': 'mapa' if view_mode == 'mapa' else 'lista',
            'recamaras': recamaras,
            'banos': banos,
            'estacionamientos': estacionamientos,
            'construccion_min': construccion_min,
            'construccion_max': construccion_max,
            'terreno_min': terreno_min,
            'terreno_max': terreno_max,
            'antiguedad': antiguedad,
            'amueblado': amueblado,
            'estudio': estudio,
            'amenity_slug': amenity_slug,
            'service_slug': service_slug,
            'interior_slug': interior_slug,
        }
    }
    context['map_markers'] = map_markers
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    context['filter_query'] = query_params.urlencode()

    return render(request, 'properties/categoria.html', context)


def casas_list(request):
    """Vista para listar solo casas en venta"""
    properties = Property.objects.filter(
        status='disponible',
        property_type='casa',
        operation_type__in=['venta', 'venta_renta']
    ).prefetch_related('images')
    
    # Aplicar filtros
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    recamaras = request.GET.get('recamaras', '')
    banos = request.GET.get('banos', '')
    
    if city:
        properties = properties.filter(city__icontains=city)
    if precio_min:
        parsed_price_min = _to_decimal(precio_min)
        if parsed_price_min is not None:
            properties = properties.filter(price__gte=parsed_price_min)
    if precio_max:
        parsed_price_max = _to_decimal(precio_max)
        if parsed_price_max is not None:
            properties = properties.filter(price__lte=parsed_price_max)
    if recamaras:
        properties = properties.filter(bedrooms__gte=recamaras)
    if banos:
        properties = properties.filter(bathrooms__gte=banos)
    
    properties = properties.order_by('-created_at')
    
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Casas en Venta',
        'subtitle': 'Encuentra la casa de tus sueños',
        'icon': 'house-door',
    }
    
    return render(request, 'properties/categoria.html', context)


def terrenos_list(request):
    """Vista para listar solo terrenos en venta"""
    properties = Property.objects.filter(
        status='disponible',
        property_type='terreno',
        operation_type__in=['venta', 'venta_renta']
    ).prefetch_related('images')
    
    # Aplicar filtros
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    area_min = request.GET.get('area_min', '')
    area_max = request.GET.get('area_max', '')
    
    if city:
        properties = properties.filter(city__icontains=city)
    if precio_min:
        parsed_price_min = _to_decimal(precio_min)
        if parsed_price_min is not None:
            properties = properties.filter(price__gte=parsed_price_min)
    if precio_max:
        parsed_price_max = _to_decimal(precio_max)
        if parsed_price_max is not None:
            properties = properties.filter(price__lte=parsed_price_max)
    if area_min:
        parsed_area_min = _to_decimal(area_min)
        if parsed_area_min is not None:
            properties = properties.filter(construction_area__gte=parsed_area_min)
    if area_max:
        parsed_area_max = _to_decimal(area_max)
        if parsed_area_max is not None:
            properties = properties.filter(construction_area__lte=parsed_area_max)
    
    properties = properties.order_by('-created_at')
    
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Terrenos en Venta',
        'subtitle': 'Invierte en el terreno ideal',
        'icon': 'map',
        'show_area': True,
    }
    
    return render(request, 'properties/categoria.html', context)


def locales_list(request):
    """Vista para listar solo locales comerciales en venta"""
    properties = Property.objects.filter(
        status='disponible',
        property_type='local',
        operation_type__in=['venta', 'venta_renta']
    ).prefetch_related('images')
    
    # Aplicar filtros
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    area_min = request.GET.get('area_min', '')
    area_max = request.GET.get('area_max', '')
    
    if city:
        properties = properties.filter(city__icontains=city)
    if precio_min:
        parsed_price_min = _to_decimal(precio_min)
        if parsed_price_min is not None:
            properties = properties.filter(price__gte=parsed_price_min)
    if precio_max:
        parsed_price_max = _to_decimal(precio_max)
        if parsed_price_max is not None:
            properties = properties.filter(price__lte=parsed_price_max)
    if area_min:
        parsed_area_min = _to_decimal(area_min)
        if parsed_area_min is not None:
            properties = properties.filter(construction_area__gte=parsed_area_min)
    if area_max:
        parsed_area_max = _to_decimal(area_max)
        if parsed_area_max is not None:
            properties = properties.filter(construction_area__lte=parsed_area_max)
    
    properties = properties.order_by('-created_at')
    
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Locales Comerciales en Venta',
        'subtitle': 'El espacio perfecto para tu negocio',
        'icon': 'shop',
        'show_area': True,
    }
    
    return render(request, 'properties/categoria.html', context)


def renta_list(request):
    """Vista para listar todas las propiedades en renta"""
    base_properties = Property.objects.filter(
        status='disponible',
        operation_type__in=['renta', 'venta_renta']
    ).prefetch_related('images')
    properties = base_properties
    
    # Aplicar filtros
    property_type = request.GET.get('tipo', '')
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    sort_by = request.GET.get('orden', 'reciente')
    view_mode = request.GET.get('vista', 'lista')
    recamaras = request.GET.get('recamaras', '')
    banos = request.GET.get('banos', '')
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    if city:
        properties = properties.filter(
            Q(city__icontains=city) |
            Q(address__icontains=city) |
            Q(region__name__icontains=city)
        )
    if precio_min:
        parsed_price_min = _to_decimal(precio_min)
        if parsed_price_min is not None:
            properties = properties.filter(price__gte=parsed_price_min)
    if precio_max:
        parsed_price_max = _to_decimal(precio_max)
        if parsed_price_max is not None:
            properties = properties.filter(price__lte=parsed_price_max)
    if recamaras:
        properties = properties.filter(bedrooms__gte=recamaras)
    if banos:
        properties = properties.filter(bathrooms__gte=banos)
    
    if sort_by == 'precio_menor':
        properties = properties.order_by('price', '-created_at')
    elif sort_by == 'precio_mayor':
        properties = properties.order_by('-price', '-created_at')
    else:
        sort_by = 'reciente'
        properties = properties.order_by('-created_at')

    # Marcadores del mapa para resultados filtrados (sin limitar por paginación)
    map_markers = []
    for prop in properties:
        if prop.latitude is None or prop.longitude is None:
            continue
        main_image = prop.get_main_image()
        map_markers.append({
            'id': prop.pk,
            'title': prop.title,
            'lat': float(prop.latitude),
            'lng': float(prop.longitude),
            'url': prop.get_absolute_url(),
            'price': prop.get_price_display(),
            'image': main_image.image.url if main_image and main_image.image else '',
        })
    
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Propiedades en Renta',
        'subtitle': 'Encuentra tu próximo hogar',
        'icon': 'key',
        'operation': 'renta',
        'available_cities': list(
            base_properties.exclude(city__isnull=True).exclude(city__exact='')
            .order_by('city').values_list('city', flat=True).distinct()
        ),
        'available_states': sorted(set([
            'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Chiapas',
            'Chihuahua', 'Ciudad de México', 'Coahuila', 'Colima', 'Durango',
            'Estado de México', 'Guanajuato', 'Guerrero', 'Hidalgo', 'Jalisco',
            'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla',
            'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa', 'Sonora',
            'Tabasco', 'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas'
        ] + list(
            base_properties.exclude(state__isnull=True).exclude(state__exact='')
            .order_by('state').values_list('state', flat=True).distinct()
        ))),
        'available_regions': Region.objects.filter(
            is_active=True,
            id__in=list(
                base_properties.exclude(region__isnull=True).values_list('region_id', flat=True).distinct()
            )
        ).order_by('name'),
        'property_types': PropertyType.choices,
        'current_filters': {
            'tipo': property_type,
            'operacion': 'renta',
            'ciudad': city,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'orden': sort_by,
            'vista': 'mapa' if view_mode == 'mapa' else 'lista',
            'recamaras': recamaras,
            'banos': banos,
            'estado': '',
            'region': '',
            'estacionamientos': '',
            'construccion_min': '',
            'construccion_max': '',
            'terreno_min': '',
            'terreno_max': '',
            'antiguedad': '',
            'amueblado': '',
            'estudio': '',
            'amenity_slug': '',
            'service_slug': '',
            'interior_slug': '',
        }
    }
    context['map_markers'] = map_markers
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    context['filter_query'] = query_params.urlencode()

    return render(request, 'properties/categoria.html', context)


def renta_departamentos_list(request):
    """Vista para listar departamentos en renta"""
    properties = Property.objects.filter(
        status='disponible',
        property_type='departamento',
        operation_type__in=['renta', 'venta_renta']
    ).prefetch_related('images')
    
    # Aplicar filtros
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    recamaras = request.GET.get('recamaras', '')
    banos = request.GET.get('banos', '')
    
    if city:
        properties = properties.filter(city__icontains=city)
    if precio_min:
        parsed_price_min = _to_decimal(precio_min)
        if parsed_price_min is not None:
            properties = properties.filter(price__gte=parsed_price_min)
    if precio_max:
        parsed_price_max = _to_decimal(precio_max)
        if parsed_price_max is not None:
            properties = properties.filter(price__lte=parsed_price_max)
    if recamaras:
        properties = properties.filter(bedrooms__gte=recamaras)
    if banos:
        properties = properties.filter(bathrooms__gte=banos)
    
    properties = properties.order_by('-created_at')
    
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Departamentos en Renta',
        'subtitle': 'Encuentra el departamento ideal',
        'icon': 'building',
        'operation': 'renta',
        'current_filters': {
            'ciudad': city,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'recamaras': recamaras,
            'banos': banos,
        }
    }
    
    return render(request, 'properties/categoria.html', context)


def renta_casas_list(request):
    """Vista para listar casas en renta"""
    
    properties = Property.objects.filter(
        status='disponible',
        property_type='casa',
        operation_type__in=['renta', 'venta_renta']
    ).prefetch_related('images')
    
    # Aplicar filtros
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    recamaras = request.GET.get('recamaras', '')
    banos = request.GET.get('banos', '')
    
    if city:
        properties = properties.filter(city__icontains=city)
    if precio_min:
        parsed_price_min = _to_decimal(precio_min)
        if parsed_price_min is not None:
            properties = properties.filter(price__gte=parsed_price_min)
    if precio_max:
        parsed_price_max = _to_decimal(precio_max)
        if parsed_price_max is not None:
            properties = properties.filter(price__lte=parsed_price_max)
    if recamaras:
        properties = properties.filter(bedrooms__gte=recamaras)
    if banos:
        properties = properties.filter(bathrooms__gte=banos)
    
    properties = properties.order_by('-created_at')
    
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Casas en Renta',
        'subtitle': 'Tu próximo hogar te espera',
        'icon': 'house-door',
        'operation': 'renta',
        'current_filters': {
            'ciudad': city,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'recamaras': recamaras,
            'banos': banos,
        }
    }
    
    return render(request, 'properties/categoria.html', context)


def renta_locales_list(request):
    """Vista para listar locales comerciales en renta"""
    properties = Property.objects.filter(
        status='disponible',
        property_type='local',
        operation_type__in=['renta', 'venta_renta']
    ).prefetch_related('images')
    
    # Aplicar filtros
    city = request.GET.get('ciudad', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    area_min = request.GET.get('area_min', '')
    area_max = request.GET.get('area_max', '')
    
    if city:
        properties = properties.filter(city__icontains=city)
    if precio_min:
        parsed_price_min = _to_decimal(precio_min)
        if parsed_price_min is not None:
            properties = properties.filter(price__gte=parsed_price_min)
    if precio_max:
        parsed_price_max = _to_decimal(precio_max)
        if parsed_price_max is not None:
            properties = properties.filter(price__lte=parsed_price_max)
    if area_min:
        parsed_area_min = _to_decimal(area_min)
        if parsed_area_min is not None:
            properties = properties.filter(construction_area__gte=parsed_area_min)
    if area_max:
        parsed_area_max = _to_decimal(area_max)
        if parsed_area_max is not None:
            properties = properties.filter(construction_area__lte=parsed_area_max)
    
    properties = properties.order_by('-created_at')
    
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj,
        'title': 'Locales Comerciales en Renta',
        'subtitle': 'El espacio ideal para tu negocio',
        'icon': 'shop',
        'show_area': True,
        'operation': 'renta',
        'current_filters': {
            'ciudad': city,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'area_min': area_min,
            'area_max': area_max,
        }
    }
    
    return render(request, 'properties/categoria.html', context)


def _address_neighborhood_tokens(address):
    """
    Fragmentos de dirección útiles para acotar colonia/zona (ej. Juriquilla, Zibata).
    Evita tokens genéricos que matchean toda la ciudad.
    """
    if not address:
        return []
    generic = {
        'querétaro', 'queretaro', 'qro.', 'qro',
        'mexico', 'méxico', 'mx',
        'guadalajara', 'monterrey', 'pachuca', 'mineral de la reforma',
    }
    parts = [p.strip() for p in address.replace(';', ',').split(',') if p.strip()]
    tokens = []
    for p in parts:
        pl = p.lower().strip('.')
        if len(p) < 5:
            continue
        if pl in generic:
            continue
        tokens.append(p)
    tokens.sort(key=len, reverse=True)
    out = []
    for t in tokens:
        if t not in out:
            out.append(t)
    return out[:6]


def similar_properties_for_detail(property_obj, limit=4):
    """
    Propiedades similares: prioriza misma región (zona), luego colonia en dirección,
    luego ciudad + tipo + operación, y por último solo ciudad + tipo.

    Usa city__iexact para que funcione aunque varíen mayúsculas en BD.
    Incluye fallbacks finales para que casi siempre haya sugerencias si existen
    otras propiedades disponibles (futuras fichas incluidas).
    """
    base = (
        Property.objects.filter(status='disponible')
        .exclude(pk=property_obj.pk)
        .prefetch_related('images')
    )
    order_by = ('-is_featured', '-created_at')
    seen = {property_obj.pk}
    result = []

    def add_from_queryset(qs):
        for p in qs:
            if p.pk not in seen and len(result) < limit:
                seen.add(p.pk)
                result.append(p)

    city = (property_obj.city or '').strip()
    state = (property_obj.state or '').strip()

    def filter_city(qs):
        """Acota por ciudad si existe; si no, por estado."""
        if city:
            return qs.filter(city__iexact=city)
        if state:
            return qs.filter(state__iexact=state)
        return qs

    # 1) Misma región + tipo + operación (mejor proxy de "misma zona")
    if property_obj.region_id:
        qs = (
            base.filter(
                region_id=property_obj.region_id,
                property_type=property_obj.property_type,
                operation_type=property_obj.operation_type,
            )
            .order_by(*order_by)[:limit]
        )
        add_from_queryset(qs)

    # 2) Misma región + tipo (si faltan resultados)
    if len(result) < limit and property_obj.region_id:
        qs = (
            base.filter(region_id=property_obj.region_id, property_type=property_obj.property_type)
            .exclude(pk__in=seen)
            .order_by(*order_by)[: limit - len(result)]
        )
        add_from_queryset(qs)

    # 3) Colonia/zona por texto en dirección (ej. Juriquilla dentro de Querétaro)
    if len(result) < limit:
        for token in _address_neighborhood_tokens(property_obj.address):
            if len(result) >= limit:
                break
            qs = filter_city(
                base.filter(
                    property_type=property_obj.property_type,
                    operation_type=property_obj.operation_type,
                    address__icontains=token,
                )
            ).exclude(pk__in=seen).order_by(*order_by)[: limit - len(result)]
            add_from_queryset(qs)

    # 4) Ciudad/estado + tipo + operación (fallback amplio)
    if len(result) < limit:
        qs = filter_city(
            base.filter(
                property_type=property_obj.property_type,
                operation_type=property_obj.operation_type,
            )
        ).exclude(pk__in=seen).order_by(*order_by)[: limit - len(result)]
        add_from_queryset(qs)

    # 5) Ciudad/estado + tipo (sin exigir misma operación)
    if len(result) < limit:
        qs = filter_city(
            base.filter(property_type=property_obj.property_type)
        ).exclude(pk__in=seen).order_by(*order_by)[: limit - len(result)]
        add_from_queryset(qs)

    # 6) Mismo tipo + operación (cualquier ciudad del estado, si hay estado)
    if len(result) < limit and state:
        qs = (
            base.filter(
                state__iexact=state,
                property_type=property_obj.property_type,
                operation_type=property_obj.operation_type,
            )
            .exclude(pk__in=seen)
            .order_by(*order_by)[: limit - len(result)]
        )
        add_from_queryset(qs)

    # 7) Mismo tipo + operación en todo el catálogo disponible
    if len(result) < limit:
        qs = (
            base.filter(
                property_type=property_obj.property_type,
                operation_type=property_obj.operation_type,
            )
            .exclude(pk__in=seen)
            .order_by(*order_by)[: limit - len(result)]
        )
        add_from_queryset(qs)

    # 8) Último recurso: cualquier otra propiedad disponible (recientes / destacadas)
    if len(result) < limit:
        qs = base.exclude(pk__in=seen).order_by(*order_by)[: limit - len(result)]
        add_from_queryset(qs)

    return result[:limit]


def property_detail(request, pk):
    """Vista para mostrar el detalle de una propiedad"""
    property_obj = get_object_or_404(
        Property.objects.select_related('region'),
        pk=pk,
    )
    
    # Obtener todas las imágenes de la propiedad
    images = property_obj.images.all().order_by('is_main', 'order')
    
    # Características asociadas a la propiedad (incluye financiamiento si se cargó en edición).
    features = property_obj.features.all()
    
    related_properties = similar_properties_for_detail(property_obj, limit=4)
    
    context = {
        'property': property_obj,
        'images': images,
        'features': features,
        'related_properties': related_properties,
    }
    
    return render(request, 'properties/detail.html', context)


def is_staff_user(user):
    """Verificar si el usuario es staff (administrador)"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def add_property(request):
    """Vista para agregar una nueva propiedad (solo administradores)"""
    
    if request.method == 'POST':
        try:
            # Crear propiedad directamente desde POST
            region_id = request.POST.get('region')
            selected_region = Region.objects.filter(pk=region_id, is_active=True).first() if region_id else None

            is_advisor_exclusive = 'is_advisor_exclusive' in request.POST
            selected_advisor = get_user_model().objects.filter(
                pk=request.POST.get('exclusive_advisor'),
                is_staff=True,
                is_active=True
            ).first() if request.POST.get('exclusive_advisor') else None

            _price = parse_mx_money(request.POST.get('price'))
            construction_area_raw = request.POST.get('construction_area')
            construction_area_value = _to_decimal(construction_area_raw)
            if construction_area_value is None:
                raise ValueError('El campo "Área Construcción (m²)" es obligatorio.')
            property_obj = Property(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                property_type=request.POST.get('property_type'),
                operation_type=request.POST.get('operation_type'),
                status='disponible',
                price=_price if _price is not None else Decimal('0'),
                currency='MXN',
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                region=selected_region,
                state=request.POST.get('state'),
                zip_code=request.POST.get('zip_code', ''),
                country='México',
                google_maps_url=request.POST.get('google_maps_url', ''),
                latitude=parse_coordinate(request.POST.get('latitude')),
                longitude=parse_coordinate(request.POST.get('longitude')),
                bedrooms=int(request.POST.get('bedrooms') or 0),
                bathrooms=int(request.POST.get('bathrooms') or 0),
                half_bathrooms=int(request.POST.get('half_bathrooms') or 0),
                parking_spaces=int(request.POST.get('parking_spaces') or 0),
                construction_area=construction_area_value,
                lot_area=_to_decimal(request.POST.get('lot_area')),
                front_measure=_to_decimal(request.POST.get('front_measure')),
                back_measure=_to_decimal(request.POST.get('back_measure')),
                floors=int(request.POST.get('floors') or 1),
                year_built=int(request.POST.get('year_built')) if request.POST.get('year_built') else None,
                rooms=int(request.POST.get('rooms') or 0),
                maintenance_fee=_to_decimal(request.POST.get('maintenance_fee')),
                is_featured='is_featured' in request.POST,
                is_new='is_new' in request.POST,
                is_advisor_exclusive=is_advisor_exclusive,
                exclusive_advisor=selected_advisor if is_advisor_exclusive else None,
                financing_options=request.POST.getlist('financing_options'),
                published_at=timezone.now(),
            )
            
            property_obj.save()
            amenity_ids = request.POST.getlist('amenities')
            if amenity_ids:
                property_obj.amenities.set(
                    Amenity.objects.filter(id__in=amenity_ids, is_active=True)
                )
            property_obj.interior_features.set(
                InteriorFeature.objects.filter(id__in=request.POST.getlist('interior_features'), is_active=True)
            )
            property_obj.service_features.set(
                ServiceFeature.objects.filter(id__in=request.POST.getlist('service_features'), is_active=True)
            )
            
            # Guardar imágenes
            images = request.FILES.getlist('images')
            if images:
                for idx, image in enumerate(images):
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image,
                        is_main=(idx == 0),
                        order=idx,
                        alt_text=f"Imagen {idx + 1} de {property_obj.title}"
                    )
                
                if property_obj.is_featured:
                    messages.success(request, f'Propiedad "{property_obj.title}" creada exitosamente y marcada como DESTACADA. Aparecerá en el carrusel principal.')
                else:
                    messages.success(request, f'Propiedad "{property_obj.title}" creada exitosamente con {len(images)} imágenes.')
            else:
                messages.warning(request, f'Propiedad "{property_obj.title}" creada sin imágenes. Puedes agregarlas después.')
            
            return redirect('properties:detail', pk=property_obj.pk)
            
        except (TypeError, ValueError, ValidationError) as e:
            messages.error(request, f'Error de validación al crear la propiedad: {str(e)}')
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al crear propiedad')
            messages.error(request, f'Error de base de datos al crear la propiedad: {str(e)}')
            regions = Region.objects.filter(is_active=True).order_by('order', 'name')
            return render(request, 'properties/add_property.html', {
                'title': 'Agregar Nueva Propiedad',
                'regions': regions,
                'advisors': get_user_model().objects.filter(is_staff=True, is_active=True).order_by('username'),
                'financing_choices': Property.FINANCING_CHOICES,
                'property_types': PropertyType.choices,
                'amenity_catalog': Amenity.objects.filter(is_active=True).select_related('category').order_by('category__sort_order', '-priority_score', 'display_name'),
                'interior_feature_catalog': InteriorFeature.objects.filter(is_active=True).order_by('sort_order', 'name'),
                'service_feature_catalog': ServiceFeature.objects.filter(is_active=True).order_by('sort_order', 'name'),
            })
    
    context = {
        'title': 'Agregar Nueva Propiedad',
        'regions': Region.objects.filter(is_active=True).order_by('order', 'name'),
        'advisors': get_user_model().objects.filter(is_staff=True, is_active=True).order_by('username'),
        'financing_choices': Property.FINANCING_CHOICES,
        'property_types': PropertyType.choices,
        'amenity_catalog': Amenity.objects.filter(is_active=True).select_related('category').order_by('category__sort_order', '-priority_score', 'display_name'),
        'interior_feature_catalog': InteriorFeature.objects.filter(is_active=True).order_by('sort_order', 'name'),
        'service_feature_catalog': ServiceFeature.objects.filter(is_active=True).order_by('sort_order', 'name'),
    }
    
    return render(request, 'properties/add_property.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def edit_property(request, pk):
    """Redirige la edición pública al editor unificado del panel."""
    return redirect('panel:property_edit', pk=pk)



@login_required
@user_passes_test(is_staff_user, login_url='admin:login')
def manage_images(request, pk):
    """Vista para gestionar imágenes de una propiedad"""
    property_obj = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'set_main':
            # Establecer imagen principal
            image_id = request.POST.get('image_id')
            PropertyImage.objects.filter(property=property_obj).update(is_main=False)
            PropertyImage.objects.filter(id=image_id).update(is_main=True)
            messages.success(request, 'Imagen principal actualizada.')
        
        elif action == 'delete':
            # Eliminar imagen
            image_id = request.POST.get('image_id')
            PropertyImage.objects.filter(id=image_id).delete()
            messages.success(request, 'Imagen eliminada.')
        
        elif action == 'upload':
            # Subir nuevas imágenes
            images = request.FILES.getlist('images')
            if images:
                current_count = property_obj.images.count()
                uploaded = 0
                for idx, image in enumerate(images):
                    try:
                        PropertyImage.objects.create(
                            property=property_obj,
                            image=image,
                            is_main=False,
                            order=current_count + idx,
                            alt_text=f"Imagen {current_count + idx + 1} de {property_obj.title}"
                        )
                        uploaded += 1
                    except ValidationError as exc:
                        messages.error(request, f'Imagen rechazada ({image.name}): {exc.messages[0]}')
                if uploaded:
                    messages.success(request, f'{uploaded} imágenes agregadas.')
        
        return redirect('properties:manage_images', pk=pk)
    
    images = property_obj.images.all().order_by('-is_main', 'order')
    
    context = {
        'property': property_obj,
        'images': images,
    }
    
    return render(request, 'properties/manage_images.html', context)



def download_property_pdf(request, pk):
    """PDF de ficha informativa (ReportLab): encabezado repetido en cada página, fotos optimizadas."""
    from django.http import HttpResponse
    from django.conf import settings
    from io import BytesIO
    from PIL import Image
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from xml.sax.saxutils import escape
    import os

    property_obj = get_object_or_404(Property.objects.prefetch_related('images'), pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="TotalLiving_{property_obj.slug}.pdf"'
    styles = getSampleStyleSheet()
    content = []

    dark = colors.HexColor('#13161a')
    muted = colors.HexColor('#5f6671')
    line = colors.HexColor('#d8dde3')

    s_small = ParagraphStyle('s_small', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=muted, leading=12)
    s_title = ParagraphStyle('s_title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=dark, leading=22)
    s_price = ParagraphStyle('s_price', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=15, textColor=dark, alignment=TA_LEFT)
    s_body = ParagraphStyle('s_body', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, textColor=dark, leading=13)
    s_metric = ParagraphStyle('s_metric', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=dark, alignment=TA_CENTER, leading=11)
    s_section = ParagraphStyle('s_section', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=11, textColor=dark, spaceAfter=4, spaceBefore=2)

    def txt(v):
        return escape(str(v or '').strip())

    def break_title_for_pdf(title_text, max_chars=36):
        """Inserta un salto de línea en el espacio más cercano al límite para separar título/precio."""
        t = (title_text or '').strip()
        if len(t) <= max_chars:
            return txt(t)
        split_at = t.rfind(' ', 0, max_chars + 1)
        if split_at < 12:
            split_at = t.find(' ', max_chars)
        if split_at == -1:
            return txt(t)
        left = txt(t[:split_at])
        right = txt(t[split_at + 1:])
        return f'{left}<br/>{right}'

    def img(path, w, h):
        if not path or not os.path.exists(path):
            return None
        try:
            return RLImage(path, width=w, height=h)
        except (OSError, ValueError, TypeError):
            return None

    def load_pil_from_property_image(image_model):
        """Abre la imagen desde disco o almacenamiento de objetos (p. ej. R2)."""
        if not image_model.image:
            return None
        rel = str(image_model.image.name)
        if not rel:
            return None
        abs_path = os.path.join(settings.MEDIA_ROOT, rel)
        try:
            if os.path.exists(abs_path):
                im = Image.open(abs_path)
            else:
                image_model.image.open('rb')
                raw = image_model.image.read()
                image_model.image.close()
                im = Image.open(BytesIO(raw))
            if im.mode != 'RGB':
                im = im.convert('RGB')
            return im
        except (OSError, ValueError, TypeError):
            try:
                image_model.image.close()
            except (AttributeError, OSError, ValueError):
                pass
            return None

    def rl_image_for_pdf(pil_im, max_w_inch, max_h_inch, jpeg_quality=80, decode_max=480):
        """JPEG redimensionado antes de ReportLab: PDF más liviano y scroll más fluido."""
        if pil_im is None:
            return None
        try:
            pil_im = pil_im.copy()
            pil_im.thumbnail((decode_max, decode_max), Image.Resampling.LANCZOS)
            iw, ih = pil_im.size
            if iw < 1 or ih < 1:
                return None
            box_w, box_h = max_w_inch, max_h_inch
            ar = iw / ih
            br = box_w / box_h
            if ar > br:
                disp_w = box_w
                disp_h = box_w / ar
            else:
                disp_h = box_h
                disp_w = box_h * ar
            disp_w_pt = disp_w * 72
            disp_h_pt = disp_h * 72
            buf = BytesIO()
            pil_im.save(buf, format='JPEG', quality=jpeg_quality, optimize=True)
            buf.seek(0)
            return RLImage(buf, width=disp_w_pt, height=disp_h_pt)
        except (OSError, ValueError, TypeError):
            return None

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'SharedScreenshot.png')
    image_objs = list(property_obj.images.all().order_by('-is_main', 'order'))
    first_four = image_objs[:4]
    rest_images = image_objs[4:]
    usable_w = 7.40 * inch
    col4 = usable_w / 4.0

    # Mismo encabezado que antes (barra + tabla logo/contacto), reutilizado en cada página vía drawOn.
    pdf_header_sep = Table([['']], colWidths=[usable_w], rowHeights=[0.03 * inch])
    pdf_header_sep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), line),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    left_logo = img(logo_path, 0.72 * inch, 0.72 * inch) or Paragraph('', s_small)
    contact = Paragraph(
        '<b><font size="13">Total Living</font></b><br/>'
        '<font size="10">Celular: +52 442 866 9965</font><br/>'
        '<font size="10">Oficina: 442 866 9965</font><br/>'
        '<font size="10">totalliving2026@gmail.com</font>',
        s_small,
    )
    pdf_header_block = Table([[left_logo, contact]], colWidths=[0.9 * inch, 6.50 * inch])
    pdf_header_block.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    header_gap = 0.06 * inch
    # Aire arriba + línea + hueco antes de la barra gris (mismo en todas las páginas).
    header_top_pad = 0.16 * inch
    post_line_gap = 0.06 * inch
    _wrap_h_max = 4 * inch
    _, h_sep = pdf_header_sep.wrap(usable_w, _wrap_h_max)
    _, h_hdr = pdf_header_block.wrap(usable_w, _wrap_h_max)
    header_bottom_slack_pt = 4
    pdf_top_margin = header_top_pad + post_line_gap + h_sep + header_gap + h_hdr + header_bottom_slack_pt

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        topMargin=pdf_top_margin,
        bottomMargin=0.32 * inch,
        leftMargin=0.40 * inch,
        rightMargin=0.40 * inch,
    )

    def draw_pdf_page_header(canvas, doc):
        page_w, page_h = doc.pagesize
        lm = doc.leftMargin
        rm = doc.rightMargin
        canvas.saveState()
        y_line = page_h - header_top_pad
        canvas.setStrokeColor(line)
        canvas.setLineWidth(0.85)
        canvas.line(lm, y_line, page_w - rm, y_line)
        y_bar = page_h - header_top_pad - post_line_gap - h_sep
        pdf_header_sep.wrap(usable_w, pdf_top_margin)
        pdf_header_sep.drawOn(canvas, lm, y_bar)
        y_hdr = y_bar - header_gap - h_hdr
        pdf_header_block.wrap(usable_w, pdf_top_margin)
        pdf_header_block.drawOn(canvas, lm, y_hdr)
        canvas.restoreState()

    # Título + precio + operación
    title_row = Table([[
        Paragraph(break_title_for_pdf(property_obj.title).upper(), s_title),
        '',
        Paragraph(f'{txt(property_obj.get_price_display())}<br/><font size="9" color="#6b7280">{txt(property_obj.get_operation_type_display())}</font>', s_price),
    ]], colWidths=[5.35 * inch, 0.12 * inch, 1.93 * inch])
    title_row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('ALIGN', (2, 0), (2, 0), 'LEFT'),
    ]))
    content.append(title_row)
    loc = property_obj.get_location_line_display() or 'Ubicación no especificada'
    content.append(Paragraph(txt(loc), s_small))
    content.append(Spacer(1, 0.06 * inch))

    # Cuatro miniaturas en una fila (menos alto que dos fotos grandes → más espacio para descripción en hoja 1)
    top_row_cells = []
    for i in range(4):
        if i < len(first_four):
            pil = load_pil_from_property_image(first_four[i])
            cell_flow = rl_image_for_pdf(pil, max_w_inch=1.78, max_h_inch=1.05)
        else:
            cell_flow = None
        top_row_cells.append(cell_flow if cell_flow else Paragraph('', s_small))

    photos_top = Table([top_row_cells], colWidths=[col4, col4, col4, col4], rowHeights=[1.12 * inch])
    photos_top.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.35, line),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    content.append(photos_top)
    content.append(Spacer(1, 0.07 * inch))

    # Métricas alineadas y menos saturadas (2 x 3)
    metric_pairs = [
        (property_obj.bedrooms or 0, 'Recámaras'),
        (property_obj.bathrooms or 0, 'Baños'),
        (property_obj.parking_spaces or 0, 'Estacionamientos'),
        (f"{property_obj.construction_area or 'N/A'} m²" if property_obj.construction_area else 'N/A', 'Construcción'),
        (property_obj.floors or 'N/A', 'Niveles'),
        (txt(property_obj.get_property_type_display()), 'Tipo'),
    ]
    metric_cells = []
    for val, lab in metric_pairs:
        metric_cells.append(Paragraph(f'{txt(val)}<br/><font size="8.5" color="#6b7280">{txt(lab)}</font>', s_metric))

    metrics = Table([metric_cells[:3], metric_cells[3:]], colWidths=[usable_w / 3.0] * 3)
    metrics.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.3, line),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    content.append(metrics)
    content.append(Spacer(1, 0.07 * inch))

    # Descripción + Amenidades parejo
    amenities = list(property_obj.amenities.values_list('display_name', flat=True))

    desc = txt((property_obj.description or '').strip()).replace('\n', '<br/>')
    amen = '<br/>'.join([f'• {txt(a)}' for a in amenities]) if amenities else 'Sin amenidades registradas.'
    cols = Table([[
        Paragraph('<b>Descripción</b><br/>' + (desc or 'Sin descripción.'), s_body),
        Paragraph('<b>Amenidades</b><br/>' + amen, s_body),
    ]], colWidths=[4.25 * inch, 3.15 * inch])
    cols.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    content.append(cols)

    if rest_images:
        content.append(Spacer(1, 0.09 * inch))
        content.append(Paragraph('<b>Más fotografías</b>', s_section))
        half_w = usable_w / 2.0
        gallery_rows = []
        for i in range(0, len(rest_images), 2):
            row = []
            for j in range(2):
                idx = i + j
                if idx < len(rest_images):
                    pil = load_pil_from_property_image(rest_images[idx])
                    row.append(
                        rl_image_for_pdf(pil, max_w_inch=3.62, max_h_inch=2.45, decode_max=560)
                        or Paragraph('', s_small)
                    )
                else:
                    row.append(Paragraph('', s_small))
            gallery_rows.append(row)
        gallery = Table(gallery_rows, colWidths=[half_w, half_w])
        gallery.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.35, line),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        content.append(gallery)

    content.append(Spacer(1, 0.08 * inch))
    if property_obj.google_maps_url:
        content.append(Paragraph(f'<b>Mapa:</b> {txt(property_obj.google_maps_url)}', s_small))
    content.append(Paragraph(
        '<font size="8" color="#6b7280">Ficha informativa | Total Living</font>',
        ParagraphStyle('s_footer', parent=s_small, alignment=TA_CENTER)
    ))

    # Importante: no envolver todo en una sola celda de tabla.
    bottom_sep = Table([['']], colWidths=[usable_w], rowHeights=[0.03 * inch])
    bottom_sep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), line),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements = [Spacer(1, 0.04 * inch)] + content + [Spacer(1, 0.06 * inch), bottom_sep]
    doc.build(elements, onFirstPage=draw_pdf_page_header, onLaterPages=draw_pdf_page_header)
    return response


