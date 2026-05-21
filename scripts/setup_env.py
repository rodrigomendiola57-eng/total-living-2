"""
Script para generar SECRET_KEY y crear archivo .env
Ejecutar: python setup_env.py
"""
from django.core.management.utils import get_random_secret_key
import os

# Generar SECRET_KEY
secret_key = get_random_secret_key()

# Contenido del archivo .env
env_content = f"""# Django
SECRET_KEY={secret_key}
DEBUG=True
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Desarrollo - SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Database (Producción - PostgreSQL)
# DATABASE_URL=postgresql://user:password@host:port/dbname

# AWS S3 (Producción)
# AWS_ACCESS_KEY_ID=tu-access-key
# AWS_SECRET_ACCESS_KEY=tu-secret-key
# AWS_STORAGE_BUCKET_NAME=tu-bucket-name
# AWS_S3_REGION_NAME=us-east-1

# Email (Opcional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=tu-email@gmail.com
# EMAIL_HOST_PASSWORD=tu-password
"""

# Crear archivo .env si no existe
if not os.path.exists('.env'):
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("[OK] Archivo .env creado exitosamente!")
    print(f"[OK] SECRET_KEY generada: {secret_key[:20]}...")
else:
    print("[AVISO] El archivo .env ya existe. No se sobrescribio.")
    print("Si deseas regenerar la SECRET_KEY, elimina el archivo .env y ejecuta este script nuevamente.")
