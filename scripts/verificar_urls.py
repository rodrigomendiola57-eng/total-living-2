"""
Script para verificar que las URLs estén funcionando correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from django.urls import reverse, resolve
from django.test import RequestFactory
from properties.views import property_list

print("=" * 70)
print("VERIFICANDO CONFIGURACION DE URLs")
print("=" * 70)
print()

# Verificar que la vista existe
print("1. Verificando vista property_list...")
try:
    print(f"   [OK] Vista importada: {property_list}")
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

# Verificar que el template existe
print("\n2. Verificando templates...")
template_paths = [
    "templates/base.html",
    "templates/properties/list.html",
    "templates/properties/detail.html",
]

for template_path in template_paths:
    exists = os.path.exists(template_path)
    status = "[OK]" if exists else "[ERROR]"
    print(f"   {status} {template_path}")

# Verificar URLs
print("\n3. Verificando URLs...")
try:
    factory = RequestFactory()
    request = factory.get('/')
    request.META['HTTP_HOST'] = '127.0.0.1:8080'
    
    # Intentar resolver la URL
    match = resolve('/')
    print(f"   [OK] URL '/' resuelve a: {match.view_name}")
    print(f"   [OK] Vista: {match.func}")
    
    # Verificar reverse
    url = reverse('properties:list')
    print(f"   [OK] Reverse 'properties:list' = '{url}'")
    
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("INSTRUCCIONES:")
print("=" * 70)
print("1. Deten el servidor (Ctrl+C)")
print("2. Reinicia el servidor:")
print("   python manage.py runserver 8080")
print("3. Accede a: http://127.0.0.1:8080/")
print("=" * 70)
