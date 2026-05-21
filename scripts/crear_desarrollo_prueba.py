#!/usr/bin/env python
"""
Script para crear un desarrollo de prueba en la base de datos.
Uso: python crear_desarrollo_prueba.py
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

from developments.models import Development, DevelopmentImage
from django.utils import timezone

def crear_desarrollo_prueba(crear_nuevo=False):
    """Crear un desarrollo de prueba para el carrusel"""
    
    # Verificar si ya existe un desarrollo de prueba
    desarrollo_existente = Development.objects.filter(name__icontains='prueba').first()
    if desarrollo_existente and not crear_nuevo:
        print(f"[INFO] Ya existe un desarrollo de prueba: '{desarrollo_existente.name}' (ID: {desarrollo_existente.id})")
        print(f"Puedes gestionar sus imagenes desde: http://127.0.0.1:8090/developments/panel/{desarrollo_existente.id}/images/")
        return desarrollo_existente
    
    print("\n" + "="*60)
    print("CREAR DESARROLLO DE PRUEBA - TOTAL LIVING")
    print("="*60)
    print("\nEste script creara un desarrollo de prueba en la base de datos.")
    print("Las imagenes deberas agregarlas desde el panel de administracion.")
    print("\n" + "-"*60)
    
    # Datos del desarrollo de prueba
    # Datos del desarrollo de prueba
    desarrollo = Development(
        name="Desarrollo Residencial Exclusivo - Prueba",
        description="Desarrollo residencial de lujo ubicado en la zona mas exclusiva de la ciudad. Proyecto arquitectonico de vanguardia con acabados premium y amenidades de clase mundial. Cada unidad esta diseñada pensando en el confort y la elegancia, con espacios amplios y luminosos. Cuenta con areas verdes, gimnasio, alberca, areas de esparcimiento y seguridad 24/7.",
        location="Av. Principal #123, Colonia Exclusiva",
        city="Ciudad de Mexico",
        state="CDMX",
        google_maps_url="https://maps.app.goo.gl/example",
        operation_type="venta",
        total_units=120,
        available_units=85,
        price_from=4500000.00,
        delivery_date=timezone.now().date() + timedelta(days=365),  # 1 año desde ahora
        is_active=True,
        is_featured=True,  # Destacado para que aparezca en el carrusel
    )
    
    desarrollo.save()
    
    print(f"\n[EXITO] Desarrollo creado exitosamente!")
    print(f"\n--- Informacion del Desarrollo ---")
    print(f"   ID: {desarrollo.id}")
    print(f"   Nombre: {desarrollo.name}")
    print(f"   Ubicacion: {desarrollo.location}, {desarrollo.city}, {desarrollo.state}")
    print(f"   Precio Desde: ${desarrollo.price_from:,.2f} MXN")
    print(f"   Unidades: {desarrollo.available_units}/{desarrollo.total_units}")
    print(f"   Estado: {'Activo' if desarrollo.is_active else 'Inactivo'}")
    print(f"   Destacado: {'Si' if desarrollo.is_featured else 'No'}")
    
    print(f"\n--- PROXIMOS PASOS PARA AGREGAR IMAGENES ---")
    print(f"   1. Accede al Panel de Gestion (icono de tuerca en el navbar)")
    print(f"   2. Ve a 'Gestion de Desarrollos'")
    print(f"   3. Haz clic en 'Imagenes' en el desarrollo recien creado (ID: {desarrollo.id})")
    print(f"   4. Sube las imagenes que quieras mostrar en el carrusel")
    print(f"   5. Establece la primera imagen como 'Principal'")
    
    print(f"\n--- URLs ---")
    print(f"   URL de Gestion de Imagenes:")
    print(f"   http://127.0.0.1:8090/developments/panel/{desarrollo.id}/images/")
    print(f"\n   URL para Ver el Desarrollo:")
    print(f"   http://127.0.0.1:8090/developments/")
    
    print("\n" + "="*60)
    print("Desarrollo de prueba creado exitosamente!")
    print("="*60 + "\n")
    
    return desarrollo

if __name__ == '__main__':
    try:
        desarrollo = crear_desarrollo_prueba()
    except Exception as e:
        print(f"\n[ERROR] Error al crear el desarrollo: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
