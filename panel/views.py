import logging
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from .login_ratelimit import panel_login_is_limited
from django.core.paginator import Paginator
from django.db.models import Case, Count, IntegerField, Q, When
from properties.models import Amenity, CarouselSlide, InteriorFeature, Property, PropertyImage, PropertyType, ServiceFeature
from properties.money import parse_coordinate, parse_decimal_value, parse_mx_money
from regions.models import Region
from contact.models import Contact, ContactNote

# Filtro de origen en buzón (alineado con contact.views y desarrollos)
INBOX_SOURCE_FILTER_CHOICES = [
    ('', 'Todos los orígenes'),
    ('sitio_web', 'Formulario contacto (general)'),
    ('sitio_web_propiedad', 'Formulario contacto (propiedad)'),
    ('asesoria_compra', 'Asesoría compra'),
    ('asesoria_venta', 'Asesoría venta'),
    ('quiz_desarrollos', 'Quiz desarrollos'),
]
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.utils import OperationalError, ProgrammingError
from django.core.exceptions import ValidationError
from .models import HomeContent, NosotrosContent, OrganigramMember
from .forms import NosotrosContentForm, OrganigramMemberForm

logger = logging.getLogger(__name__)


def _redirect_if_organigram_table_missing(request):
    """Evita 500 si no se ha ejecutado migrate (tabla panel_organigrammember)."""
    try:
        OrganigramMember.objects.exists()
    except (OperationalError, ProgrammingError):
        messages.error(
            request,
            'Falta crear la tabla del organigrama. En la carpeta del proyecto ejecuta: python manage.py migrate',
        )
        return redirect('panel:nosotros_edit')
    return None


