"""
Script que crea la base de datos en C:\Users\rodri\db.sqlite3
para que funcione cuando el servidor se ejecuta desde ahí
"""
import os
import sys
import django

# Intentar desde C:\Users\rodri primero
possible_dirs = [
    "C:\\Users\\rodri",
    "C:\\TOTAL LIVING"
]

for project_dir in possible_dirs:
    if os.path.exists(project_dir):
        os.chdir(project_dir)
        sys.path.insert(0, project_dir)
        
        # Buscar manage.py
        if os.path.exists("manage.py"):
            print(f"Trabajando desde: {project_dir}")
            break
        elif os.path.exists(os.path.join(project_dir, "manage.py")):
            print(f"Trabajando desde: {project_dir}")
            break
else:
    # Si no encontramos, usar C:\TOTAL LIVING
    project_dir = "C:\\TOTAL LIVING"
    os.chdir(project_dir)
    sys.path.insert(0, project_dir)
    print(f"Usando directorio por defecto: {project_dir}")

print(f"Directorio actual: {os.getcwd()}")
print()

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')

try:
    django.setup()
except Exception as e:
    print(f"Error al configurar Django: {e}")
    print("Intentando desde C:\\TOTAL LIVING...")
    os.chdir("C:\\TOTAL LIVING")
    sys.path.insert(0, "C:\\TOTAL LIVING")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
    django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings

print("=" * 60)
print("CREANDO BASE DE DATOS")
print("=" * 60)
print()

# Obtener la ruta de la base de datos
db_path = settings.DATABASES['default']['NAME']
print(f"Ruta de la base de datos: {db_path}")
print(f"Base de datos existe: {os.path.exists(db_path)}")
print()

# Si la base de datos no existe o está vacía, crearla
if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
    print("La base de datos no existe o está vacía. Creando...")
    if os.path.exists(db_path):
        os.remove(db_path)
else:
    print("La base de datos ya existe. Verificando tablas...")
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if 'auth_user' in tables:
            print("[OK] La tabla auth_user ya existe")
            print()
            print("=" * 60)
            print("BASE DE DATOS CORRECTA")
            print("=" * 60)
            print(f"Ubicación: {db_path}")
            print(f"Tablas: {len(tables)}")
            print()
            print("El servidor debería funcionar ahora.")
            print("Si el error persiste, reinicia el servidor.")
            sys.exit(0)
    except Exception as e:
        print(f"Error al verificar: {e}")

# Aplicar migraciones
print("Aplicando migraciones...")
print("-" * 60)

try:
    # Cambiar al directorio donde está manage.py
    manage_dir = r"C:\TOTAL LIVING"
    if os.path.exists(os.path.join(manage_dir, "manage.py")):
        original_dir = os.getcwd()
        os.chdir(manage_dir)
        
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        
        os.chdir(original_dir)
    else:
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
except Exception as e:
    print(f"Error: {e}")
    print()
    print("Intentando método alternativo...")
    
    # Método alternativo: ejecutar desde C:\TOTAL LIVING
    os.chdir("C:\\TOTAL LIVING")
    import subprocess
    result = subprocess.run(['python', 'manage.py', 'migrate', '--run-syncdb'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errores:", result.stderr)

# Verificar resultado
print()
print("=" * 60)
print("VERIFICACIÓN FINAL")
print("=" * 60)

if os.path.exists(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"Base de datos: {db_path}")
    print(f"Tablas encontradas: {len(tables)}")
    print()
    
    if 'auth_user' in tables:
        print("[OK] La tabla auth_user existe correctamente")
        
        # Verificar superusuario
        from django.contrib.auth import get_user_model
        User = get_user_model()
        superusers = User.objects.filter(is_superuser=True).count()
        print(f"Superusuarios: {superusers}")
        
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
        print("[ERROR] La tabla auth_user NO existe")
        print("Tablas encontradas:", tables)
else:
    print(f"[ERROR] La base de datos no existe en: {db_path}")

print()
print("=" * 60)
print("INSTRUCCIONES")
print("=" * 60)
print("1. Reinicia el servidor (Ctrl+C y luego python manage.py runserver 8080)")
print("2. Accede a: http://127.0.0.1:8080/admin/")
print("3. Usuario: admin")
print("4. Contraseña: admin123")
print("=" * 60)
