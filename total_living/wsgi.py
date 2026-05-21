"""
WSGI config for total_living project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.production')

application = get_wsgi_application()
