"""Paquete de settings de Django.

Usar módulos explícitos en cada entorno:
- total_living.settings.development
- total_living.settings.staging
- total_living.settings.production
"""
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_env_file = _PROJECT_ROOT / '.env'
if _env_file.is_file():
    load_dotenv(_env_file, override=True)
