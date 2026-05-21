from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'developments'

urlpatterns = [
    path('', views.developments_list, name='list'),
    path('quiz-lead/', views.developments_quiz_lead, name='quiz_lead'),
    # —— Panel (rutas literales antes que <slug>) ——
    path('panel/cms/', views.panel_dev_cms, name='panel_cms'),
    path('panel/amenidades/', views.panel_amenity_list, name='panel_amenities'),
    path('panel/amenidades/nueva/', views.panel_amenity_add, name='panel_amenity_add'),
    path('panel/amenidades/<uuid:pk>/editar/', views.panel_amenity_edit, name='panel_amenity_edit'),
    path('panel/amenidades/<uuid:pk>/eliminar/', views.panel_amenity_delete, name='panel_amenity_delete'),
    path('panel/modelos/', views.panel_unit_models_list, name='panel_unit_models'),
    path('panel/modelos/nuevo/', views.panel_unit_model_add, name='panel_unit_model_add'),
    path('panel/modelos/<int:pk>/editar/', views.panel_unit_model_edit, name='panel_unit_model_edit'),
    path('panel/modelos/<int:pk>/imagenes/', views.panel_unit_model_images, name='panel_unit_model_images'),
    path(
        'panel/pagina-hero/',
        RedirectView.as_view(pattern_name='developments:panel_cms', permanent=False),
        name='panel_page_hero',
    ),
    path('panel/add/', views.panel_development_add, name='panel_add'),
    path('panel/<int:pk>/edit/', views.panel_development_edit, name='panel_edit'),
    path('panel/<int:pk>/delete/', views.panel_development_delete, name='panel_delete'),
    path('panel/<int:pk>/images/', views.panel_development_images, name='panel_images'),
    path('panel/', views.panel_developments, name='panel_list'),
    # —— URLs antiguas (ID numérico) → redirección canónica por slug ——
    path(
        '<int:pk>/modelo/<slug:model_slug>/',
        views.redirect_legacy_unit_model,
        name='unit_model_detail_legacy',
    ),
    path('<int:pk>/', views.redirect_legacy_development_detail, name='detail_legacy'),
    # —— Público canónico: /desarrollos/<slug-desarrollo>/modelos/<slug-modelo>/ ——
    path(
        '<slug:development_slug>/modelos/<slug:model_slug>/',
        views.development_unit_detail,
        name='unit_model_detail',
    ),
    path('<slug:development_slug>/', views.development_detail, name='detail'),
]
