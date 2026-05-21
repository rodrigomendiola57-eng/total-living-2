"""
Script para verificar y agregar el campo process si no existe
"""
import sqlite3
import os

# Ruta de la base de datos según settings
DB_PATH = r'C:\TOTAL LIVING\db.sqlite3'

if not os.path.exists(DB_PATH):
    print(f"Error: No se encontro la base de datos en {DB_PATH}")
    exit(1)

print(f"Verificando base de datos: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Verificar si el campo ya existe
    cursor.execute('PRAGMA table_info(properties_property)')
    columns = [(row[1], row[2]) for row in cursor.fetchall()]
    column_names = [row[0] for row in columns]
    
    print(f"\nColumnas actuales en properties_property:")
    for name, type in columns:
        print(f"  - {name}: {type}")
    
    if 'process' in column_names:
        print("\n[OK] El campo 'process' ya existe en la tabla.")
        
        # Verificar valores
        cursor.execute('SELECT COUNT(*) FROM properties_property WHERE process IS NULL OR process = ""')
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"[INFO] Hay {null_count} propiedades sin proceso asignado")
            cursor.execute('''
                UPDATE properties_property 
                SET process = CASE 
                    WHEN status = 'vendida' OR status = 'rentada' THEN 'cerrado'
                    WHEN status = 'reservada' THEN 'en_negociacion'
                    ELSE 'en_busqueda'
                END
                WHERE process IS NULL OR process = ''
            ''')
            conn.commit()
            print("[OK] Propiedades actualizadas con valores de proceso")
    else:
        print("\n[INFO] El campo 'process' NO existe. Agregandolo...")
        
        # Agregar el campo process
        cursor.execute('''
            ALTER TABLE properties_property 
            ADD COLUMN process VARCHAR(30) DEFAULT 'en_busqueda'
        ''')
        conn.commit()
        print("[OK] Campo 'process' agregado exitosamente")
        
        # Actualizar propiedades existentes según su estado
        cursor.execute('''
            UPDATE properties_property 
            SET process = CASE 
                WHEN status = 'vendida' OR status = 'rentada' THEN 'cerrado'
                WHEN status = 'reservada' THEN 'en_negociacion'
                ELSE 'en_busqueda'
            END
        ''')
        conn.commit()
        print("[OK] Propiedades existentes actualizadas con valores de proceso")
    
    # Verificar final
    cursor.execute('PRAGMA table_info(properties_property)')
    final_columns = [row[1] for row in cursor.fetchall()]
    print(f"\n[OK] Verificacion final: process existe = {'process' in final_columns}")
    
    # Contar propiedades
    cursor.execute('SELECT COUNT(*) FROM properties_property')
    count = cursor.fetchone()[0]
    print(f"[OK] Total de propiedades: {count}")
    
except sqlite3.Error as e:
    print(f"\n[ERROR] Error al aplicar la migracion: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n[OK] Proceso completado!")
