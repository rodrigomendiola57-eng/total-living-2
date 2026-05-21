import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from properties.models import Property

# Marcar las primeras 4 propiedades como destacadas
properties = Property.objects.filter(status='disponible').order_by('-created_at')[:4]

count = 0
for prop in properties:
    prop.is_featured = True
    prop.save()
    count += 1
    print(f"[+] Propiedad marcada como destacada: {prop.title}")

print(f"\nTotal: {count} propiedades marcadas como destacadas")
print("Ahora aparecerán en el carrusel principal!")
