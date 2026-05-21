"""
Script para aplicar la migración del campo process directamente a la base de datos
"""
import sqlite3
import os

# Conectar a la base de datos
db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Error: No se encontró la base de datos en {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar si el campo ya existe
    cursor.execute('PRAGMA table_info(properties_property)')
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'process' in columns:
        print("El campo 'process' ya existe en la tabla.")
    else:
        # Agregar el campo process
        cursor.execute('''
            ALTER TABLE properties_property 
            ADD COLUMN process VARCHAR(30) DEFAULT 'en_busqueda'
        ''')
        conn.commit()
        print("[OK] Campo 'process' agregado exitosamente a la tabla properties_property")
        
        # Actualizar propiedades existentes según su estado
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
        print("[OK] Propiedades existentes actualizadas con valores de proceso")
        
        # Verificar
        cursor.execute('SELECT COUNT(*) FROM properties_property')
        count = cursor.fetchone()[0]
        print(f"[OK] Total de propiedades en la base de datos: {count}")
        
except sqlite3.Error as e:
    print(f"Error al aplicar la migración: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n[OK] Migracion aplicada exitosamente!")
