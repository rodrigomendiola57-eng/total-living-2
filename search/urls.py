from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_view, name='search'),
    path('api/cities/', views.api_cities, name='api_cities'),
    path('api/regions/', views.api_regions_by_city, name='api_regions'),
]
