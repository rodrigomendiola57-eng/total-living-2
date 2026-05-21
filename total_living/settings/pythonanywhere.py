"""
Configuración para PythonAnywhere
"""
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['rodrigomendiola.pythonanywhere.com', 'www.rodrigomendiola.pythonanywhere.com']

# Base de datos SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = '/home/RodrigoMendiola/total_living/staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/RodrigoMendiola/total_living/media'

# Security
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False