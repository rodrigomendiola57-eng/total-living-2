#!/usr/bin/env python
"""Django command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)

    # PowerShell/Cursor dejan DJANGO_SETTINGS_MODULE=production de sesiones anteriores;
    # `setdefault` NO lo sobrescribe → runserver carga prod y falla ALLOWED_HOSTS en local.
    # Para probar producción en runserver: RUNSERVER_USE_PRODUCTION=1 (PowerShell: $env:RUNSERVER_USE_PRODUCTION='1')
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        if (os.environ.get('RUNSERVER_USE_PRODUCTION') or '').strip() != '1':
            os.environ['DJANGO_SETTINGS_MODULE'] = 'total_living.settings.development'

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
