"""
Endpoints ligeros para balanceadores y orquestadores (ALB, Kubernetes, etc.).

- /health/live/  — proceso arriba (sin I/O pesado).
- /health/ready/ — aplicación puede atender tráfico (comprueba la base de datos).
"""

import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_live(request):
    return JsonResponse({'status': 'live'})


def health_ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        logger.exception('Health ready: fallo de base de datos')
        return JsonResponse({'status': 'not_ready', 'database': 'error'}, status=503)
    return JsonResponse({'status': 'ready', 'database': 'ok'})
