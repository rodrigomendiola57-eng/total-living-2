import os
import django

os.chdir('C:\\TOTAL LIVING')
os.environ['DJANGO_SETTINGS_MODULE'] = 'total_living.settings.development'
django.setup()

from django.conf import settings
from django.urls import get_resolver

print("=" * 50)
print("DIAGNOSTICO DE URLS")
print("=" * 50)

print("\n1. ROOT_URLCONF:", settings.ROOT_URLCONF)

resolver = get_resolver()
print("\n2. URL Patterns cargados:")
for pattern in resolver.url_patterns:
    print(f"   - {pattern.pattern}")

print("\n3. Probando URL raiz '/':")
from django.urls import resolve
try:
    match = resolve('/')
    print(f"   Vista encontrada: {match.func.__name__}")
    print(f"   Modulo: {match.func.__module__}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n4. Verificando archivo urls.py:")
urls_file = 'C:\\TOTAL LIVING\\total_living\\urls.py'
with open(urls_file, 'r', encoding='utf-8') as f:
    content = f.read()
    if 'home_view' in content:
        print("   OK: home_view encontrado")
    if 'PropertyType, PropertyOperation' in content:
        print("   OK: Imports corregidos")
    else:
        print("   ERROR: Imports NO corregidos")
