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


class SearchViewTests(TestCase):
    def test_search_get_ok(self):
        response = Client().get(reverse('search:search'))
        self.assertEqual(response.status_code, 200)


class HealthEndpointTests(TestCase):
    """Regresión Día 6–7: endpoints para balanceador / despliegue."""

    def test_health_live_returns_json(self):
        r = self.client.get('/health/live/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get('status'), 'live')

    def test_health_ready_database_ok(self):
        r = self.client.get('/health/ready/')
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body.get('status'), 'ready')
        self.assertEqual(body.get('database'), 'ok')


class SearchIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_finds_property_by_city(self):
        Property.objects.create(
            title='Residencial D5 Norte',
            description='Desc',
            property_type=PropertyType.CASA,
            operation_type=PropertyOperation.VENTA,
            status=PropertyStatus.DISPONIBLE,
            process=PropertyProcess.NO_APLICA,
            price=Decimal('3500000'),
            currency='MXN',
            address='Privada Test',
            city='Querétaro',
            state='Querétaro',
            construction_area=Decimal('200'),
        )
        r = self.client.get(reverse('search:search'), {'city': 'Querétaro'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Residencial D5 Norte')

    def test_api_cities_returns_json(self):
        r = self.client.get(reverse('search:api_cities'))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('cities', data)
        self.assertIsInstance(data['cities'], list)

    def test_public_home_smoke_200(self):
        """Regresión mínima: página de inicio responde."""
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
