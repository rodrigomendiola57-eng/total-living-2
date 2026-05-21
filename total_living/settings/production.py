"""
Configuración para entorno de producción.

Almacenamiento de archivos: Amazon S3 vía django-storages/boto3 (variables AWS_* en .env).
Proveedor compatible R2 opcional (OBJECT_STORAGE_PROVIDER=r2). Credenciales solo por entorno;
en EC2 con perfil de instancia IAM las claves pueden ir vacías y boto usa el rol.
"""
from pathlib import Path
import os

from dotenv import load_dotenv

# Cargar `.env` antes de base/decouple (evita ALLOWED_HOSTS vacío en Windows).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if (_PROJECT_ROOT / '.env').is_file():
    load_dotenv(_PROJECT_ROOT / '.env', override=True)

from .base import *
from decouple import config
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

DEBUG = False

_allow_raw = (os.environ.get('ALLOWED_HOSTS') or '').strip() or config('ALLOWED_HOSTS', default='').strip()
ALLOWED_HOSTS = [h.strip() for h in _allow_raw.split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in config('CSRF_TRUSTED_ORIGINS', default='').split(',') if o.strip()]

# Auto-soporte para Render: evita 400 por host no permitido.
render_host = (os.getenv('RENDER_EXTERNAL_HOSTNAME') or '').strip()
if render_host and render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_host)
if render_host:
    render_origin = f'https://{render_host}'
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)

if not ALLOWED_HOSTS:
    raise ValueError(
        'ALLOWED_HOSTS está vacío. En tu archivo .env del proyecto pon una línea como:\n'
        '  ALLOWED_HOSTS=127.0.0.1,localhost\n'
        'Si en PowerShell ejecutaste antes DJANGO_SETTINGS_MODULE=production y solo quieres desarrollo, '
        'cierra esa terminal o ejecuta: Remove-Item Env:\\DJANGO_SETTINGS_MODULE\n'
        'Para runserver con settings de producción a propósito: '
        '$env:RUNSERVER_USE_PRODUCTION=\"1\" ; python manage.py runserver 8090'
    )

# Cookies de sesión (explícito para auditorías de seguridad).
SESSION_COOKIE_HTTPONLY = True

# Database - PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Security settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=SECURE_SSL_REDIRECT, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=SECURE_SSL_REDIRECT, cast=bool)
SESSION_COOKIE_SAMESITE = config('SESSION_COOKIE_SAMESITE', default='Lax')
CSRF_COOKIE_SAMESITE = config('CSRF_COOKIE_SAMESITE', default='Lax')
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# En producción real conviene activarlo para bloquear claves débiles.
ENFORCE_STRONG_SECRET_KEY = config('ENFORCE_STRONG_SECRET_KEY', default=True, cast=bool)
if ENFORCE_STRONG_SECRET_KEY:
    weak_key = (
        not SECRET_KEY
        or SECRET_KEY.startswith('django-insecure-')
        or len(SECRET_KEY) < 50
        or len(set(SECRET_KEY)) < 5
    )
    if weak_key:
        raise ImproperlyConfigured(
            'SECRET_KEY insegura: usa una clave aleatoria robusta y >= 50 caracteres.'
        )

if not DEBUG:
    # Nota: SECURE_BROWSER_XSS_FILTER es un ajuste legacy para navegadores antiguos.
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Almacenamiento de objetos (S3-compatible).
# USE_S3 y USE_S3_* son nombres heredados; USE_OBJECT_STORAGE es el conmutador principal.
USE_S3 = config('USE_S3', default=False, cast=bool)
USE_OBJECT_STORAGE = config('USE_OBJECT_STORAGE', default=USE_S3, cast=bool)
OBJECT_STORAGE_PROVIDER = config('OBJECT_STORAGE_PROVIDER', default='aws').strip().lower()
USE_S3_STATIC = config('USE_S3_STATIC', default=USE_OBJECT_STORAGE, cast=bool)
USE_S3_MEDIA = config('USE_S3_MEDIA', default=USE_OBJECT_STORAGE, cast=bool)

AWS_STATIC_LOCATION = config('AWS_STATIC_LOCATION', default='static')
AWS_MEDIA_LOCATION = config('AWS_MEDIA_LOCATION', default='media')
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_QUERYSTRING_AUTH = config('AWS_QUERYSTRING_AUTH', default=True, cast=bool)
AWS_QUERYSTRING_EXPIRE = config('AWS_QUERYSTRING_EXPIRE', default=900, cast=int)
AWS_DEFAULT_ACL = None
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ADDRESSING_STYLE = 'virtual'
AWS_S3_CUSTOM_DOMAIN = None
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_ENDPOINT_URL = None
R2_S3_API_HOST = ''
R2_BUCKET_NAME = ''

