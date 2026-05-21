"""
Parseo de precios en MXN (panel, desarrollos, alta de propiedades).

Evita errores al mezclar formatos: 2,170,000 (miles US), 2.170.000 (miles MX),
2170,50 (decimal con coma), etc.
"""
import re
from decimal import Decimal, InvalidOperation


def parse_mx_money(raw):
    """
    Convierte texto de precio a Decimal.

    Ejemplos válidos: 2170000, 2,170,000, 2.170.000, $2.170.000, 2170,50
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    s = re.sub(r'[\$\sMXNmxn]', '', s, flags=re.I)
    if not s:
        return None
    if not re.match(r'^[\d.,]+$', s):
        try:
            return Decimal(s)
        except (InvalidOperation, ValueError):
            return None

    # Comas: miles (varias) o decimal europeo (una coma, 1–2 decimales)
    if ',' in s:
        if s.count(',') == 1:
            a, b = s.split(',')
            if len(b) <= 2 and b.isdigit() and a.replace('.', '').isdigit():
                s = a + '.' + b
            else:
                s = s.replace(',', '')
        else:
            s = s.replace(',', '')

    if '.' not in s:
        try:
            return Decimal(s)
        except InvalidOperation:
            return None

    parts = s.split('.')
    if len(parts) >= 3:
        last = parts[-1]
        if len(last) <= 2 and last.isdigit():
            return Decimal(''.join(parts[:-1]) + '.' + last)
        return Decimal(''.join(parts))

    left, right = parts[0], parts[1]
    if len(right) <= 2 and right.isdigit():
        return Decimal(f'{left}.{right}')
    if len(right) == 3 and left.isdigit() and len(left) <= 3:
        return Decimal(left + right)
    try:
        return Decimal(s.replace('.', ''))
    except InvalidOperation:
        return None


def parse_decimal_value(raw):
    """
    Convierte valores numéricos a Decimal con tolerancia de formato.

    Ejemplos válidos:
    - 1850
    - 1,850.75
    - 1.850,75
    - "  $ 1,850  "
    """
    if raw is None:
        return None

    s = str(raw).strip()
    if not s:
        return None

    s = re.sub(r'[\$\s]', '', s)
    if not s:
        return None

    if ',' in s and '.' in s:
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        if s.count(',') == 1:
            left, right = s.split(',')
            if len(right) <= 2 and right.isdigit() and left.replace('.', '').isdigit():
                s = left.replace('.', '') + '.' + right
            else:
                s = s.replace(',', '')
        else:
            s = s.replace(',', '')

    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def parse_coordinate(raw):
    """
    Latitud o longitud para DecimalField (sin float).
    Acepta valores en [-180, 180] (cubre lat/lon usados en México y globalmente).
    """
    d = parse_decimal_value(raw)
    if d is None:
        return None
    if Decimal('-180') <= d <= Decimal('180'):
        return d
    return None
