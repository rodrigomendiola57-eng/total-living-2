from pathlib import Path

from dotenv import load_dotenv

# Misma raíz que BASE_DIR en base.py: cargar .env antes de cualquier config()
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_env_file = _PROJECT_ROOT / '.env'
if _env_file.is_file():
    load_dotenv(_env_file, override=True)

import os

from decouple import config

# Al importar total_living.settings.production, Python ejecuta este __init__ primero.
# Respetar DJANGO_SETTINGS_MODULE evita cargar development (y su DATABASE_URL) en Render.
_django_settings = (os.environ.get('DJANGO_SETTINGS_MODULE') or '').strip()
if _django_settings.endswith('.production'):
    from .production import *
elif _django_settings.endswith('.staging'):
    from .staging import *
elif _django_settings.endswith('.development'):
    from .development import *
else:
    ENVIRONMENT = config('ENVIRONMENT', default='development')
    if ENVIRONMENT == 'production':
        from .production import *
    elif ENVIRONMENT == 'staging':
        from .staging import *
    else:
        from .development import *
