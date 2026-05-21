"""
Contrato de acceso para el equipo interno (~2 cuentas staff).

No hay roles granulares: quien edita el inventario y captación usa cuentas Django
con is_staff=True (panel Total Living y rutas de desarrollos protegidas así).
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse


def _is_staff_operator(user) -> bool:
    """Misma condición que `is_staff_user` en panel/developments/properties."""
    return user.is_authenticated and user.is_staff


class StaffOperatorContractTests(TestCase):
    def test_anonymous_not_operator(self):
        self.assertFalse(_is_staff_operator(AnonymousUser()))

    def test_authenticated_non_staff_not_operator(self):
        User = get_user_model()
        u = User.objects.create_user('visitante', 'v@example.com', 'x', is_staff=False)
        self.assertTrue(u.is_authenticated)
        self.assertFalse(_is_staff_operator(u))

    def test_staff_user_is_operator(self):
        User = get_user_model()
        u = User.objects.create_user('interno', 'i@example.com', 'x', is_staff=True)
        self.assertTrue(_is_staff_operator(u))


class AdminLoginRouteTests(TestCase):
    """Las vistas staff usan `login_url='admin:login'` en varios módulos."""

    def test_admin_login_named_url_resolves(self):
        url = reverse('admin:login')
        self.assertTrue(url.startswith('/'))
