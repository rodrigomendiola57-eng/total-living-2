from decimal import Decimal
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from contact.models import Contact

from .models import Development


def _minimal_development(**kwargs):
    data = dict(
        name='Torre Demo QA',
        description='Descripción de prueba.',
        location='Centro',
        city='Querétaro',
        state='Querétaro',
        price_from=Decimal('2500000'),
        is_active=True,
    )
    data.update(kwargs)
    return Development.objects.create(**data)


class DevelopmentModelTests(TestCase):
    def test_slug_auto_generated_when_blank(self):
        dev = _minimal_development(name='Proyecto Sin Slug', slug='')
        self.assertTrue(dev.slug)
        self.assertIn('proyecto', dev.slug)

    def test_get_absolute_url_uses_slug(self):
        dev = _minimal_development(slug='torre-demo')
        self.assertEqual(
            dev.get_absolute_url(),
            reverse('developments:detail', kwargs={'development_slug': 'torre-demo'}),
        )


class DevelopmentsPublicViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_list_returns_200(self):
        _minimal_development()
        r = self.client.get(reverse('developments:list'))
        self.assertEqual(r.status_code, 200)

    def test_detail_active_returns_200(self):
        dev = _minimal_development(slug='activo-uno')
        r = self.client.get(
            reverse('developments:detail', kwargs={'development_slug': dev.slug})
        )
        self.assertEqual(r.status_code, 200)

    def test_detail_inactive_returns_404(self):
        dev = _minimal_development(slug='inactivo', is_active=False)
        r = self.client.get(
            reverse('developments:detail', kwargs={'development_slug': dev.slug})
        )
        self.assertEqual(r.status_code, 404)


class DevelopmentsLegacyRedirectTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_numeric_detail_redirects_to_slug(self):
        dev = _minimal_development(slug='legacy-slug')
        legacy = reverse('developments:detail_legacy', kwargs={'pk': dev.pk})
        r = self.client.get(legacy)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, dev.get_absolute_url())


class DevelopmentsQuizLeadTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Misma cache IP que formularios de contacto (`ratelimit_contact`).
        cache.clear()

    def test_quiz_get_returns_405(self):
        r = self.client.get(reverse('developments:quiz_lead'))
        self.assertEqual(r.status_code, 405)

    def test_quiz_invalid_returns_400(self):
        r = self.client.post(reverse('developments:quiz_lead'), {})
        self.assertEqual(r.status_code, 400)
        data = r.json()
        self.assertFalse(data.get('ok'))
        self.assertEqual(data.get('error'), 'name')

    def test_quiz_valid_creates_contact(self):
        before = Contact.objects.count()
        r = self.client.post(
            reverse('developments:quiz_lead'),
            {
                'name': 'Cliente Quiz',
                'whatsapp': '+52 442 123 4567',
                'ambiente': 'urbano',
                'espacio': 'pareja',
                'tiempo': 'pronto',
                'must_have': ['pool', 'pet'],
            },
        )
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(body.get('ok'))
        self.assertEqual(Contact.objects.count(), before + 1)
        lead = Contact.objects.order_by('-id').first()
        self.assertEqual(lead.source, 'quiz_desarrollos')
        self.assertIn('Quiz desarrollos', lead.subject)


class DevelopmentsPanelGateTests(TestCase):
    """Panel de desarrollos: solo staff (acceso total para el equipo reducido)."""

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.staff = User.objects.create_user(
            'staff_dev', 'staff_dev@example.com', 'secret123', is_staff=True
        )
        self.plain = User.objects.create_user(
            'no_staff', 'plain@example.com', 'secret123', is_staff=False
        )

    def test_panel_anonymous_redirects_to_login_with_next(self):
        """`login_required` usa LOGIN_URL (/accounts/login/ por defecto) con next al panel."""
        url = reverse('developments:panel_list')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 302)
        parsed = urlparse(r.url)
        self.assertTrue(parsed.path.endswith('/login/'))
        qs = parse_qs(parsed.query)
        self.assertEqual(qs.get('next', [''])[0], url)

    def test_panel_plain_user_redirected(self):
        self.client.login(username='no_staff', password='secret123')
        r = self.client.get(reverse('developments:panel_list'))
        self.assertEqual(r.status_code, 302)

    def test_panel_staff_gets_200(self):
        self.client.login(username='staff_dev', password='secret123')
        r = self.client.get(reverse('developments:panel_list'))
        self.assertEqual(r.status_code, 200)
