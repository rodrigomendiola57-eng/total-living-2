"""
Integración del panel interno (staff): CMS inicio, listados, edición de propiedad,
carrusel y buzón — regresión mínima para release (Día 5).
"""

from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image

from contact.models import Contact
from panel.models import HomeContent, OrganigramMember
from properties.models import (
    CarouselSlide,
    Property,
    PropertyOperation,
    PropertyProcess,
    PropertyStatus,
    PropertyType,
)


def _tiny_jpeg_upload(name='slide.jpg'):
    buf = BytesIO()
    Image.new('RGB', (40, 24), color=(40, 80, 40)).save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type='image/jpeg')


class PanelStaffIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.staff = User.objects.create_user(
            'staff_d5', 'staff_d5@example.com', 'djangotest-pass-01', is_staff=True
        )

    def test_anonymous_redirected_from_dashboard(self):
        r = self.client.get(reverse('panel:dashboard'))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse('panel:login'), r.url)

    def test_staff_dashboard_and_properties_list(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('panel:dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('panel:properties')).status_code, 200)

    def test_home_cms_post_persists(self):
        self.client.force_login(self.staff)
        marker = 'CMS D5 integración único'
        r = self.client.post(
            reverse('panel:home_edit'),
            {'about_title': marker},
        )
        self.assertEqual(r.status_code, 302)
        hc = HomeContent.objects.get(singleton_key=HomeContent.SINGLETON_DEFAULT)
        self.assertEqual(hc.about_title, marker)

    def test_property_edit_post_updates_title_and_area(self):
        prop = Property.objects.create(
            title='Antes D5',
            description='Descripción',
            property_type=PropertyType.CASA,
            operation_type=PropertyOperation.VENTA,
            status=PropertyStatus.DISPONIBLE,
            process=PropertyProcess.NO_APLICA,
            price=Decimal('900000'),
            currency='MXN',
            address='Calle Prueba 1',
            city='Querétaro',
            state='Querétaro',
            construction_area=Decimal('100.00'),
        )
        self.client.force_login(self.staff)
        new_title = 'Después D5 integración'
        r = self.client.post(
            reverse('panel:property_edit', kwargs={'pk': prop.pk}),
            {
                'title': new_title,
                'description': prop.description,
                'property_type': PropertyType.CASA,
                'operation_type': PropertyOperation.VENTA,
                'status': PropertyStatus.DISPONIBLE,
                'process': PropertyProcess.NO_APLICA,
                'price': '950000',
                'currency': 'MXN',
                'address': prop.address,
                'city': prop.city,
                'state': prop.state,
                'zip_code': '',
                'country': 'México',
                'google_maps_url': '',
                'latitude': '',
                'longitude': '',
                'bedrooms': '2',
                'bathrooms': '2',
                'half_bathrooms': '0',
                'parking_spaces': '1',
                'construction_area': '145,50',
                'lot_area': '',
                'front_measure': '',
                'back_measure': '',
                'floors': '1',
                'year_built': '',
                'rooms': '4',
                'maintenance_fee': '',
            },
        )
        self.assertEqual(r.status_code, 302)
        prop.refresh_from_db()
        self.assertEqual(prop.title, new_title)
        self.assertEqual(prop.construction_area, Decimal('145.50'))

    def test_carousel_add_with_image_redirects_and_creates(self):
        before = CarouselSlide.objects.count()
        self.client.force_login(self.staff)
        r = self.client.post(
            reverse('panel:carousel_add'),
            {
                'title': 'Slide D5',
                'subtitle': '',
                'link_url': '',
                'link_text': 'Ver más',
                'order': '0',
                'is_active': 'on',
                'image': _tiny_jpeg_upload(),
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(CarouselSlide.objects.count(), before + 1)
        slide = CarouselSlide.objects.order_by('-id').first()
        self.assertEqual(slide.title, 'Slide D5')

    def test_inbox_lists_contact_from_public_form(self):
        Contact.objects.create(
            name='Cliente Buzón D5',
            email='buzon-d5@example.com',
            phone='',
            subject='Consulta',
            message='Texto de prueba integración.',
            status=Contact.STATUS_NEW,
            source='sitio_web',
        )
        self.client.force_login(self.staff)
        r = self.client.get(reverse('panel:inbox'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Cliente Buzón D5')

    def test_inbox_delete_removes_contact(self):
        row = Contact.objects.create(
            name='Borrar buzón D5',
            email='borrar-buzon-d5@example.com',
            phone='',
            subject='Asunto borrar',
            message='Cuerpo.',
            status=Contact.STATUS_NEW,
            source='sitio_web',
        )
        self.client.force_login(self.staff)
        pk = row.pk
        r = self.client.post(reverse('panel:inbox_delete', args=[pk]))
        self.assertEqual(r.status_code, 302)
        self.assertRedirects(r, reverse('panel:inbox'))
        self.assertFalse(Contact.objects.filter(pk=pk).exists())

    def _organigram_post_payload(self, **overrides):
        data = {
            'tier': OrganigramMember.TIER_ADVISOR,
            'sort_order': '3',
            'slug': '',
            'full_name': 'Miembro Org Integración D5',
            'role_label': 'Asesor de pruebas',
            'tag_label': '',
            'tag_icon': 'bi-briefcase',
            'bio': 'Bio breve de integración.',
            'expertise_1': 'Primera especialidad',
            'expertise_2': '',
            'expertise_3': '',
            'email': '',
            'url_whatsapp': '',
            'url_instagram': '',
            'url_facebook': '',
            'url_linkedin': '',
            'url_tiktok': '',
            'url_x': '',
            'is_visible': 'on',
        }
        data.update(overrides)
        return data

    def test_organigram_add_anonymous_redirects_to_login(self):
        r = self.client.get(reverse('panel:organigram_add'))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse('panel:login'), r.url)

    def test_organigram_add_post_creates_member_redirects_and_slug(self):
        self.client.force_login(self.staff)
        full_name = 'Ficha Org Integración Única D5'
        expected_slug = slugify(full_name)
        before = OrganigramMember.objects.count()
        r = self.client.post(
            reverse('panel:organigram_add'),
            self._organigram_post_payload(full_name=full_name, sort_order='9'),
        )
        self.assertEqual(r.status_code, 302)
        self.assertRedirects(r, reverse('panel:organigram_list'))
        self.assertEqual(OrganigramMember.objects.count(), before + 1)
        member = OrganigramMember.objects.get(full_name=full_name)
        self.assertEqual(member.slug, expected_slug)
        self.assertEqual(member.sort_order, 9)
        self.assertTrue(member.is_visible)

        pub = self.client.get(
            reverse('team_member_detail', kwargs={'slug': member.slug})
        )
        self.assertEqual(pub.status_code, 200)
        self.assertContains(pub, full_name)

    def test_organigram_add_duplicate_full_name_gets_incremented_slug(self):
        self.client.force_login(self.staff)
        full_name = 'Colisión Slug Org D5'
        base_slug = slugify(full_name)
        p = self._organigram_post_payload(full_name=full_name)
        r1 = self.client.post(reverse('panel:organigram_add'), p)
        self.assertEqual(r1.status_code, 302)
        r2 = self.client.post(reverse('panel:organigram_add'), p)
        self.assertEqual(r2.status_code, 302)
        slugs = list(
            OrganigramMember.objects.filter(full_name=full_name)
            .order_by('id')
            .values_list('slug', flat=True)
        )
        self.assertEqual(len(slugs), 2)
        self.assertEqual(slugs[0], base_slug)
        self.assertEqual(slugs[1], f'{base_slug}-2')


class PanelLoginIntegrationTests(TestCase):
    def test_staff_can_login_via_panel_form(self):
        User = get_user_model()
        User.objects.create_user(
            'login_d5', 'login_d5@example.com', 'secret-login-d5', is_staff=True
        )
        c = Client()
        r = c.post(
            reverse('panel:login'),
            {'username': 'login_d5', 'password': 'secret-login-d5'},
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('panel:dashboard'))
