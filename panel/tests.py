from django.test import TestCase

from panel.models import HomeContent, NosotrosContent


class PanelSingletonTests(TestCase):
    def test_home_content_singleton_key(self):
        a, _ = HomeContent.objects.get_or_create(singleton_key=HomeContent.SINGLETON_DEFAULT)
        b, _ = HomeContent.objects.get_or_create(singleton_key=HomeContent.SINGLETON_DEFAULT)
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(HomeContent.objects.count(), 1)

    def test_nosotros_singleton_key(self):
        a, _ = NosotrosContent.objects.get_or_create(singleton_key=NosotrosContent.SINGLETON_DEFAULT)
        b, _ = NosotrosContent.objects.get_or_create(singleton_key=NosotrosContent.SINGLETON_DEFAULT)
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(NosotrosContent.objects.count(), 1)
