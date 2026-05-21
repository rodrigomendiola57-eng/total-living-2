from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('api/amenities/', views.amenities_api, name='api_amenities'),
    path('mapa/', views.properties_map, name='map'),
    path('', views.property_list, name='list'),
    path('comprar/todas/', views.comprar_todas_list, name='comprar_todas'),
    path('departamentos/', views.departamentos_list, name='departamentos'),
    path('casas/', views.casas_list, name='casas'),
    path('terrenos/', views.terrenos_list, name='terrenos'),
    path('locales/', views.locales_list, name='locales'),
    path('renta/', views.renta_list, name='renta'),
    path('renta/departamentos/', views.renta_departamentos_list, name='renta_departamentos'),
    path('renta/casas/', views.renta_casas_list, name='renta_casas'),
    path('renta/locales/', views.renta_locales_list, name='renta_locales'),
    path('<int:pk>/', views.property_detail, name='detail'),
    path('agregar/', views.add_property, name='add'),
    path('<int:pk>/editar/', views.edit_property, name='edit'),
    path('<int:pk>/imagenes/', views.manage_images, name='manage_images'),
    path('<int:pk>/pdf/', views.download_property_pdf, name='download_pdf'),
]
