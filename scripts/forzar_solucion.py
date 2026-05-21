"""
Script que fuerza la creación de la base de datos en el lugar correcto
y verifica que todo esté funcionando
"""
import os
import sys
import sqlite3

# Forzar cambio al directorio correcto
project_dir = "C:\\TOTAL LIVING"
os.chdir(project_dir)
sys.path.insert(0, project_dir)

print("=" * 70)
print("FORZANDO SOLUCION - TOTAL LIVING")
print("=" * 70)
print(f"Directorio del proyecto: {project_dir}")
print(f"Directorio actual: {os.getcwd()}")
print()

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')

import django
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# Obtener ruta de la base de datos
db_path = settings.DATABASES['default']['NAME']
print(f"Ruta de la base de datos: {db_path}")
print(f"Base de datos existe: {os.path.exists(db_path)}")
print()

# Paso 1: Eliminar base de datos si existe (para empezar limpio)
if os.path.exists(db_path):
    print("Eliminando base de datos antigua...")
    try:
        os.remove(db_path)
        print("[OK] Base de datos eliminada")
    except Exception as e:
        print(f"[ERROR] No se pudo eliminar: {e}")
print()

# Paso 2: Aplicar migraciones
print("=" * 70)
print("APLICANDO MIGRACIONES")
print("=" * 70)
print()

try:
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    print()
    print("[OK] Migraciones aplicadas")
except Exception as e:
    print(f"[ERROR] Error al aplicar migraciones: {e}")
    print()
    print("Intentando método alternativo...")
    import subprocess
    result = subprocess.run(
        ['python', 'manage.py', 'migrate', '--run-syncdb'],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("Errores:", result.stderr)

print()

# Paso 3: Verificar que auth_user existe
print("=" * 70)
print("VERIFICANDO BASE DE DATOS")
print("=" * 70)
print()

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"Tablas encontradas: {len(tables)}")
    print(f"Tablas: {', '.join(sorted(tables))}")
    print()
    
    if 'auth_user' in tables:
        print("[OK] La tabla auth_user existe correctamente")
        
        # Verificar superusuario
        try:
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
                print("[OK] Superusuario creado")
            else:
                print("[OK] Ya existe un superusuario")
        except Exception as e:
            print(f"[ERROR] Error al verificar/crear superusuario: {e}")
    else:
        print("[ERROR] La tabla auth_user NO existe")
        print("Esto indica que las migraciones no se aplicaron correctamente")
else:
    print(f"[ERROR] La base de datos no existe en: {db_path}")
    print("Las migraciones no se ejecutaron correctamente")

print()
print("=" * 70)
print("RESUMEN")
print("=" * 70)
print(f"Base de datos: {db_path}")
print(f"Existe: {os.path.exists(db_path)}")
if os.path.exists(db_path):
    print(f"Tamaño: {os.path.getsize(db_path)} bytes")
print()

if os.path.exists(db_path) and 'auth_user' in tables:
    print("[OK] TODO ESTA CORRECTO")
    print()
    print("=" * 70)
    print("INSTRUCCIONES FINALES")
    print("=" * 70)
    print("1. CIERRA TODAS las terminales donde corre el servidor")
    print("2. Abre UNA NUEVA terminal PowerShell")
    print("3. Ejecuta:")
    print("   cd 'C:\\TOTAL LIVING'")
    print("   python manage.py runserver 8080")
    print()
    print("4. Accede a: http://127.0.0.1:8080/admin/")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("=" * 70)
else:
    print("[ERROR] HAY PROBLEMAS CON LA BASE DE DATOS")
    print("Ejecuta manualmente:")
    print("  cd 'C:\\TOTAL LIVING'")
    print("  python manage.py migrate")
    print("  python crear_superusuario.py")
