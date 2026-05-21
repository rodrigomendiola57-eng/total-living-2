from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from properties.models import Property, PropertyType, PropertyOperation
from properties.money import parse_decimal_value
from regions.models import Region


def search_view(request):
    """Vista para búsqueda avanzada de propiedades"""
    properties = Property.objects.filter(status='disponible').prefetch_related('images')
    
    # Búsqueda por texto
    query = request.GET.get('q', '').strip()
    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query)
        )
    
    # Filtros
    property_type = request.GET.get('property_type', '')
    operation_type = request.GET.get('operation_type', '')
    city = request.GET.get('city', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_bedrooms = request.GET.get('min_bedrooms', '')
    min_bathrooms = request.GET.get('min_bathrooms', '')
    min_area = request.GET.get('min_area', '') or request.GET.get('area_min', '')
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    if operation_type:
        properties = properties.filter(operation_type=operation_type)
    if city:
        properties = properties.filter(city__icontains=city)
    if min_price:
        parsed_min_price = parse_decimal_value(min_price)
        if parsed_min_price is not None:
            properties = properties.filter(price__gte=parsed_min_price)
    if max_price:
        parsed_max_price = parse_decimal_value(max_price)
        if parsed_max_price is not None:
            properties = properties.filter(price__lte=parsed_max_price)
    if min_bedrooms:
        try:
            properties = properties.filter(bedrooms__gte=int(min_bedrooms))
        except ValueError:
            pass
    if min_bathrooms:
        try:
            properties = properties.filter(bathrooms__gte=int(min_bathrooms))
        except ValueError:
            pass
    if min_area:
        parsed_min_area = parse_decimal_value(min_area)
        if parsed_min_area is not None:
            properties = properties.filter(construction_area__gte=parsed_min_area)
    
    # Ordenamiento
    order_alias = {
        'reciente': '-created_at',
        'precio_menor': 'price',
        'precio_mayor': '-price',
        'area_menor': 'construction_area',
        'area_mayor': '-construction_area',
    }
    order_by = request.GET.get('order_by') or request.GET.get('orden', '-created_at')
    order_by = order_alias.get(order_by, order_by)
    if order_by in ['price', '-price', 'created_at', '-created_at', 'construction_area', '-construction_area']:
        properties = properties.order_by(order_by)
    else:
        properties = properties.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener opciones para filtros
    property_types = PropertyType.choices
    operation_types = PropertyOperation.choices
    
    # Obtener ciudades únicas para el autocompletado
    cities = Property.objects.values_list('city', flat=True).distinct().order_by('city')
    
    context = {
        'properties': page_obj,
        'property_types': property_types,
        'operation_types': operation_types,
        'cities': cities,
        'current_filters': {
            'q': query,
            'property_type': property_type,
            'operation_type': operation_type,
            'city': city,
            'min_price': min_price,
            'max_price': max_price,
            'min_bedrooms': min_bedrooms,
            'min_bathrooms': min_bathrooms,
            'min_area': min_area,
            'order_by': order_by,
        },
        'total_results': page_obj.paginator.count,
    }
    
    return render(request, 'search/search.html', context)


def api_cities(request):
    """API para obtener estados de México con autocompletado"""
    query = request.GET.get('q', '').strip().lower()
    
    # Lista completa de estados de México
    estados_mexico = [
        'Aguascalientes',
        'Baja California',
        'Baja California Sur',
        'Campeche',
        'Chiapas',
        'Chihuahua',
        'Ciudad de México',
        'Coahuila',
        'Colima',
        'Durango',
        'Estado de México',
        'Guanajuato',
        'Guerrero',
        'Hidalgo',
        'Jalisco',
        'Michoacán',
        'Morelos',
        'Nayarit',
        'Nuevo León',
        'Oaxaca',
        'Puebla',
        'Querétaro',
        'Quintana Roo',
        'San Luis Potosí',
        'Sinaloa',
        'Sonora',
        'Tabasco',
        'Tamaulipas',
        'Tlaxcala',
        'Veracruz',
        'Yucatán',
        'Zacatecas'
    ]
    
    # También obtener estados únicos de la base de datos
    db_states = list(Property.objects.values_list('state', flat=True).distinct().order_by('state'))
    
    # Combinar y eliminar duplicados
    all_states = list(set(estados_mexico + db_states))
    all_states.sort()
    
    # Filtrar por query si existe
    if query:
        filtered = [s for s in all_states if query in s.lower()]
        return JsonResponse({
            'cities': filtered[:20]  # Mantener nombre 'cities' para compatibilidad con JS
        })
    
    return JsonResponse({
        'cities': all_states[:32]  # Todos los estados
    })


def api_regions_by_city(request):
    """API para obtener regiones/delegaciones según el estado"""
    state = request.GET.get('city', '').strip().lower()  # Mantener 'city' para compatibilidad con JS
    
    # Definir regiones por estado
    regions_data = {
        'querétaro': [
            'Centro Histórico',
            'Juriquilla',
            'El Campanario',
            'Zibata',
            'La Pradera',
            'Corregidora',
            'San Ángel',
            'Vista Real',
            'Paseo del Álamo',
            'La Estancia',
            'El Refugio',
            'Hacienda Santa Rosa',
            'Lomas del Campanario',
            'Villas del Mesón',
            'Paseo de los Olivos'
        ],
        'ciudad de méxico': [
            'Álvaro Obregón',
            'Azcapotzalco',
            'Benito Juárez',
            'Coyoacán',
            'Cuajimalpa',
            'Cuauhtémoc',
            'Gustavo A. Madero',
            'Iztacalco',
            'Iztapalapa',
            'Magdalena Contreras',
            'Miguel Hidalgo',
            'Milpa Alta',
            'Tláhuac',
            'Tlalpan',
            'Venustiano Carranza',
            'Xochimilco'
        ],
        'cdmx': [
            'Álvaro Obregón',
            'Azcapotzalco',
            'Benito Juárez',
            'Coyoacán',
            'Cuajimalpa',
            'Cuauhtémoc',
            'Gustavo A. Madero',
            'Iztacalco',
            'Iztapalapa',
            'Magdalena Contreras',
            'Miguel Hidalgo',
            'Milpa Alta',
            'Tláhuac',
            'Tlalpan',
            'Venustiano Carranza',
            'Xochimilco'
        ],
        'estado de méxico': [
            'Toluca',
            'Naucalpan',
            'Ecatepec',
            'Nezahualcóyotl',
            'Tlalnepantla',
            'Atizapán',
            'Cuautitlán',
            'Chimalhuacán',
            'Ixtapaluca',
            'Nicolás Romero',
            'Coacalco',
            'Chalco',
            'Valle de Chalco',
            'Texcoco',
            'Huehuetoca',
            'Zumpango'
        ],
        'jalisco': [
            'Guadalajara',
            'Zapopan',
            'Tlaquepaque',
            'Tonalá',
            'Puerto Vallarta',
            'Tepatitlán',
            'Lagos de Moreno',
            'Ocotlán',
            'Ciudad Guzmán',
            'San Juan de los Lagos'
        ],
        'nuevo león': [
            'Monterrey',
            'San Pedro Garza García',
            'Guadalupe',
            'Apodaca',
            'San Nicolás de los Garza',
            'Santa Catarina',
            'Escobedo',
            'García',
            'Juárez',
            'San Nicolás'
        ],
        'puebla': [
            'Puebla',
            'Cholula',
            'San Andrés Cholula',
            'San Pedro Cholula',
            'Atlixco',
            'Tehuacán',
            'Zacatlán',
            'Huauchinango',
            'San Martín Texmelucan',
            'Cuautlancingo'
        ],
        'yucatán': [
            'Mérida',
            'Valladolid',
            'Progreso',
            'Tizimín',
            'Motul',
            'Oxkutzcab',
            'Tekax',
            'Peto',
            'Izamal',
            'Dzidzantún'
        ],
        'quintana roo': [
            'Cancún',
            'Playa del Carmen',
            'Chetumal',
            'Cozumel',
            'Tulum',
            'Puerto Morelos',
            'Felipe Carrillo Puerto',
            'Bacalar',
            'Isla Mujeres',
            'Mahahual'
        ]
    }
    
    # Buscar regiones en la base de datos primero
    db_regions = []
    if state:
        # Buscar regiones que coincidan con el estado
        db_regions = list(Region.objects.filter(
            is_active=True
        ).values_list('name', flat=True).order_by('name'))
    
    # Combinar con regiones predefinidas
    predefined_regions = regions_data.get(state, [])
    
    # Si hay regiones en la BD, usarlas; si no, usar las predefinidas
    if db_regions:
        all_regions = list(set(db_regions + predefined_regions))
    else:
        all_regions = predefined_regions
    
    return JsonResponse({
        'regions': sorted(all_regions)
    })
