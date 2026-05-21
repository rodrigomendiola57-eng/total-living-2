from django.urls import path
from . import views

app_name = 'regions'

urlpatterns = [
    path('', views.regions_list, name='list'),
    path('panel/', views.panel_regions, name='panel_regions'),
    path('panel/agregar/', views.panel_region_add, name='panel_region_add'),
    path('panel/editar/<int:pk>/', views.panel_region_edit, name='panel_region_edit'),
    path('panel/eliminar/<int:pk>/', views.panel_region_delete, name='panel_region_delete'),
]
