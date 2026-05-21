"""
WSGI config for total_living project on PythonAnywhere.
"""

import os
import sys

# Agregar el directorio del proyecto al path
path = '/home/yourusername/total_living'  # Cambiar 'yourusername' por tu usuario
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()