"""
Script para corregir el problema de la base de datos
Crea la base de datos en el directorio correcto y aplica todas las migraciones
"""
import os
import sys
import django

# Cambiar al directorio del proyecto
project_dir = r"C:\TOTAL LIVING"
os.chdir(project_dir)
sys.path.insert(0, project_dir)

print("=" * 60)
print("CORRIGIENDO BASE DE DATOS - TOTAL LIVING")
print("=" * 60)
print(f"Directorio del proyecto: {project_dir}")
print(f"Directorio actual: {os.getcwd()}")
print()

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from django.core.management import execute_from_command_line
from total_living.settings.development import DATABASES, BASE_DIR

db_path = DATABASES['default']['NAME']
print(f"Ruta de la base de datos: {db_path}")
print(f"Base de datos existe: {os.path.exists(db_path)}")
print()

# Eliminar base de datos si existe (opcional, comentado por seguridad)
# if os.path.exists(db_path):
#     print("Eliminando base de datos antigua...")
#     os.remove(db_path)

# Aplicar migraciones
print("Aplicando migraciones...")
print("-" * 60)
execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])

# Verificar que auth_user existe
import sqlite3
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if 'auth_user' in tables:
        print()
        print("=" * 60)
        print("[OK] La tabla auth_user existe correctamente")
        print("=" * 60)
        
        # Verificar si hay superusuario
        from django.contrib.auth import get_user_model
        User = get_user_model()
        superusers = User.objects.filter(is_superuser=True).count()
        print(f"Superusuarios encontrados: {superusers}")
        
        if superusers == 0:
            print()
            print("Creando superusuario...")
            User.objects.create_superuser(
                username='admin',
                email='admin@totalliving.com',
                password='admin123'
            )
            print("[OK] Superusuario creado:")
            print("     Usuario: admin")
            print("     Contraseña: admin123")
    else:
        print()
        print("=" * 60)
        print("[ERROR] La tabla auth_user NO existe")
        print("=" * 60)
        print("Intenta ejecutar manualmente:")
        print("  python manage.py migrate")
else:
    print()
    print("=" * 60)
    print("[ERROR] La base de datos no se creó")
    print("=" * 60)

print()
print("=" * 60)
print("INSTRUCCIONES:")
print("=" * 60)
print("1. Detén el servidor actual (Ctrl+C)")
print("2. Ejecuta: cd 'C:\\TOTAL LIVING'")
print("3. Ejecuta: python manage.py runserver 8080")
print("4. O usa: .\\iniciar_servidor.ps1")
print()
print("URL: http://127.0.0.1:8080/admin/")
print("Usuario: admin")
print("Contraseña: admin123")
print("=" * 60)
