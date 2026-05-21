from decimal import Decimal
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from properties.money import parse_coordinate, parse_decimal_value
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
