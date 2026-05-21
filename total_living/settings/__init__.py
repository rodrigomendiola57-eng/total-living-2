from pathlib import Path

from dotenv import load_dotenv

# Misma raíz que BASE_DIR en base.py: cargar .env antes de cualquier config()
# (decouple/cwd pueden fallar si el proceso no arranca desde el directorio del proyecto).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_env_file = _PROJECT_ROOT / '.env'
if _env_file.is_file():
    load_dotenv(_env_file, override=True)

from decouple import config

# Determinar el entorno
ENVIRONMENT = config('ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'staging':
    from .staging import *
else:
    from .development import *
