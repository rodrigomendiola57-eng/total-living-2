"""
Script para actualizar propiedades existentes con el campo process
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from properties.models import Property, PropertyProcess

# Actualizar todas las propiedades que no tengan proceso asignado
properties = Property.objects.filter(process__isnull=True) | Property.objects.filter(process='')
count = 0

for property in properties:
    # Asignar proceso según el estado
    if property.status == 'vendida' or property.status == 'rentada':
        property.process = PropertyProcess.CERRADO
    elif property.status == 'reservada':
        property.process = PropertyProcess.EN_NEGOCIACION
    else:
        property.process = PropertyProcess.EN_BUSQUEDA
    
    property.save()
    count += 1
    print(f"Actualizada propiedad {property.id}: {property.title} -> {property.get_process_display()}")

print(f"\nTotal de propiedades actualizadas: {count}")