def require_organigram_table(view_func):
    """Evita repetir la comprobación de migración en cada vista del organigrama."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        resp = _redirect_if_organigram_table_missing(request)
        if resp is not None:
            return resp
        return view_func(request, *args, **kwargs)
    return _wrapped


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def panel_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel:dashboard')
    
    if request.method == 'POST':
        if panel_login_is_limited(request):
            messages.error(
                request,
                'Demasiados intentos de inicio de sesión. Espera unos minutos e inténtalo de nuevo.',
            )
            return render(request, 'panel/login.html')

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('panel:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos, o no tienes permisos de acceso.')
    
    return render(request, 'panel/login.html')


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_logout(request):
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('panel:login')


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def dashboard(request):
    total_properties = Property.objects.count()
    disponibles = Property.objects.filter(status='disponible').count()
    vendidas = Property.objects.filter(status='vendida').count()
    rentadas = Property.objects.filter(status='rentada').count()
    destacadas = Property.objects.filter(is_featured=True).count()
    
    recent_properties = Property.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_properties': total_properties,
        'disponibles': disponibles,
        'vendidas': vendidas,
        'rentadas': rentadas,
        'destacadas': destacadas,
        'recent_properties': recent_properties,
    }
    
    return render(request, 'panel/dashboard.html', context)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_home_edit(request):
    """CMS de secciones estratégicas del Inicio público."""
    content, _ = HomeContent.objects.get_or_create(singleton_key=HomeContent.SINGLETON_DEFAULT)

    if request.method == 'POST':
        editable_fields = [
            'about_eyebrow', 'about_title', 'about_paragraph_1', 'about_paragraph_2',
            'about_cta_text', 'about_cta_url',
            'why_title', 'why_subtitle',
            'why_1_icon', 'why_1_title', 'why_1_text', 'why_1_bullet_1', 'why_1_bullet_2', 'why_1_bullet_3', 'why_1_bullet_4',
            'why_2_icon', 'why_2_title', 'why_2_text', 'why_2_bullet_1', 'why_2_bullet_2', 'why_2_bullet_3', 'why_2_bullet_4',
            'why_3_icon', 'why_3_title', 'why_3_text', 'why_3_bullet_1', 'why_3_bullet_2', 'why_3_bullet_3', 'why_3_bullet_4',
            'why_4_icon', 'why_4_title', 'why_4_text', 'why_4_bullet_1', 'why_4_bullet_2', 'why_4_bullet_3', 'why_4_bullet_4',
            'services_title', 'services_subtitle',
            'service_1_icon', 'service_1_title', 'service_1_text', 'service_1_b1', 'service_1_b2', 'service_1_b3',
            'service_2_icon', 'service_2_title', 'service_2_text', 'service_2_b1', 'service_2_b2', 'service_2_b3',
            'service_3_icon', 'service_3_title', 'service_3_text', 'service_3_b1', 'service_3_b2', 'service_3_b3',
        ]
        for field in editable_fields:
            setattr(content, field, (request.POST.get(field) or '').strip())
        if 'about_image' in request.FILES:
            content.about_image = request.FILES['about_image']
        content.save()
        messages.success(request, 'Inicio CMS actualizado correctamente.')
        return redirect('panel:home_edit')

    return render(request, 'panel/home_edit.html', {'content': content})


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_nosotros_edit(request):
    try:
        content, _ = NosotrosContent.objects.get_or_create(singleton_key=NosotrosContent.SINGLETON_DEFAULT)
    except (OperationalError, ProgrammingError):
        messages.error(
            request,
            'Falta aplicar migraciones del módulo Nosotros. Ejecuta: python manage.py migrate',
        )
        return redirect('panel:dashboard')

    if request.method == 'POST':
        form = NosotrosContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Los textos configurables de la página Nosotros se guardaron correctamente.')
            return redirect('panel:nosotros_edit')
        messages.error(request, 'Revisa los errores del formulario antes de guardar.')
    else:
        form = NosotrosContentForm(instance=content)

    return render(request, 'panel/nosotros_edit.html', {'form': form})


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
@require_organigram_table
def panel_organigram_list(request):
    members = OrganigramMember.objects.annotate(
        tier_rank=Case(
            When(tier=OrganigramMember.TIER_DIRECTOR, then=0),
            When(tier=OrganigramMember.TIER_MANAGER, then=1),
            When(tier=OrganigramMember.TIER_ADVISOR, then=2),
            default=3,
            output_field=IntegerField(),
        ),
    ).order_by('tier_rank', 'sort_order', 'id')
    return render(request, 'panel/organigram_list.html', {'members': members})


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
@require_organigram_table
def panel_organigram_add(request):
    if request.method == 'POST':
        form = OrganigramMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ficha del organigrama creada correctamente.')
            return redirect('panel:organigram_list')
    else:
        form = OrganigramMemberForm()
    return render(request, 'panel/organigram_form.html', {'form': form, 'member': None})


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
@require_organigram_table
def panel_organigram_edit(request, pk):
    member = get_object_or_404(OrganigramMember, pk=pk)
    if request.method == 'POST':
        form = OrganigramMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ficha actualizada correctamente.')
            return redirect('panel:organigram_list')
    else:
        form = OrganigramMemberForm(instance=member)
    return render(request, 'panel/organigram_form.html', {'form': form, 'member': member})


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
@require_organigram_table
def panel_organigram_delete(request, pk):
    member = get_object_or_404(OrganigramMember, pk=pk)
    if request.method == 'POST':
        name = member.full_name
        member.delete()
        messages.success(request, f'Se eliminó la ficha de {name}.')
        return redirect('panel:organigram_list')
    return render(request, 'panel/organigram_delete.html', {'member': member})


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_legacy_organigram_edit_redirect(request, pk):
    return redirect('panel:organigram_edit', pk=pk)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_legacy_organigram_delete_redirect(request, pk):
    return redirect('panel:organigram_delete', pk=pk)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_properties(request):
    properties = Property.objects.all().order_by('-created_at')
    
    # Filtros
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    property_type = request.GET.get('tipo', '')
    process = request.GET.get('process', '')
    
    if search:
        properties = properties.filter(
            Q(title__icontains=search) | 
            Q(city__icontains=search) | 
            Q(address__icontains=search)
        )
    if status:
        properties = properties.filter(status=status)
    if property_type:
        properties = properties.filter(property_type=property_type)
    if process:
        properties = properties.filter(process=process)
    
    paginator = Paginator(properties, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'search': search,
        'status_filter': status,
        'type_filter': property_type,
        'process_filter': process,
        'property_types': PropertyType.choices,
    }
    
    return render(request, 'panel/properties.html', context)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_property_edit(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        try:
            def parse_decimal_field(raw_value, current_value):
                """
                Convierte strings numéricos (m², medidas) conservando el valor actual si viene vacío o inválido.
                No usar para precio: ahí se usa parse_mx_money.
                """
                if raw_value is None:
                    return current_value

                value = str(raw_value).strip()
                if value == '':
                    return current_value

                # "1,234.56" US: quitar comas de miles
                if ',' in value and '.' in value:
                    value = value.replace(',', '')
                elif ',' in value and '.' not in value:
                    # Una coma + 1–2 decimales → coma decimal (ej. 185,50)
                    if value.count(',') == 1:
                        a, b = value.split(',')
                        if len(b) <= 2 and b.isdigit():
                            value = a + '.' + b
                        else:
                            value = value.replace(',', '')
                    else:
                        # Varias comas → miles (2,170,000)
                        value = value.replace(',', '')
                parsed = parse_decimal_value(value)
                if parsed is None:
                    return current_value
                return parsed

            property_obj.title = request.POST.get('title')
            property_obj.description = request.POST.get('description')
            property_obj.property_type = request.POST.get('property_type')
            property_obj.operation_type = request.POST.get('operation_type')
            property_obj.status = request.POST.get('status')
            property_obj.process = request.POST.get('process', 'en_busqueda')

            raw_price = request.POST.get('price')
            parsed_price = parse_mx_money(raw_price)
            if parsed_price is not None:
                property_obj.price = parsed_price

            property_obj.currency = request.POST.get('currency', 'MXN')
            property_obj.address = request.POST.get('address')
            property_obj.city = request.POST.get('city')
            region_id = request.POST.get('region')
            property_obj.region = Region.objects.filter(pk=region_id, is_active=True).first() if region_id else None
            property_obj.state = request.POST.get('state')
            property_obj.zip_code = request.POST.get('zip_code', '')
            property_obj.country = request.POST.get('country', 'México')
            property_obj.google_maps_url = request.POST.get('google_maps_url', '')
            # Coordenadas
            latitude = request.POST.get('latitude')
            property_obj.latitude = parse_coordinate(latitude)
            longitude = request.POST.get('longitude')
            property_obj.longitude = parse_coordinate(longitude)
            property_obj.bedrooms = int(request.POST.get('bedrooms') or 0)
            property_obj.bathrooms = int(request.POST.get('bathrooms') or 0)
            property_obj.half_bathrooms = int(request.POST.get('half_bathrooms') or 0)
            property_obj.parking_spaces = int(request.POST.get('parking_spaces') or 0)
            # Áreas
            construction_area_raw = request.POST.get('construction_area')
            construction_area_value = parse_decimal_value(construction_area_raw)
            if construction_area_value is None:
                raise ValueError('El campo "Área Construcción (m²)" es obligatorio.')
            property_obj.construction_area = construction_area_value
            property_obj.lot_area = parse_decimal_field(request.POST.get('lot_area'), property_obj.lot_area)
            property_obj.front_measure = parse_decimal_field(request.POST.get('front_measure'), property_obj.front_measure)
            property_obj.back_measure = parse_decimal_field(request.POST.get('back_measure'), property_obj.back_measure)
            property_obj.floors = int(request.POST.get('floors') or 1)
            property_obj.year_built = int(request.POST.get('year_built')) if request.POST.get('year_built') else None
            property_obj.rooms = int(request.POST.get('rooms') or 0)
            property_obj.maintenance_fee = parse_decimal_field(request.POST.get('maintenance_fee'), property_obj.maintenance_fee)
            property_obj.is_featured = 'is_featured' in request.POST
            property_obj.is_new = 'is_new' in request.POST
            property_obj.is_advisor_exclusive = 'is_advisor_exclusive' in request.POST
            exclusive_advisor_id = request.POST.get('exclusive_advisor')
            selected_advisor = get_user_model().objects.filter(
                pk=exclusive_advisor_id,
                is_staff=True,
                is_active=True
            ).first() if exclusive_advisor_id else None
            property_obj.exclusive_advisor = selected_advisor if property_obj.is_advisor_exclusive else None
            property_obj.financing_options = request.POST.getlist('financing_options')
            
            property_obj.save()
            amenity_ids = request.POST.getlist('amenities')
            property_obj.amenities.set(Amenity.objects.filter(id__in=amenity_ids, is_active=True))
            property_obj.interior_features.set(
                InteriorFeature.objects.filter(id__in=request.POST.getlist('interior_features'), is_active=True)
            )
            property_obj.service_features.set(
                ServiceFeature.objects.filter(id__in=request.POST.getlist('service_features'), is_active=True)
            )
            
            messages.success(request, f'Propiedad "{property_obj.title}" actualizada exitosamente.')
            return redirect('panel:properties')
            
        except (TypeError, ValueError, ValidationError) as e:
            messages.error(request, f'Error de validación al actualizar la propiedad: {str(e)}')
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al actualizar propiedad %s', pk)
            messages.error(request, f'Error de base de datos al actualizar la propiedad: {str(e)}')
    
    context = {
        'property': property_obj,
        'regions': Region.objects.filter(is_active=True).order_by('order', 'name'),
        'advisors': get_user_model().objects.filter(is_staff=True, is_active=True).order_by('username'),
        'financing_choices': Property.FINANCING_CHOICES,
        'property_types': PropertyType.choices,
        'amenity_catalog': Amenity.objects.filter(is_active=True).select_related('category').order_by('category__sort_order', '-priority_score', 'display_name'),
        'interior_feature_catalog': InteriorFeature.objects.filter(is_active=True).order_by('sort_order', 'name'),
        'service_feature_catalog': ServiceFeature.objects.filter(is_active=True).order_by('sort_order', 'name'),
    }
    
    return render(request, 'panel/property_edit.html', context)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_property_delete(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        title = property_obj.title
        property_obj.delete()
        messages.success(request, f'Propiedad "{title}" eliminada exitosamente.')
        return redirect('panel:properties')
    
    context = {
        'property': property_obj,
    }
    
    return render(request, 'panel/property_delete.html', context)


# ========== GESTIÓN DEL CARRUSEL ==========

@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_carousel_list(request):
    """Lista de slides del carrusel"""
    slides = CarouselSlide.objects.all().order_by('order', '-created_at')
    
    context = {
        'slides': slides,
    }
    
    return render(request, 'panel/carousel_list.html', context)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_carousel_add(request):
    """Agregar nuevo slide al carrusel"""
    if request.method == 'POST':
        try:
            slide = CarouselSlide()
            slide.title = request.POST.get('title')
            slide.subtitle = request.POST.get('subtitle', '')
            slide.link_url = request.POST.get('link_url', '')
            slide.link_text = request.POST.get('link_text', 'Ver Más')
            slide.is_active = 'is_active' in request.POST
            slide.order = int(request.POST.get('order', 0))
            
            if 'image' in request.FILES:
                slide.image = request.FILES['image']
            
            slide.save()
            
            messages.success(request, f'Slide "{slide.title}" agregado exitosamente.')
            return redirect('panel:carousel_list')
            
        except (TypeError, ValueError, ValidationError) as e:
            messages.error(request, f'Error de validación al agregar el slide: {str(e)}')
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al crear slide de carrusel')
            messages.error(request, f'Error de base de datos al agregar el slide: {str(e)}')
    
    return render(request, 'panel/carousel_add.html')


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_carousel_edit(request, pk):
    """Editar slide del carrusel"""
    slide = get_object_or_404(CarouselSlide, pk=pk)
    
    if request.method == 'POST':
        try:
            slide.title = request.POST.get('title')
            slide.subtitle = request.POST.get('subtitle', '')
            slide.link_url = request.POST.get('link_url', '')
            slide.link_text = request.POST.get('link_text', 'Ver Más')
            slide.is_active = 'is_active' in request.POST
            slide.order = int(request.POST.get('order', 0))
            
            if 'image' in request.FILES:
                slide.image = request.FILES['image']
            
            slide.save()
            
            messages.success(request, f'Slide "{slide.title}" actualizado exitosamente.')
            return redirect('panel:carousel_list')
            
        except (TypeError, ValueError, ValidationError) as e:
            messages.error(request, f'Error de validación al actualizar el slide: {str(e)}')
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al editar slide %s', pk)
            messages.error(request, f'Error de base de datos al actualizar el slide: {str(e)}')
    
    context = {
        'slide': slide,
    }
    
    return render(request, 'panel/carousel_edit.html', context)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_carousel_delete(request, pk):
    """Eliminar slide del carrusel"""
    slide = get_object_or_404(CarouselSlide, pk=pk)
    
    if request.method == 'POST':
        title = slide.title
        slide.delete()
        messages.success(request, f'Slide "{title}" eliminado exitosamente.')
        return redirect('panel:carousel_list')
    
    context = {
        'slide': slide,
    }
    
    return render(request, 'panel/carousel_delete.html', context)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_inbox(request):
    """Buzon interno de solicitudes de informacion."""
    contacts = Contact.objects.select_related('property', 'assigned_to').order_by('-created_at')
    staff_users = get_user_model().objects.filter(is_staff=True, is_active=True).order_by('username')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    priority = request.GET.get('priority', '').strip()
    assigned_to = request.GET.get('assigned_to', '').strip()
    mine = request.GET.get('mine', '').strip()
    overdue = request.GET.get('overdue', '').strip()
    source_filter = request.GET.get('source', '').strip()

    if request.method == 'POST':
        action = request.POST.get('bulk_action', '').strip()
        selected_ids = request.POST.getlist('selected_contacts')
        selected_qs = Contact.objects.filter(pk__in=selected_ids)

        if not selected_ids:
            messages.warning(request, 'Selecciona al menos una solicitud para aplicar accion masiva.')
            return redirect('panel:inbox')

        if action == 'mark_read':
            updated = selected_qs.update(is_read=True)
            messages.success(request, f'{updated} solicitudes marcadas como leidas.')
        elif action == 'mark_in_progress':
            updated = selected_qs.update(is_read=True, is_responded=False, status=Contact.STATUS_IN_PROGRESS)
            messages.success(request, f'{updated} solicitudes marcadas en seguimiento.')
        elif action == 'mark_responded':
            updated = selected_qs.update(
                is_read=True,
                is_responded=True,
                status=Contact.STATUS_RESPONDED,
                responded_at=timezone.now()
            )
            messages.success(request, f'{updated} solicitudes marcadas como respondidas.')
        elif action == 'mark_closed':
            updated = selected_qs.update(status=Contact.STATUS_CLOSED)
            messages.success(request, f'{updated} solicitudes cerradas.')
        elif action == 'assign_to_me':
            updated = selected_qs.update(assigned_to=request.user)
            messages.success(request, f'{updated} solicitudes asignadas a tu usuario.')
        else:
            messages.warning(request, 'Accion masiva no valida.')

        return redirect('panel:inbox')

    if search:
        contacts = contacts.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(subject__icontains=search) |
            Q(message__icontains=search) |
            Q(property__title__icontains=search)
        )

    if status:
        contacts = contacts.filter(status=status)

    if priority:
        contacts = contacts.filter(priority=priority)

    if assigned_to == 'none':
        contacts = contacts.filter(assigned_to__isnull=True)
    elif assigned_to:
        contacts = contacts.filter(assigned_to_id=assigned_to)

    if mine == '1':
        contacts = contacts.filter(assigned_to=request.user)

    if overdue == '1':
        contacts = contacts.filter(
            follow_up_at__isnull=False,
            follow_up_at__lt=timezone.now()
        ).exclude(status__in=[Contact.STATUS_RESPONDED, Contact.STATUS_CLOSED])

    allowed_sources = {v for v, _ in INBOX_SOURCE_FILTER_CHOICES if v}
    if source_filter and source_filter in allowed_sources:
        contacts = contacts.filter(source=source_filter)

    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    base_qs = Contact.objects.all()
    context = {
        'contacts': page_obj,
        'search': search,
        'status_filter': status,
        'priority_filter': priority,
        'assigned_to_filter': assigned_to,
        'mine_filter': mine,
        'overdue_filter': overdue,
        'source_filter': source_filter,
        'source_choices': INBOX_SOURCE_FILTER_CHOICES,
        'staff_users': staff_users,
        'status_choices': Contact.STATUS_CHOICES,
        'priority_choices': Contact.PRIORITY_CHOICES,
        'counts': {
            'total': base_qs.count(),
            'new': base_qs.filter(status=Contact.STATUS_NEW).count(),
            'in_progress': base_qs.filter(status=Contact.STATUS_IN_PROGRESS).count(),
            'responded': base_qs.filter(status=Contact.STATUS_RESPONDED).count(),
            'closed': base_qs.filter(status=Contact.STATUS_CLOSED).count(),
            'overdue': base_qs.filter(
                follow_up_at__isnull=False,
                follow_up_at__lt=timezone.now()
            ).exclude(status__in=[Contact.STATUS_RESPONDED, Contact.STATUS_CLOSED]).count(),
        },
    }
    return render(request, 'panel/inbox.html', context)


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_inbox_delete(request, pk):
    """Elimina definitivamente una solicitud del buzón (incluye notas internas en cascada)."""
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        deleted_pk = contact.pk
        contact.delete()
        messages.success(request, f'Solicitud #{deleted_pk} eliminada del buzón.')
        return redirect('panel:inbox')
    return render(request, 'panel/inbox_delete.html', {'contact': contact})


@login_required(login_url='panel:login')
@user_passes_test(is_staff_user, login_url='panel:login')
def panel_inbox_detail(request, pk):
    """Detalle y gestion de una solicitud del buzon."""
    contact = get_object_or_404(Contact.objects.select_related('property', 'assigned_to'), pk=pk)
    staff_users = get_user_model().objects.filter(is_staff=True, is_active=True).order_by('username')

    if not contact.is_read:
        contact.is_read = True
        if contact.status == Contact.STATUS_NEW:
            contact.status = Contact.STATUS_IN_PROGRESS
        contact.save(update_fields=['is_read', 'status', 'updated_at'])

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'save_details':
            status = request.POST.get('status', '').strip()
            priority = request.POST.get('priority', '').strip()
            assigned_to_id = request.POST.get('assigned_to', '').strip()
            follow_up_raw = request.POST.get('follow_up_at', '').strip()
            internal_summary = request.POST.get('internal_summary', '').strip()

            if status in dict(Contact.STATUS_CHOICES):
                contact.status = status

            if priority in dict(Contact.PRIORITY_CHOICES):
                contact.priority = priority

            if assigned_to_id:
                contact.assigned_to = get_user_model().objects.filter(
                    pk=assigned_to_id,
                    is_staff=True,
                    is_active=True
                ).first()
            else:
                contact.assigned_to = None

            if follow_up_raw:
                dt = parse_datetime(follow_up_raw)
                if dt and timezone.is_naive(dt):
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                contact.follow_up_at = dt
            else:
                contact.follow_up_at = None

            contact.internal_summary = internal_summary
            contact.is_read = True

            if contact.status in [Contact.STATUS_RESPONDED, Contact.STATUS_CLOSED]:
                contact.is_responded = True
                if not contact.responded_at:
                    contact.responded_at = timezone.now()
            else:
                contact.is_responded = False
                if contact.status != Contact.STATUS_CLOSED:
                    contact.responded_at = None

            contact.save()
            messages.success(request, 'Solicitud actualizada correctamente.')

        elif action == 'add_note':
            note_text = request.POST.get('note', '').strip()
            if note_text:
                ContactNote.objects.create(
                    contact=contact,
                    author=request.user,
                    note=note_text
                )
                messages.success(request, 'Nota agregada.')
            else:
                messages.warning(request, 'Escribe una nota antes de guardar.')

        elif action == 'mark_read':
            contact.is_read = True
            if contact.status == Contact.STATUS_NEW:
                contact.status = Contact.STATUS_IN_PROGRESS
            contact.save(update_fields=['is_read', 'status', 'updated_at'])
            messages.success(request, 'Solicitud marcada como leida.')
        elif action == 'mark_unread':
            contact.is_read = False
            if contact.status == Contact.STATUS_IN_PROGRESS:
                contact.status = Contact.STATUS_NEW
            contact.save(update_fields=['is_read', 'status', 'updated_at'])
            messages.success(request, 'Solicitud marcada como no leida.')
        elif action == 'mark_responded':
            contact.is_read = True
            contact.is_responded = True
            contact.status = Contact.STATUS_RESPONDED
            contact.responded_at = timezone.now()
            contact.save(update_fields=['is_read', 'is_responded', 'status', 'responded_at', 'updated_at'])
            messages.success(request, 'Solicitud marcada como respondida.')
        elif action == 'mark_pending':
            contact.is_read = True
            contact.is_responded = False
            contact.status = Contact.STATUS_IN_PROGRESS
            contact.responded_at = None
            contact.save(update_fields=['is_read', 'is_responded', 'status', 'responded_at', 'updated_at'])
            messages.success(request, 'Solicitud marcada en seguimiento.')
        elif action == 'mark_closed':
            contact.status = Contact.STATUS_CLOSED
            contact.is_read = True
            contact.is_responded = True
            if not contact.responded_at:
                contact.responded_at = timezone.now()
            contact.save(update_fields=['status', 'is_read', 'is_responded', 'responded_at', 'updated_at'])
            messages.success(request, 'Solicitud cerrada.')

        return redirect('panel:inbox_detail', pk=contact.pk)

    context = {
        'contact': contact,
        'staff_users': staff_users,
        'status_choices': Contact.STATUS_CHOICES,
        'priority_choices': Contact.PRIORITY_CHOICES,
        'notes': contact.notes.select_related('author').all(),
    }
    return render(request, 'panel/inbox_detail.html', context)

