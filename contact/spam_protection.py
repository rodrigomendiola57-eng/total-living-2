"""
Proteccion anti-spam para el formulario publico de contacto.

Incluye:
- Honeypot: campo oculto que los bots suelen completar.
- Rate limit por IP usando cache de Django.
"""
from django.conf import settings
from django.core.cache import cache
from functools import wraps


def _parse_rate(rate_str):
    """
    Convierte un rate en formato "N/unidad" a (N, segundos).
    Ejemplos: 6/10m, 30/h, 100/d.
    """
    default_count = 5
    default_period = 60 * 60
    if not rate_str:
        return default_count, default_period

    parts = str(rate_str).strip().lower().split("/")
    if len(parts) != 2:
        return default_count, default_period

    try:
        count = int(parts[0])
    except ValueError:
        return default_count, default_period

    window = parts[1].strip()
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}

    if len(window) == 1 and window in multipliers:
        return count, multipliers[window]
    if len(window) > 1 and window[:-1].isdigit() and window[-1] in multipliers:
        return count, int(window[:-1]) * multipliers[window[-1]]
    return default_count, default_period


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def is_honeypot_triggered(request):
    """True si el campo honeypot trae valor."""
    return bool((request.POST.get("website") or "").strip())


def is_contact_rate_limited(request):
    """True si la IP excedio el limite de envios al contacto."""
    if request.method != "POST":
        return False

    max_hits, period_seconds = _parse_rate(
        getattr(settings, "CONTACT_FORM_RATELIMIT_IP", "5/h")
    )
    ip = _client_ip(request)
    key = f"contact_rl:ip:{ip}"

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


def ratelimit_contact(view_func):
    """
    Decorador de rate limit para POST del formulario de contacto.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.method == "POST" and is_contact_rate_limited(request):
            request.contact_rate_limited = True
        return view_func(request, *args, **kwargs)

    return _wrapped

