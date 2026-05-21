from django.db import connection

# Limpiar coordenadas inválidas directamente en SQL
with connection.cursor() as cursor:
    cursor.execute("UPDATE properties_property SET latitude = NULL, longitude = NULL WHERE latitude = '' OR longitude = '' OR latitude IS NOT NULL")
    print(f"Limpiadas {cursor.rowcount} propiedades")
