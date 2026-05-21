"""
Script para poblar la base de datos con regiones iniciales de Querétaro
Ejecutar con: python manage.py shell < populate_regions.py
"""

from regions.models import Region

# Limpiar regiones existentes (opcional)
# Region.objects.all().delete()

regiones_data = [
    {
        "name": "Zibatá",
        "slug": "zibata",
        "description": "La primera comunidad planeada del estado de Querétaro. Se destaca por su urbanismo de primer nivel, amplias áreas verdes, seguridad 24/7 y un diseño arquitectónico que integra naturaleza y modernidad. Ideal para familias que buscan calidad de vida en un entorno exclusivo.",
        "highlights": "Campo de golf de 18 hoyos profesional, Universidad Anáhuac Querétaro, Plaza Xentric, Town Center, Parques caninos, Ciclovías y senderos, Seguridad privada 24/7",
        "growth_level": "alto",
        "order": 1,
        "is_active": True
    },
    {
        "name": "Juriquilla",
        "slug": "juriquilla",
        "description": "Zona con gran tradición y prestigio que combina arquitectura colonial con desarrollos modernos. Es el hub educativo y comercial del norte de Querétaro, consolidada como una de las zonas más exclusivas de la ciudad con excelente infraestructura.",
        "highlights": "Plaza Antea (centro comercial más grande), Campus UNAM y UAQ, Hospital Moscati, Club de Yates Juriquilla, Club de Golf La Loma, Múltiples colegios privados, Zona gastronómica",
        "growth_level": "alto",
        "order": 2,
        "is_active": True
    },
    {
        "name": "El Refugio",
        "slug": "el-refugio",
        "description": "Ubicación estratégica sobre el Anillo Vial Fray Junípero Serra. Es la zona favorita para familias jóvenes por su excelente conectividad, cercanía a servicios y desarrollo comercial en constante crecimiento. Ofrece opciones residenciales para todos los presupuestos.",
        "highlights": "Paseo Querétaro (centro comercial), Hospital IMSS El Marqués, HEB y Costco, Colegio Maple Grove, Lagos artificiales y parques, Canchas de pádel, Excelente conectividad vial",
        "growth_level": "alto",
        "order": 3,
        "is_active": True
    },
    {
        "name": "Ciudad Maderas",
        "slug": "ciudad-maderas",
        "description": "Ubicada en el corredor industrial y tecnológico de Querétaro. Es el epicentro de inversión inmobiliaria con enfoque en sustentabilidad y tecnología. Ideal para ejecutivos y profesionistas que trabajan en el sector industrial y tecnológico de la región.",
        "highlights": "Universidad Mondragón, Bio-Parque tecnológico, Aeropuerto Internacional a 15 min, Parques Industriales cercanos, Diseño sustentable, Clubes deportivos con albercas, Preventa con alta plusvalía",
        "growth_level": "alto",
        "order": 4,
        "is_active": True
    },
    {
        "name": "Milenio III",
        "slug": "milenio-iii",
        "description": "Zona céntrica y ejecutiva con excelente ubicación en el corazón de Querétaro. Ofrece acceso rápido a las principales vialidades, centros comerciales y servicios médicos. Perfecta para profesionistas que buscan vivir cerca de todo.",
        "highlights": "Superama y tiendas de conveniencia, Cercanía a Los Arcos, Hospital General a 10 min, Acceso rápido a Bernardo Quintana, Zona consolidada, Plusvalía estable, Opciones de departamentos y casas",
        "growth_level": "medio",
        "order": 5,
        "is_active": True
    },
    {
        "name": "Corregidora",
        "slug": "corregidora",
        "description": "Municipio en rápido crecimiento al sur de Querétaro. Ofrece opciones residenciales más accesibles con excelente proyección de plusvalía. Ideal para inversión y primera vivienda, con desarrollo de infraestructura comercial y educativa en expansión.",
        "highlights": "Precios más accesibles, Alta proyección de plusvalía, Nuevos desarrollos comerciales, Cercanía a Querétaro Centro, Opciones de terrenos amplios, Ambiente familiar, Crecimiento acelerado",
        "growth_level": "alto",
        "order": 6,
        "is_active": True
    },
    {
        "name": "Huimilpan (Zona Sur)",
        "slug": "huimilpan",
        "description": "Zona campestre y de lujo al sur de Querétaro. Ofrece desarrollos exclusivos en entornos naturales con amplios terrenos. Ideal para quienes buscan tranquilidad, privacidad y contacto con la naturaleza sin alejarse de la ciudad.",
        "highlights": "Cañadas del Lago, Entorno natural privilegiado, Terrenos amplios, Cercanía a Centro Cívico, Desarrollos campestres exclusivos, Aire puro y tranquilidad, Inversión de alto nivel",
        "growth_level": "medio",
        "order": 7,
        "is_active": True
    },
    {
        "name": "Centro Histórico",
        "slug": "centro-historico",
        "description": "El corazón cultural y turístico de Querétaro. Zona Patrimonio de la Humanidad con arquitectura colonial, restaurantes, museos y vida nocturna. Ideal para inversión en departamentos tipo loft y propiedades con valor histórico.",
        "highlights": "Patrimonio de la Humanidad UNESCO, Arquitectura colonial, Zona gastronómica, Museos y teatros, Vida nocturna, Inversión turística, Departamentos tipo loft",
        "growth_level": "medio",
        "order": 8,
        "is_active": True
    },
    {
        "name": "Santa Fe",
        "slug": "santa-fe",
        "description": "Zona residencial consolidada con excelente ubicación y servicios. Ofrece opciones de vivienda tradicional en una de las áreas más establecidas de Querétaro. Perfecta para familias que buscan estabilidad y cercanía a todo.",
        "highlights": "Zona consolidada, Cercanía a hospitales, Colegios tradicionales, Centros comerciales, Transporte público, Plusvalía estable, Ambiente familiar",
        "growth_level": "medio",
        "order": 9,
        "is_active": True
    },
    {
        "name": "El Pueblito",
        "slug": "el-pueblito",
        "description": "Zona emergente con gran potencial de crecimiento. Ubicada estratégicamente entre Corregidora y el Centro de Querétaro. Ofrece opciones accesibles con proyección de desarrollo comercial e industrial cercano.",
        "highlights": "Precios competitivos, Proyección de crecimiento, Desarrollo industrial cercano, Nuevos fraccionamientos, Acceso a carreteras principales, Primera vivienda, Inversión a mediano plazo",
        "growth_level": "emergente",
        "order": 10,
        "is_active": True
    }
]

print("Iniciando población de regiones...")
print("-" * 50)

for data in regiones_data:
    region, created = Region.objects.get_or_create(
        slug=data['slug'],
        defaults=data
    )
    
    if created:
        print(f"✓ Creada: {region.name}")
    else:
        print(f"○ Ya existe: {region.name}")

print("-" * 50)
print(f"Total de regiones en base de datos: {Region.objects.count()}")
print("¡Proceso completado!")
