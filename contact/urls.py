from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_view, name='contact'),
    path('asesoria/compra/', views.advisory_purchase_view, name='advisory_purchase'),
    path('asesoria/venta/', views.advisory_sale_view, name='advisory_sale'),
]
