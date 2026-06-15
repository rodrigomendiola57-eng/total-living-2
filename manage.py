#!/usr/bin/env python
"""Django command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def _configure_settings_module() -> None:
    """Elige settings según entorno; Render siempre usa production."""
    if os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'total_living.settings.production'
        os.environ.setdefault('ENVIRONMENT', 'production')
        return

    env = (os.environ.get('ENVIRONMENT') or '').strip().lower()
    if env == 'production':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'total_living.settings.production'
        return
    if env == 'staging':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'total_living.settings.staging'
        return

    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        if (os.environ.get('RUNSERVER_USE_PRODUCTION') or '').strip() != '1':
            os.environ['DJANGO_SETTINGS_MODULE'] = 'total_living.settings.development'
            return

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')


def main():
    """Run administrative tasks."""
    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)
    _configure_settings_module()

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
