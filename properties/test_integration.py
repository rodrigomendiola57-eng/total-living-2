"""Integración pública de propiedades (detalle / listado)."""

from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from properties.models import (
    Property,
    PropertyOperation,
    PropertyProcess,
    PropertyStatus,
    PropertyType,
)


class PropertyPublicIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_detail_disponible_returns_200(self):
        prop = Property.objects.create(
            title='Ficha pública D5',
            description='Texto',
            property_type=PropertyType.CASA,
            operation_type=PropertyOperation.VENTA,
            status=PropertyStatus.DISPONIBLE,
            process=PropertyProcess.NO_APLICA,
            price=Decimal('1200000'),
            currency='MXN',
            address='Av. Test',
            city='Querétaro',
            state='Querétaro',
            construction_area=Decimal('110'),
        )
        r = self.client.get(reverse('properties:detail', kwargs={'pk': prop.pk}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Ficha pública D5')
