from decimal import Decimal

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from contact.models import Contact
from contact.quick_presets import get_contact_quick_presets
from properties.models import (
    Property,
    PropertyOperation,
    PropertyProcess,
    PropertyStatus,
    PropertyType,
)


class ContactViewTests(TestCase):
    def test_contact_get_ok(self):
        response = Client().get(reverse('contact:contact'))
        self.assertEqual(response.status_code, 200)


class ContactQuickPresetsTests(TestCase):
    def test_presets_without_property_count(self):
        presets = get_contact_quick_presets(None)
        self.assertEqual(len(presets), 5)
        self.assertTrue(all('label' in p and 'message' in p and 'lead' in p for p in presets))

    def test_presets_with_property_adds_row(self):
        class _FakeProp:
            title = 'Casa demo'

        presets = get_contact_quick_presets(_FakeProp())
        self.assertEqual(len(presets), 6)
        self.assertIn('Casa demo', presets[-1]['message'])


class ContactFormIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()  # rate limit por IP comparte contador entre tests

    def test_valid_post_creates_contact_and_redirects(self):
        before = Contact.objects.count()
        r = self.client.post(
            reverse('contact:contact'),
            {
                'name': 'María Integración',
                'email': 'maria.integracion@example.com',
                'phone': '4421234567',
                'subject': 'Consulta inventario',
                'message': 'Busco casa en zona norte; mensaje de prueba Día 5.',
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Contact.objects.count(), before + 1)
        lead = Contact.objects.order_by('-id').first()
        self.assertEqual(lead.email, 'maria.integracion@example.com')
        self.assertEqual(lead.source, 'sitio_web')

    def test_contact_with_property_sets_source_propiedad(self):
        prop = Property.objects.create(
            title='Casa buzón contacto',
            description='d',
            property_type=PropertyType.CASA,
            operation_type=PropertyOperation.VENTA,
            status=PropertyStatus.DISPONIBLE,
            process=PropertyProcess.NO_APLICA,
            price=Decimal('1'),
            currency='MXN',
            address='A',
            city='C',
            state='S',
            construction_area=Decimal('100'),
        )
        r = self.client.post(
            reverse('contact:contact'),
            {
                'name': 'Lead Propiedad',
                'email': 'lead.propiedad@example.com',
                'phone': '',
                'subject': '',
                'message': 'Quiero información.',
                'property_id': str(prop.pk),
            },
        )
        self.assertEqual(r.status_code, 302)
        lead = Contact.objects.get(email='lead.propiedad@example.com')
        self.assertEqual(lead.source, 'sitio_web_propiedad')
        self.assertEqual(lead.property_id, prop.pk)

    def test_lead_metadata_prepended_to_message(self):
        r = self.client.post(
            reverse('contact:contact'),
            {
                'name': 'Lead Meta',
                'email': 'lead.meta@example.com',
                'phone': '',
                'subject': 'Asunto prueba',
                'message': 'Cuerpo del mensaje.',
                'lead_interest': 'comprar',
                'contact_channel': 'whatsapp',
                'timeline': '1_3_meses',
                'marketing_ok': '1',
            },
        )
        self.assertEqual(r.status_code, 302)
        lead = Contact.objects.get(email='lead.meta@example.com')
        self.assertIn('[Captación de lead]', lead.message)
        self.assertIn('Comprar vivienda', lead.message)
        self.assertIn('WhatsApp', lead.message)
        self.assertIn('Cuerpo del mensaje.', lead.message)

    def test_missing_required_fields_returns_200_and_no_row(self):
        before = Contact.objects.count()
        r = self.client.post(
            reverse('contact:contact'),
            {
                'name': '',
                'email': 'solo@email.com',
                'message': '',
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Contact.objects.count(), before)

    def test_honeypot_does_not_create_contact(self):
        before = Contact.objects.count()
        r = self.client.post(
            reverse('contact:contact'),
            {
                'name': 'Bot',
                'email': 'bot@example.com',
                'message': 'Spam',
                'website': 'http://spam.example',
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Contact.objects.count(), before)


class AdvisoryFormsIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_advisory_purchase_post_creates_contact(self):
        r = self.client.post(
            reverse('contact:advisory_purchase'),
            {
                'name': 'Comprador D5',
                'email': 'compra@example.com',
                'phone': '',
                'city': 'Querétaro',
                'property_type': 'casa',
                'budget': '3 MD',
                'message': 'Busco 3 recámaras.',
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(
            Contact.objects.filter(source='asesoria_compra', name='Comprador D5').exists()
        )

    def test_advisory_sale_post_creates_contact(self):
        r = self.client.post(
            reverse('contact:advisory_sale'),
            {
                'name': 'Vendedor D5',
                'email': 'venta@example.com',
                'phone': '',
                'city': 'Querétaro',
                'property_type': 'departamento',
                'estimated_price': '4.5M',
                'sale_urgency': 'media',
                'exclusive_interest': 'si',
                'message': 'Quiero publicar.',
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(
            Contact.objects.filter(source='asesoria_venta', name='Vendedor D5').exists()
        )
