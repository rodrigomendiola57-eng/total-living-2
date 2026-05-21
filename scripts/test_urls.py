"""
Script para probar que las URLs funcionan correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

print("=" * 70)
print("PROBANDO CONFIGURACION DE URLs")
print("=" * 70)
print()

# Probar importar URLs principales
try:
    from total_living.urls import urlpatterns
    print(f"[OK] total_living.urls importado: {len(urlpatterns)} patrones")
    for pattern in urlpatterns:
        print(f"     - {pattern.pattern}")
except Exception as e:
    print(f"[ERROR] Error al importar total_living.urls: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# Probar importar URLs de properties
try:
    from properties.urls import urlpatterns as prop_urls
    print(f"[OK] properties.urls importado: {len(prop_urls)} patrones")
except Exception as e:
    print(f"[ERROR] Error al importar properties.urls: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# Probar resolver URL raíz
try:
    from django.urls import resolve
    match = resolve('/')
    print(f"[OK] URL '/' resuelve correctamente")
    print(f"     Vista: {match.func}")
    print(f"     Nombre: {match.view_name}")
except Exception as e:
    print(f"[ERROR] Error al resolver '/': {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()
print("=" * 70)
print("[OK] TODAS LAS URLs ESTAN CONFIGURADAS CORRECTAMENTE")
print("=" * 70)
print()
print("Si ves el cohete de Django, el problema es que:")
print("1. El servidor está corriendo desde otro directorio")
print("2. El servidor necesita reiniciarse")
print()
print("SOLUCION:")
print("1. Deten el servidor (Ctrl+C)")
print("2. Ejecuta: cd 'C:\\TOTAL LIVING'")
print("3. Ejecuta: python manage.py runserver 8080")
print("=" * 70)
