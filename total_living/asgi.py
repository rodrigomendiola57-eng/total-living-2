"""
ASGI config for total_living project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.production')

application = get_asgi_application()
