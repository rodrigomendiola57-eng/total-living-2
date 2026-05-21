from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'panel'

urlpatterns = [
    path('login/', views.panel_login, name='login'),
    path('logout/', views.panel_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('inicio/', views.panel_home_edit, name='home_edit'),
    # Organigrama = parte de Nosotros (mismas rutas con nombre panel:*; URL bajo /nosotros/…)
    path('nosotros/organigrama/', views.panel_organigram_list, name='organigram_list'),
    path('nosotros/organigrama/agregar/', views.panel_organigram_add, name='organigram_add'),
    path('nosotros/organigrama/editar/<int:pk>/', views.panel_organigram_edit, name='organigram_edit'),
    path('nosotros/organigrama/eliminar/<int:pk>/', views.panel_organigram_delete, name='organigram_delete'),
    path('nosotros/', views.panel_nosotros_edit, name='nosotros_edit'),
    path('buzon/', views.panel_inbox, name='inbox'),
    path('buzon/<int:pk>/eliminar/', views.panel_inbox_delete, name='inbox_delete'),
    path('buzon/<int:pk>/', views.panel_inbox_detail, name='inbox_detail'),
    path('propiedades/', views.panel_properties, name='properties'),
    path('propiedades/editar/<int:pk>/', views.panel_property_edit, name='property_edit'),
    path('propiedades/eliminar/<int:pk>/', views.panel_property_delete, name='property_delete'),
    # Carrusel
    path('carrusel/', views.panel_carousel_list, name='carousel_list'),
    path('carrusel/agregar/', views.panel_carousel_add, name='carousel_add'),
    path('carrusel/editar/<int:pk>/', views.panel_carousel_edit, name='carousel_edit'),
    path('carrusel/eliminar/<int:pk>/', views.panel_carousel_delete, name='carousel_delete'),
    path('organigrama/', RedirectView.as_view(pattern_name='panel:organigram_list', permanent=False)),
    path('organigrama/agregar/', RedirectView.as_view(pattern_name='panel:organigram_add', permanent=False)),
    path('organigrama/editar/<int:pk>/', views.panel_legacy_organigram_edit_redirect, name='organigram_edit_legacy'),
    path('organigrama/eliminar/<int:pk>/', views.panel_legacy_organigram_delete_redirect, name='organigram_delete_legacy'),
]
