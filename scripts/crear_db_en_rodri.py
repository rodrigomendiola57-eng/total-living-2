"""
Script para crear la base de datos también en C:\Users\rodri
por si el servidor se ejecuta desde ahí
"""
import os
import sys
import sqlite3
import shutil

# Directorios
source_dir = "C:\\TOTAL LIVING"
target_dir = "C:\\Users\\rodri"
source_db = os.path.join(source_dir, "db.sqlite3")
target_db = os.path.join(target_dir, "db.sqlite3")

print("=" * 70)
print("CREANDO BASE DE DATOS EN C:\\Users\\rodri")
print("=" * 70)
print()

# Verificar que la base de datos fuente existe
if not os.path.exists(source_db):
    print(f"[ERROR] No se encuentra la base de datos fuente: {source_db}")
    print("Ejecuta primero: python forzar_solucion.py")
    sys.exit(1)

print(f"Base de datos fuente: {source_db}")
print(f"Base de datos destino: {target_db}")
print()

# Copiar la base de datos
print("Copiando base de datos...")
try:
    # Si ya existe, eliminarla primero
    if os.path.exists(target_db):
        os.remove(target_db)
        print("[OK] Base de datos antigua eliminada")
    
    # Copiar
    shutil.copy2(source_db, target_db)
    print(f"[OK] Base de datos copiada a {target_db}")
    
    # Verificar
    if os.path.exists(target_db):
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"[OK] Base de datos verificada: {len(tables)} tablas")
        print(f"[OK] auth_user existe: {'auth_user' in tables}")
        
except Exception as e:
    print(f"[ERROR] Error al copiar: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("RESUMEN")
print("=" * 70)
print(f"Base de datos en C:\\TOTAL LIVING: {os.path.exists(source_db)}")
print(f"Base de datos en C:\\Users\\rodri: {os.path.exists(target_db)}")
print()
print("[OK] Ahora el servidor debería funcionar desde cualquier directorio")
print()
print("Reinicia el servidor y prueba de nuevo.")
print("=" * 70)
