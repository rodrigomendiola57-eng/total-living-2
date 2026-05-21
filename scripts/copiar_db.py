# Script para copiar la base de datos a C:\Users\rodri
import os
import shutil
import sqlite3

source_db = "C:\\TOTAL LIVING\\db.sqlite3"
target_db = "C:\\Users\\rodri\\db.sqlite3"

print("=" * 70)
print("COPIANDO BASE DE DATOS")
print("=" * 70)
print()

if not os.path.exists(source_db):
    print("ERROR: No se encuentra la base de datos fuente")
    exit(1)

print("Copiando base de datos...")
if os.path.exists(target_db):
    os.remove(target_db)

shutil.copy2(source_db, target_db)
print("[OK] Base de datos copiada")

# Verificar
conn = sqlite3.connect(target_db)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
conn.close()

print(f"[OK] Tablas: {len(tables)}")
print(f"[OK] auth_user existe: {'auth_user' in tables}")
print()
print("Base de datos copiada correctamente!")
print("Reinicia el servidor y prueba de nuevo.")
