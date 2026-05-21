from decimal import Decimal
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from properties.money import parse_coordinate, parse_decimal_value
from django.test import RequestFactory, override_settings

from properties.og_meta import absolute_media_uri, build_property_open_graph
from properties.technical_sheet import apply_technical_sheet, validate_technical_sheet_upload
from properties.models import (
    Property,
    PropertyImage,
    PropertyOperation,
    PropertyProcess,
    PropertyStatus,
    PropertyType,
)


def _tiny_jpeg():
    buf = BytesIO()
    Image.new('RGB', (10, 10), color='gray').save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile('t.jpg', buf.read(), content_type='image/jpeg')


class MoneyParseTests(TestCase):
    def test_parse_coordinate(self):
        self.assertEqual(parse_coordinate('20.588793'), Decimal('20.588793'))
        self.assertIsNone(parse_coordinate(''))
        self.assertIsNone(parse_coordinate('300'))  # fuera de [-180, 180]

    def test_parse_decimal_value_construction(self):
        self.assertEqual(parse_decimal_value('150,50'), Decimal('150.50'))


class PropertyConstructionAreaTests(TestCase):
    def test_save_requires_construction_area(self):
        prop = Property(
            title='Test',
            description='d',
            property_type=PropertyType.CASA,
            operation_type=PropertyOperation.VENTA,
            status=PropertyStatus.DISPONIBLE,
            process=PropertyProcess.NO_APLICA,
            price=Decimal('100'),
            currency='MXN',
            address='Calle 1',
            city='Querétaro',
            state='Querétaro',
            construction_area=None,
        )
        with self.assertRaises(ValidationError):
            prop.save()


class OpenGraphMetaTests(TestCase):
    @override_settings(PUBLIC_SITE_URL='https://totalliving.example')
    def test_og_urls_use_public_site(self):
        prop = Property.objects.create(
            title='Casa con vista',
            description='Hermosa casa en la zona.',
            property_type=PropertyType.CASA,
            operation_type=PropertyOperation.VENTA,
            status=PropertyStatus.DISPONIBLE,
            process=PropertyProcess.NO_APLICA,
            price=Decimal('2500000'),
            currency='MXN',
            address='Av. 1',
            city='Querétaro',
            state='Qro.',
            construction_area=Decimal('120'),
        )
        request = RequestFactory().get('/properties/1/')
        og = build_property_open_graph(prop, request)
        self.assertEqual(og['url'], f'https://totalliving.example{prop.get_absolute_url()}')
        self.assertTrue(og['image'].startswith('https://totalliving.example'))
        self.assertIn('Casa con vista', og['title'])

    def test_absolute_media_uri_with_request(self):
        request = RequestFactory().get('/properties/1/')
        uri = absolute_media_uri('/media/x.jpg', request)
        self.assertIn('/media/x.jpg', uri)


class TechnicalSheetTests(TestCase):
    def test_validate_rejects_invalid_extension(self):
        bad = SimpleUploadedFile('ficha.exe', b'x', content_type='application/octet-stream')
        with self.assertRaises(ValidationError):
            validate_technical_sheet_upload(bad)

    def test_apply_and_download_pdf(self):
        prop = Property.objects.create(
            title='Con ficha',
            description='d',
            property_type=PropertyType.CASA,
            operation_type=PropertyOperation.VENTA,
            status=PropertyStatus.DISPONIBLE,
            process=PropertyProcess.NO_APLICA,
            price=Decimal('500000'),
            currency='MXN',
            address='A',
            city='C',
            state='S',
            construction_area=Decimal('90'),
        )
        pdf = SimpleUploadedFile('mi-ficha.pdf', b'%PDF-1.4 test', content_type='application/pdf')
        apply_technical_sheet(prop, uploaded_file=pdf)
        prop.save(update_fields=['technical_sheet'])
        prop.refresh_from_db()
        self.assertTrue(prop.has_technical_sheet())
        self.assertTrue(prop.get_technical_sheet_display_name().endswith('.pdf'))

        client = Client()
        url = reverse('properties:technical_sheet', kwargs={'pk': prop.pk})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response.get('Content-Disposition', ''))


class PropertyMainImageTests(TestCase):
    def test_second_main_demotes_first(self):
        prop = Property.objects.create(
            title='Casa demo',
            description='d',
            property_type=PropertyType.CASA,
            operation_type=PropertyOperation.VENTA,
            status=PropertyStatus.DISPONIBLE,
            process=PropertyProcess.NO_APLICA,
            price=Decimal('1000000'),
            currency='MXN',
            address='A',
            city='C',
            state='S',
            construction_area=Decimal('120.00'),
        )
        i1 = PropertyImage.objects.create(
            property=prop, image=_tiny_jpeg(), is_main=True, order=0
        )
        i2 = PropertyImage.objects.create(
            property=prop, image=_tiny_jpeg(), is_main=True, order=1
        )
        i1.refresh_from_db()
        i2.refresh_from_db()
        mains = list(PropertyImage.objects.filter(property=prop, is_main=True))
        self.assertEqual(len(mains), 1)
        self.assertEqual(mains[0].pk, i2.pk)
        self.assertFalse(PropertyImage.objects.get(pk=i1.pk).is_main)