if USE_S3_STATIC or USE_S3_MEDIA:
    if OBJECT_STORAGE_PROVIDER in ('aws', 'aws_s3', 's3'):
        AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
        AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
        AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1').strip() or 'us-east-1'
        endpoint = config('AWS_S3_ENDPOINT_URL', default='').strip()
        AWS_S3_ENDPOINT_URL = endpoint or None
        custom = config('AWS_S3_CUSTOM_DOMAIN', default='').strip().rstrip('/')
        if custom:
            AWS_S3_CUSTOM_DOMAIN = custom.replace('https://', '').replace('http://', '')
    elif OBJECT_STORAGE_PROVIDER == 'r2':
        R2_ACCOUNT_ID = config('R2_ACCOUNT_ID')
        R2_ACCESS_KEY_ID = config('R2_ACCESS_KEY_ID')
        R2_SECRET_ACCESS_KEY = config('R2_SECRET_ACCESS_KEY')
        R2_BUCKET_NAME = config('R2_BUCKET_NAME')
        R2_PUBLIC_BASE_URL = config('R2_PUBLIC_BASE_URL', default='').strip().rstrip('/')
        R2_S3_API_HOST = f'{R2_ACCOUNT_ID}.r2.cloudflarestorage.com'

        AWS_ACCESS_KEY_ID = R2_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY = R2_SECRET_ACCESS_KEY
        AWS_STORAGE_BUCKET_NAME = R2_BUCKET_NAME
        AWS_S3_REGION_NAME = 'auto'
        AWS_S3_ENDPOINT_URL = f'https://{R2_S3_API_HOST}'
        if R2_PUBLIC_BASE_URL:
            AWS_S3_CUSTOM_DOMAIN = R2_PUBLIC_BASE_URL.replace('https://', '').replace('http://', '')
    else:
        raise ImproperlyConfigured(
            'OBJECT_STORAGE_PROVIDER debe ser "aws" (Amazon S3) o "r2" (Cloudflare R2), '
            'o desactiva USE_S3_STATIC / USE_S3_MEDIA.'
        )

    if USE_S3_MEDIA or USE_S3_STATIC:
        if not (AWS_STORAGE_BUCKET_NAME or '').strip():
            raise ImproperlyConfigured(
                'Configura el bucket (AWS_STORAGE_BUCKET_NAME o variables R2_*) cuando '
                'USE_S3_MEDIA o USE_S3_STATIC están activos.'
            )


def _s3_virtual_host_base(bucket: str, region: str) -> str:
    bucket = (bucket or '').strip()
    region = (region or 'us-east-1').strip()
    if region == 'us-east-1':
        return f'{bucket}.s3.amazonaws.com'
    return f'{bucket}.s3.{region}.amazonaws.com'


if USE_S3_STATIC:
    STATICFILES_STORAGE = 'total_living.storage_backends.StaticStorage'
    if AWS_S3_CUSTOM_DOMAIN:
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
    elif OBJECT_STORAGE_PROVIDER == 'r2':
        STATIC_URL = f'https://{R2_S3_API_HOST}/{R2_BUCKET_NAME}/{AWS_STATIC_LOCATION}/'
    else:
        host = _s3_virtual_host_base(AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME)
        STATIC_URL = f'https://{host}/{AWS_STATIC_LOCATION}/'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if USE_S3_MEDIA:
    DEFAULT_FILE_STORAGE = 'total_living.storage_backends.MediaStorage'
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}/'
    elif OBJECT_STORAGE_PROVIDER == 'r2':
        MEDIA_URL = f'https://{R2_S3_API_HOST}/{R2_BUCKET_NAME}/{AWS_MEDIA_LOCATION}/'
    else:
        host = _s3_virtual_host_base(AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME)
        MEDIA_URL = f'https://{host}/{AWS_MEDIA_LOCATION}/'

if USE_S3_MEDIA and SERVE_LOCAL_MEDIA:
    raise ImproperlyConfigured(
        'USE_S3_MEDIA=True junto con SERVE_LOCAL_MEDIA=True no es válido: el media debe servirse '
        'solo desde el bucket (desactiva SERVE_LOCAL_MEDIA).'
    )

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'no-reply@example.com')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
