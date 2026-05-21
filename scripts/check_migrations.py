"""
Script para verificar y marcar migraciones como aplicadas
"""
import sqlite3
import os

DB_PATH = r'C:\TOTAL LIVING\db.sqlite3'

if not os.path.exists(DB_PATH):
    print(f"Error: No se encontro la base de datos en {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Verificar si existe la tabla de migraciones
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
    if not cursor.fetchone():
        print("La tabla django_migrations no existe")
    else:
        # Verificar migraciones de properties
        cursor.execute("SELECT app, name FROM django_migrations WHERE app='properties' ORDER BY id DESC LIMIT 10")
        migrations = cursor.fetchall()
        print("Migraciones de properties registradas:")
        for app, name in migrations:
            print(f"  - {name}")
        
        # Verificar si 0006 está registrada
        cursor.execute("SELECT * FROM django_migrations WHERE app='properties' AND name='0006_property_process'")
        if cursor.fetchone():
            print("\n[OK] La migracion 0006_property_process ya esta registrada")
        else:
            print("\n[INFO] La migracion 0006_property_process NO esta registrada")
            print("Agregandola a django_migrations...")
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('properties', '0006_property_process', datetime('now'))
            """)
            conn.commit()
            print("[OK] Migracion registrada exitosamente")
    
    # Verificar que el campo process existe
    cursor.execute("PRAGMA table_info(properties_property)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'process' in columns:
        print("\n[OK] El campo 'process' existe en la base de datos")
    else:
        print("\n[ERROR] El campo 'process' NO existe en la base de datos")
        
except sqlite3.Error as e:
    print(f"\n[ERROR] Error: {e}")
finally:
    conn.close()

print("\n[OK] Verificacion completada!")
