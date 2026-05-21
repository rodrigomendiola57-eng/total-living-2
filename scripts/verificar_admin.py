import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from django.contrib import admin

print("=" * 70)
print("MODELOS REGISTRADOS EN EL ADMIN")
print("=" * 70)
print()

models_registered = []
for model, admin_class in admin.site._registry.items():
    app_label = model._meta.app_label
    model_name = model.__name__
    models_registered.append((app_label, model_name))
    print(f"  - {app_label}.{model_name}")

print()
print(f"Total: {len(models_registered)} modelos registrados")
print()

# Verificar modelos esperados
expected_models = [
    ('properties', 'Property'),
    ('properties', 'PropertyImage'),
    ('properties', 'PropertyFeature'),
    ('properties', 'PropertyFeatureRelation'),
    ('contact', 'Contact'),
]

print("Verificando modelos esperados:")
for app, model in expected_models:
    found = (app, model) in models_registered
    status = "[OK]" if found else "[FALTA]"
    print(f"  {status} {app}.{model}")

print()
print("=" * 70)
if all((app, model) in models_registered for app, model in expected_models):
    print("[OK] Todos los modelos estan registrados correctamente")
    print("Si no los ves en el admin, recarga la pagina (F5)")
else:
    print("[ERROR] Faltan algunos modelos")
    print("Verifica que los archivos admin.py esten correctos")
print("=" * 70)
