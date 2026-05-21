"""
Script para crear superusuario de forma no interactiva
Uso: python crear_superusuario.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Verificar si ya existe un superusuario
if User.objects.filter(is_superuser=True).exists():
    print("Ya existe un superusuario. Usa 'python manage.py createsuperuser' para crear otro.")
else:
    # Crear superusuario por defecto
    username = 'admin'
    email = 'admin@totalliving.com'
    password = 'admin123'  # Cambiar en producción
    
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    print("=" * 50)
    print("SUPERUSUARIO CREADO EXITOSAMENTE")
    print("=" * 50)
    print(f"Usuario: {username}")
    print(f"Email: {email}")
    print(f"Contraseña: {password}")
    print("=" * 50)
    print("\n[IMPORTANTE] Cambia la contraseña despues del primer login!")
    print("Accede a: http://127.0.0.1:8080/admin/")
