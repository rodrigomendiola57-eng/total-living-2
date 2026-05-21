from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Property, PropertyImage, PropertyFeature
from .forms import PropertyForm, PropertyImageForm


def property_list(request):
    """Vista para listar todas las propiedades"""
    from properties.models import PropertyType, PropertyOperation
    
    # Obtener todas las propiedades disponibles
    properties = Property.objects.filter(status='disponible').order_by('-created_at')
    
    # Filtros básicos
    property_type = request.GET.get('tipo', '')
    operation_type = request.GET.get('operacion', '')
    city = request.GET.get('ciudad', '')
    
    # Filtros avanzados
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    recamaras = request.GET.get('recamaras', '')
    banos = request.GET.get('banos', '')
    estacionamiento = request.GET.get('estacionamiento', '')
    area_min = request.GET.get('area_min', '')
    area_max = request.GET.get('area_max', '')
    
    # Aplicar filtros
    if property_type:
        properties = properties.filter(property_type=property_type)
    if operation_type:
        properties = properties.filter(operation_type=operation_type)
    if city:
        properties = properties.filter(city__icontains=city)
    if precio_min:
        properties = properties.filter(price__gte=precio_min)
    if precio_max:
        properties = properties.filter(price__lte=precio_max)
    if recamaras:
        properties = properties.filter(bedrooms__gte=recamaras)
    if banos:
        properties = properties.filter(bathrooms__gte=banos)
    if estacionamiento:
        properties = properties.filter(parking_spaces__gte=estacionamiento)
    if area_min:
        properties = properties.filter(area__gte=area_min)
    if area_max:
        properties = properties.filter(area__lte=area_max)
    
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
        }
    }
    
    return render(request, 'properties/list.html', context)


def property_detail(request, pk):
    """Vista para mostrar el detalle de una propiedad"""
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Obtener todas las imágenes de la propiedad
    images = property_obj.images.all().order_by('is_main', 'order')
    
    # Obtener características de la propiedad
    features = property_obj.features.all()
    
    # Obtener propiedades relacionadas (misma ciudad, mismo tipo)
    related_properties = Property.objects.filter(
        city=property_obj.city,
        property_type=property_obj.property_type,
        status='disponible'
    ).exclude(pk=pk)[:4]
    
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
@user_passes_test(is_staff_user, login_url='/admin/login/')
def add_property(request):
    """Vista para agregar una nueva propiedad (solo administradores)"""
    
    if request.method == 'POST':
        try:
            # Crear propiedad directamente desde POST
            property_obj = Property(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                property_type=request.POST.get('property_type'),
                operation_type=request.POST.get('operation_type'),
                status='disponible',
                price=request.POST.get('price'),
                currency='MXN',
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                zip_code=request.POST.get('zip_code', ''),
                country='México',
                bedrooms=int(request.POST.get('bedrooms', 0)),
                bathrooms=int(request.POST.get('bathrooms', 0)),
                half_bathrooms=int(request.POST.get('half_bathrooms', 0)),
                parking_spaces=int(request.POST.get('parking_spaces', 0)),
                area=request.POST.get('construction_area', 0),
                construction_area=request.POST.get('construction_area', 0),
                lot_area=request.POST.get('lot_area', 0),
                front_measure=request.POST.get('front_measure') or None,
                back_measure=request.POST.get('back_measure') or None,
                floors=int(request.POST.get('floors', 1)),
                year_built=int(request.POST.get('year_built')) if request.POST.get('year_built') else None,
                rooms=int(request.POST.get('rooms', 0)),
                maintenance_fee=request.POST.get('maintenance_fee') or None,
                is_featured='is_featured' in request.POST,
                is_new='is_new' in request.POST,
                published_at=timezone.now(),
                # Distribución
                has_sala='has_sala' in request.POST,
                has_comedor='has_comedor' in request.POST,
                has_cocina='has_cocina' in request.POST,
                has_estudio='has_estudio' in request.POST,
                has_despensa='has_despensa' in request.POST,
                has_cuarto_tv='has_cuarto_tv' in request.POST,
                has_gimnasio='has_gimnasio' in request.POST,
                has_balcon='has_balcon' in request.POST,
                has_jardin='has_jardin' in request.POST,
                has_patio='has_patio' in request.POST,
                has_roof_garden='has_roof_garden' in request.POST,
                has_area_lavado='has_area_lavado' in request.POST,
                has_bodega='has_bodega' in request.POST,
                # Amenidades
                amenity_salon='amenity_salon' in request.POST,
                amenity_vigilancia='amenity_vigilancia' in request.POST,
                amenity_acceso='amenity_acceso' in request.POST,
                amenity_areas_verdes='amenity_areas_verdes' in request.POST,
                amenity_juegos='amenity_juegos' in request.POST,
                amenity_gimnasio='amenity_gimnasio' in request.POST,
                amenity_alberca='amenity_alberca' in request.POST,
                amenity_cancha_futbol='amenity_cancha_futbol' in request.POST,
                amenity_cancha_tenis='amenity_cancha_tenis' in request.POST,
                amenity_cancha_basket='amenity_cancha_basket' in request.POST,
                amenity_asadores='amenity_asadores' in request.POST,
                amenity_pet_friendly='amenity_pet_friendly' in request.POST,
                # Servicios
                service_agua='service_agua' in request.POST,
                service_drenaje='service_drenaje' in request.POST,
                service_luz='service_luz' in request.POST,
                service_gas='service_gas' in request.POST,
                service_internet='service_internet' in request.POST,
                service_fibra='service_fibra' in request.POST,
                service_cable='service_cable' in request.POST,
                service_telefono='service_telefono' in request.POST,
                service_cisterna='service_cisterna' in request.POST,
                service_hidroneumatico='service_hidroneumatico' in request.POST,
                service_aire='service_aire' in request.POST,
                service_boiler='service_boiler' in request.POST,
            )
            
            property_obj.save()
            
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
            
        except Exception as e:
            messages.error(request, f'Error al crear la propiedad: {str(e)}')
            return render(request, 'properties/add_property.html', {'title': 'Agregar Nueva Propiedad'})
    
    context = {
        'title': 'Agregar Nueva Propiedad'
    }
    
    return render(request, 'properties/add_property.html', context)


@login_required
@user_passes_test(is_staff_user, login_url='/admin/login/')
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
                for idx, image in enumerate(images):
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image,
                        is_main=False,
                        order=current_count + idx,
                        alt_text=f"Imagen {current_count + idx + 1} de {property_obj.title}"
                    )
                messages.success(request, f'{len(images)} imágenes agregadas.')
        
        return redirect('properties:manage_images', pk=pk)
    
    images = property_obj.images.all().order_by('-is_main', 'order')
    
    context = {
        'property': property_obj,
        'images': images,
    }
    
    return render(request, 'properties/manage_images.html', context)
