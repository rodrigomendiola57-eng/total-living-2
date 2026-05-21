"""
Límite de intentos en el login del panel (solo caché Django, sin paquetes extra).
Compatible con los mismos valores de settings que antes (ej. 15/15m, 5/m).
"""
from django.conf import settings
from django.core.cache import cache


def _parse_rate(rate_str):
    """
    Devuelve (max_intentos, periodo_segundos).
    Ejemplos: '15/15m', '8/15m', '5/m', '10/h'
    """
    rate_str = (rate_str or '15/15m').strip().lower()
    parts = rate_str.split('/')
    if len(parts) != 2:
        return 15, 15 * 60
    try:
        count = int(parts[0])
    except ValueError:
        return 15, 15 * 60
    r = parts[1].strip()
    mult = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    if len(r) >= 2 and r[:-1].isdigit() and r[-1] in mult:
        return count, int(r[:-1]) * mult[r[-1]]
    if len(r) == 1 and r in mult:
        return count, mult[r]
    return 15, 15 * 60


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _increment_and_blocked(cache_key, max_hits, period_seconds):
    """
    Cuenta un intento. Devuelve True si ya se superó el límite (bloqueado).
    """
    key = f'panel_rl:{cache_key}'
    current = cache.get(key)
    if current is None:
        cache.set(key, 1, period_seconds)
        return False
    if current >= max_hits:
        return True
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, period_seconds)
    return False


def panel_login_is_limited(request):
    """True si este POST al login debe rechazarse por rate limit."""
    if request.method != 'POST':
        return False

    ip_rate = getattr(settings, 'PANEL_LOGIN_RATELIMIT_IP', '15/15m')
    user_rate = getattr(settings, 'PANEL_LOGIN_RATELIMIT_USERNAME', '8/15m')
    ip_max, ip_sec = _parse_rate(ip_rate)
    user_max, user_sec = _parse_rate(user_rate)

    ip = _get_client_ip(request)
    username = (request.POST.get('username') or '').strip() or 'anonymous'

    # Primero IP: si está bloqueada, no contamos usuario
    if _increment_and_blocked(f'ip:{ip}', ip_max, ip_sec):
        return True
    # Luego por nombre de usuario (fuerza bruta sobre una cuenta)
    if _increment_and_blocked(f'u:{username}', user_max, user_sec):
        return True
    return False
