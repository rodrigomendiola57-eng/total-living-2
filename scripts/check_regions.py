"""
Script para corregir encoding de regiones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from regions.models import Region

print("Corrigiendo encoding de regiones...")
print("-" * 50)

regions = Region.objects.all()
for region in regions:
    print(f"Región: {region.name}")
    print(f"  Descripción: {region.description[:50]}...")
    print(f"  Highlights: {region.highlights[:50]}...")
    print()

print("-" * 50)
print(f"Total: {regions.count()} regiones")
