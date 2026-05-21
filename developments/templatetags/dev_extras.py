"""Filtros de plantilla para desarrollos."""
from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter(is_safe=True)
def price_intcomma(value):
    """
    Precio entero con separador de miles tipo 1,234,567 (coma anglosajona).
    Evita depender solo de la localización de intcomma.
    """
    if value is None:
        return '—'
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return str(value)
    n = int(d.quantize(Decimal('1')))
    return f'{n:,}'
