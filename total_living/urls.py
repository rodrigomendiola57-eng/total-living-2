"""
URL configuration for total_living project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.views.static import serve as static_serve
from django.utils.text import slugify
from django.db.utils import OperationalError, ProgrammingError
from panel.models import HomeContent, NosotrosContent, OrganigramMember
from total_living.health_views import health_live, health_ready


def _normalize_private_path(raw_value: str, default_path: str) -> str:
    """Normaliza rutas privadas para evitar errores de slash."""
    value = (raw_value or '').strip().strip('/')
    fallback = (default_path or '').strip().strip('/') or 'admin'
    return f'{value}/' if value else f'{fallback}/'

# Vista mejorada para la página principal
def home_view(request):
    """Vista mejorada para la página principal con estadísticas"""
    from properties.models import CarouselSlide, Property
    
    # Propiedades destacadas
    featured_properties = Property.objects.filter(
        status='disponible',
        is_featured=True
    ).prefetch_related('images').order_by('-created_at')[:6]
    
    # Últimas propiedades
    latest_properties = Property.objects.filter(
        status='disponible'
    ).prefetch_related('images').order_by('-created_at')[:9]

    # Mapa (solo propiedades con coordenadas registradas)
    map_props = Property.objects.filter(
        status='disponible',
        latitude__isnull=False,
        longitude__isnull=False
    ).only('id', 'title', 'latitude', 'longitude', 'price', 'currency')

    map_markers = []
    for p in map_props:
        map_markers.append({
            'id': p.pk,
            'title': p.title,
            'lat': float(p.latitude),
            'lng': float(p.longitude),
            'url': p.get_absolute_url(),
            'price': p.get_price_display(),
        })
    
    # Estadísticas
    total_properties = Property.objects.filter(status='disponible').count()
    cities_count = Property.objects.filter(status='disponible').values('city').distinct().count()
    
    # Tipos más comunes
    property_types_stats = Property.objects.filter(
        status='disponible'
    ).values('property_type').annotate(
        count=Count('id')
    ).order_by('-count')[:4]
    
    try:
        home_content, _ = HomeContent.objects.get_or_create(
            singleton_key=HomeContent.SINGLETON_DEFAULT,
        )
    except (OperationalError, ProgrammingError):
        home_content = HomeContent()

    manual_slides = CarouselSlide.objects.filter(is_active=True).order_by('order', '-created_at')[:6]
    carousel_items = []
    for s in manual_slides:
        carousel_items.append({'kind': 'slide', 'slide': s})
    for p in featured_properties:
        carousel_items.append({'kind': 'property', 'property': p})

    context = {
        'featured_properties': featured_properties,
        'carousel_items': carousel_items,
        'latest_properties': latest_properties,
        'map_markers': map_markers,
        'total_properties': total_properties,
        'cities_count': cities_count,
        'property_types_stats': property_types_stats,
        'home_content': home_content,
    }
    
    return render(request, 'home.html', context)


def about_view(request):
    """Módulo institucional Nosotros."""
    from django.contrib.staticfiles.storage import staticfiles_storage

    try:
        organigram_directors = list(
            OrganigramMember.objects.filter(
                is_visible=True,
                tier=OrganigramMember.TIER_DIRECTOR,
            ).order_by('sort_order', 'id')
        )
        organigram_managers = list(
            OrganigramMember.objects.filter(
                is_visible=True,
                tier=OrganigramMember.TIER_MANAGER,
            ).order_by('sort_order', 'id')
        )
        organigram_advisors = list(
            OrganigramMember.objects.filter(
                is_visible=True,
                tier=OrganigramMember.TIER_ADVISOR,
            ).order_by('sort_order', 'id')
        )
    except (OperationalError, ProgrammingError):
        organigram_directors = []
        organigram_managers = []
        organigram_advisors = []

    try:
        nosotros_content, _ = NosotrosContent.objects.get_or_create(
            singleton_key=NosotrosContent.SINGLETON_DEFAULT,
        )
    except (OperationalError, ProgrammingError):
        # Evita 500 si todavía no se aplican migraciones del módulo panel.
        nosotros_content = NosotrosContent()

    if getattr(settings, 'NOSOTROS_HERO_VIDEO_URL', ''):
        nosotros_hero_video_url = settings.NOSOTROS_HERO_VIDEO_URL
    else:
        nosotros_hero_video_url = staticfiles_storage.url('videos/nosotros-hero.mp4')

    context = {
        'organigram_directors': organigram_directors,
        'organigram_managers': organigram_managers,
        'organigram_advisors': organigram_advisors,
        'nosotros_content': nosotros_content,
        'nosotros_hero_video_url': nosotros_hero_video_url,
    }
    return render(request, 'nosotros.html', context)


def team_member_detail_view(request, slug):
    """Perfil detallado de miembro del equipo."""
    User = get_user_model()
    normalized_slug = slugify(slug or '')

    try:
        om = OrganigramMember.objects.filter(slug=normalized_slug, is_visible=True).first()
    except (OperationalError, ProgrammingError):
        om = None

    if om:
        expertise = [x for x in [om.expertise_1, om.expertise_2, om.expertise_3] if (x or '').strip()]
        if not expertise:
            expertise = [
                'Prospección y acompañamiento comercial',
                'Seguimiento y negociación',
                'Cierre con enfoque en resultados',
            ]
        profile = {
            'full_name': om.full_name,
            'role': om.role_label,
            'tag': (om.tag_label or '').strip() or 'Total Living',
            'bio': om.bio,
            'expertise': expertise,
            'email': (om.email or '').strip() or None,
            'whatsapp': (om.url_whatsapp or '').strip() or None,
            'instagram': (om.url_instagram or '').strip() or None,
            'facebook': (om.url_facebook or '').strip() or None,
            'linkedin': (om.url_linkedin or '').strip() or None,
            'tiktok': (om.url_tiktok or '').strip() or None,
            'x_url': (om.url_x or '').strip() or None,
            'photo_url': om.photo.url if om.photo else None,
        }
        return render(request, 'team_member_detail.html', {'profile': profile})

    static_profiles = {
        'alfredo-mendiola': {
            'full_name': 'Alfredo Mendiola',
            'role': 'Director General',
            'tag': 'Dirección estratégica',
            'bio': 'Lidera la visión de Total Living, define estándares de servicio y asegura que cada unidad comercial opere con procesos medibles y enfoque en resultados.',
            'expertise': [
                'Estrategia comercial y posicionamiento',
                'Estandarización de procesos',
                'Dirección de equipos de alto desempeño',
            ],
            'email': 'contacto@totalliving.com',
            'whatsapp': None,
            'instagram': 'https://www.instagram.com/total.living.mx/',
            'facebook': 'https://www.facebook.com/total.living.mx?locale=es_LA',
            'linkedin': None,
            'tiktok': None,
            'x_url': None,
            'photo_url': None,
        },
        'patricia-chavarria': {
            'full_name': 'Patricia Chavarría',
            'role': 'Gerente Comercial',
            'tag': 'Ventas y captación',
            'bio': 'Coordina el frente comercial, estructura estrategias de captación y supervisa la correcta ejecución de cada operación activa.',
            'expertise': [
                'Gestión de cartera activa',
                'Seguimiento comercial y cierres',
                'Estrategias de captación',
            ],
            'email': 'contacto@totalliving.com',
            'whatsapp': 'https://api.whatsapp.com/send?phone=4428669965',
            'instagram': None,
            'facebook': None,
            'linkedin': None,
            'tiktok': None,
            'x_url': None,
            'photo_url': None,
        },
    }

    if normalized_slug in static_profiles:
        profile = static_profiles[normalized_slug]
    else:
        team_members = User.objects.filter(is_staff=True, is_active=True)
        selected_member = None
        for member in team_members:
            full_name = f"{member.first_name} {member.last_name}".strip() or member.username
            member_slug = slugify(full_name) or slugify(member.username)
            if member_slug == normalized_slug:
                selected_member = member
                break

        if not selected_member:
            return render(request, 'team_member_detail.html', {'profile': None}, status=404)

        photo_field = getattr(selected_member, 'profile_photo', None)
        profile = {
            'full_name': (f"{selected_member.first_name} {selected_member.last_name}".strip() or selected_member.username),
            'role': 'Asesor Inmobiliario',
            'tag': 'Compra, venta y renta',
            'bio': 'Acompaña al cliente en valuación, prospección y cierre, con foco en tiempos de respuesta y calidad de seguimiento.',
            'expertise': [
                'Prospección y filtrado de oportunidades',
                'Acompañamiento operativo de inicio a cierre',
                'Negociación y seguimiento comercial',
            ],
            'email': selected_member.email or 'contacto@totalliving.com',
            'whatsapp': None,
            'instagram': None,
            'facebook': None,
            'linkedin': None,
            'tiktok': None,
            'x_url': None,
            'photo_url': getattr(photo_field, 'url', None) if photo_field else None,
        }

    return render(request, 'team_member_detail.html', {'profile': profile})

# URL patterns
urlpatterns = [
    path('health/live/', health_live, name='health_live'),
    path('health/ready/', health_ready, name='health_ready'),
    path(_normalize_private_path(settings.ADMIN_URL_PATH, 'admin'), admin.site.urls),
    path('', home_view, name='home'),
    path('nosotros/', about_view, name='about'),
    path('nosotros/equipo/<slug:slug>/', team_member_detail_view, name='team_member_detail'),
]

# Agregar más URLs
urlpatterns.append(path('properties/', include('properties.urls')))
urlpatterns.append(path('contact/', include('contact.urls')))
urlpatterns.append(path('search/', include('search.urls')))
urlpatterns.append(path('accounts/', include('accounts.urls')))
urlpatterns.append(path(_normalize_private_path(settings.PANEL_URL_PATH, 'panel'), include('panel.urls')))
urlpatterns.append(path('desarrollos/', include('developments.urls')))
urlpatterns.append(path('regiones/', include('regions.urls')))
urlpatterns.append(path('i18n/', include('django.conf.urls.i18n')))

# Servir MEDIA en desarrollo o en predeploy local (Docker) cuando se habilite.
if settings.DEBUG or getattr(settings, 'SERVE_LOCAL_MEDIA', False):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# STATIC solo en DEBUG; en producción lo sirve WhiteNoise (o R2 si USE_S3_STATIC).
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
