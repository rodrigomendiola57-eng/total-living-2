"""
Script para verificar y corregir la base de datos
"""
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from total_living.settings.development import BASE_DIR, DATABASES

db_path = DATABASES['default']['NAME']
print(f"Ruta de la base de datos: {db_path}")
print(f"Base de datos existe: {os.path.exists(db_path)}")
print()

# Verificar tablas
if os.path.exists(db_path):
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tablas encontradas ({len(tables)}):")
    for table in sorted(tables):
        print(f"  - {table}")
    conn.close()
    
    # Verificar si auth_user existe
    if 'auth_user' in tables:
        print("\n[OK] La tabla auth_user existe")
    else:
        print("\n[ERROR] La tabla auth_user NO existe")
        print("Ejecuta: python manage.py migrate")
else:
    print("[ERROR] La base de datos no existe")
    print("Ejecuta: python manage.py migrate")
