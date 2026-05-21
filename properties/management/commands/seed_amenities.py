from django.core.management.base import BaseCommand
from django.utils.text import slugify

from properties.models import Amenity, AmenityAlias, AmenityCategory


CATALOG = {
    'Seguridad': [('Seguridad 24/7', 'bi-shield-check'), ('Vigilancia privada', 'bi-person-check'), ('Acceso controlado', 'bi-door-closed'),
                  ('Caseta de vigilancia', 'bi-house-lock'), ('CCTV', 'bi-camera-video'), ('Video portero', 'bi-camera-reels'),
                  ('Interfón', 'bi-telephone'), ('Portón eléctrico', 'bi-door-open'), ('Acceso biométrico', 'bi-fingerprint'),
                  ('Acceso con tarjeta', 'bi-credit-card'), ('Concierge', 'bi-person-badge'), ('Lobby', 'bi-building'),
                  ('Recepción', 'bi-person-workspace'), ('Control visitas', 'bi-person-lines-fill'), ('Barda perimetral', 'bi-border'),
                  ('Botón de pánico', 'bi-exclamation-octagon'), ('Sistema contra incendios', 'bi-fire'),
                  ('Detectores humo', 'bi-cloud-haze2'), ('Rociadores automáticos', 'bi-droplet-half'), ('Salidas emergencia', 'bi-box-arrow-right')],
    'Movilidad / Estacionamiento': [('Estacionamiento techado', 'bi-p-square'), ('Estacionamiento subterráneo', 'bi-p-square-fill'),
                                    ('Estacionamiento visitas', 'bi-car-front'), ('Valet parking', 'bi-car-front-fill'),
                                    ('Bike parking', 'bi-bicycle'), ('Bodega', 'bi-box-seam'), ('Carga eléctrica autos', 'bi-ev-station'),
                                    ('Car wash station', 'bi-droplet'), ('Motor lobby', 'bi-car-front'), ('Drop off zone', 'bi-sign-turn-right')],
    'Albercas / Wellness': [('Alberca', 'bi-water'), ('Alberca techada', 'bi-water'), ('Alberca climatizada', 'bi-thermometer-sun'),
                            ('Alberca infinity', 'bi-water'), ('Carril de nado', 'bi-water'), ('Chapoteadero', 'bi-water'),
                            ('Jacuzzi', 'bi-water'), ('Spa', 'bi-flower1'), ('Sauna', 'bi-thermometer-high'),
                            ('Vapor', 'bi-cloud-fog2'), ('Hidroterapia', 'bi-droplet-half'), ('Área de masajes', 'bi-hand-index'),
                            ('Asoleadero', 'bi-brightness-high'), ('Camas de sol', 'bi-sun'), ('Pool lounge', 'bi-lamp'),
                            ('Wet bar', 'bi-cup-straw')],
    'Fitness / Deporte': [('Gimnasio', 'bi-activity'), ('Gym exterior', 'bi-tree'), ('Crossfit zone', 'bi-activity'),
                          ('Yoga room', 'bi-person-standing'), ('Pilates studio', 'bi-person-standing'), ('Spinning room', 'bi-bicycle'),
                          ('Boxing room', 'bi-shield'), ('TRX area', 'bi-diagram-3'), ('Cancha pádel', 'bi-circle'),
                          ('Cancha tenis', 'bi-circle'), ('Cancha pickleball', 'bi-circle'), ('Cancha fútbol', 'bi-dribbble'),
                          ('Cancha basketball', 'bi-dribbble'), ('Cancha multiusos', 'bi-grid-3x3-gap'), ('Cancha voleibol', 'bi-dribbble'),
                          ('Frontón', 'bi-circle'), ('Squash', 'bi-circle'), ('Golf simulator', 'bi-bullseye'),
                          ('Putting green', 'bi-tree'), ('Running track', 'bi-signpost-2'), ('Trotapista', 'bi-signpost-2'),
                          ('Skate park', 'bi-triangle'), ('Muro escalar', 'bi-bricks')],
    'Social / Entretenimiento': [('Coworking', 'bi-laptop'), ('Business center', 'bi-building'), ('Sala juntas', 'bi-people'),
                                 ('Cine', 'bi-film'), ('Cinema room', 'bi-camera-reels'), ('Game room', 'bi-controller'),
                                 ('Arcade', 'bi-joystick'), ('Sports bar', 'bi-cup-straw'), ('Bar privado', 'bi-cup-hot'),
                                 ('Karaoke room', 'bi-mic'), ('Biblioteca', 'bi-book'), ('Reading room', 'bi-book-half'),
                                 ('Podcast room', 'bi-mic-fill'), ('Music room', 'bi-music-note-beamed'), ('Poker room', 'bi-suit-spade'),
                                 ('Billar', 'bi-circle-square'), ('Ping pong', 'bi-circle'), ('Teen room', 'bi-emoji-smile'),
                                 ('Adult room', 'bi-person'), ('Lounge', 'bi-lamp')],
    'Exterior': [('Rooftop', 'bi-building-up'), ('Roof garden', 'bi-flower2'), ('Terraza', 'bi-sun'),
                 ('Sky lounge', 'bi-clouds'), ('Mirador', 'bi-binoculars'), ('Fogatero', 'bi-fire'),
                 ('Fire pit', 'bi-fire'), ('Zona picnic', 'bi-basket2'), ('Jardín', 'bi-flower3'),
                 ('Áreas verdes', 'bi-tree-fill'), ('Parque central', 'bi-tree'), ('Huerto urbano', 'bi-flower1'),
                 ('Fuente decorativa', 'bi-droplet'), ('Senderos', 'bi-signpost-split'), ('Zona zen', 'bi-flower1'),
                 ('Hamacas', 'bi-layout-text-sidebar-reverse'), ('Pergolado', 'bi-columns-gap'), ('Palapas', 'bi-house'),
                 ('Deck exterior', 'bi-grid')],
    'Mascotas': [('Pet friendly', 'bi-heart'), ('Pet park', 'bi-tree'), ('Dog park', 'bi-tree-fill'),
                 ('Pet spa', 'bi-droplet-half'), ('Pet wash station', 'bi-droplet'), ('Grooming area', 'bi-scissors'),
                 ('Pet daycare', 'bi-house-heart')],
    'Infantil / Familiar': [('Juegos infantiles', 'bi-emoji-smile'), ('Kids club', 'bi-people'),
                            ('Ludoteca', 'bi-book'), ('Guardería', 'bi-house-heart'), ('Splash zone', 'bi-water'),
                            ('Mini golf', 'bi-bullseye'), ('Zona bebés', 'bi-emoji-smile-upside-down')],
    'Cocina / Convivencia': [('Asadores', 'bi-fire'), ('Zona BBQ', 'bi-fire'), ('Parrillas', 'bi-fire'),
                             ('Cocina exterior', 'bi-egg-fried'), ('Kitchen lounge', 'bi-cup-hot'), ('Comedor común', 'bi-people'),
                             ('Wine cellar', 'bi-cup'), ('Wine tasting room', 'bi-cup-straw'),
                             ('Chef kitchen', 'bi-egg-fried'), ('Private dining room', 'bi-table')],
    'Servicios': [('Elevador', 'bi-arrow-up-square'), ('Elevador servicio', 'bi-arrow-up-square-fill'), ('Montacargas', 'bi-boxes'),
                  ('Trash chute', 'bi-trash3'), ('Cuarto basura', 'bi-trash'), ('Laundry room', 'bi-basket3'),
                  ('Lavandería', 'bi-basket3-fill'), ('Dry cleaning', 'bi-droplet'), ('Housekeeping', 'bi-house-gear'),
                  ('Administración', 'bi-person-workspace'), ('Mantenimiento', 'bi-tools'), ('Paquetería', 'bi-box2'),
                  ('Mail room', 'bi-mailbox'), ('Lockers inteligentes', 'bi-safe'), ('Bodega privada', 'bi-box-seam')],
    'Infraestructura': [('Gas natural', 'bi-fire'), ('Boiler gas', 'bi-fire'), ('Calentador eléctrico', 'bi-lightning'),
                        ('Paneles solares', 'bi-sun'), ('Planta eléctrica', 'bi-lightning-charge'),
                        ('Generador emergencia', 'bi-lightning-charge-fill'), ('Cisterna', 'bi-droplet'),
                        ('Tinaco', 'bi-droplet-fill'), ('Hidroneumático', 'bi-droplet-half'),
                        ('Tratamiento agua', 'bi-funnel'), ('Captación pluvial', 'bi-cloud-rain'),
                        ('Fibra óptica', 'bi-broadcast'), ('WiFi áreas comunes', 'bi-wifi'),
                        ('Smart home', 'bi-house-gear'), ('Domótica', 'bi-cpu'), ('Aire acondicionado', 'bi-snow2'),
                        ('Preparación A/C', 'bi-snow'), ('Calefacción', 'bi-thermometer-high')],
    'Lujo / Premium': [('Residencias amuebladas', 'bi-house-check'), ('Servicio hotelero', 'bi-stars'),
                       ('Room service', 'bi-bell'), ('Private chef', 'bi-egg-fried'), ('Butler service', 'bi-person-badge'),
                       ('Helipuerto', 'bi-airplane'), ('Marina', 'bi-water'), ('Beach club', 'bi-umbrella'),
                       ('Club house', 'bi-house'), ('Club deportivo', 'bi-trophy'), ('Private lounge', 'bi-lamp'),
                       ('Cigar room', 'bi-cloud-smoke'), ('Whiskey room', 'bi-cup-straw'), ('Art gallery', 'bi-image'),
                       ('Office suites privadas', 'bi-building')],
    'Remote Work / Moderno': [('Phone booths', 'bi-telephone'), ('Zoom rooms', 'bi-camera-video'),
                              ('Podcast studio', 'bi-mic'), ('Creator studio', 'bi-camera'),
                              ('Content studio', 'bi-camera-reels'), ('Printing station', 'bi-printer'),
                              ('Meeting pods', 'bi-people'), ('High speed internet', 'bi-wifi')],
}

ALIASES = {
    'gimnasio': ['gym', 'fitness', 'gimnasio completo'],
    'alberca': ['pool', 'piscina'],
    'seguridad-24-7': ['seguridad 24 horas', 'vigilancia 24/7', 'security'],
    'coworking': ['cowork', 'business center', 'co-working'],
    'pet-friendly': ['dog friendly', 'mascotas', 'pet park'],
}


class Command(BaseCommand):
    help = 'Carga/actualiza catálogo maestro de amenidades y aliases'

    def handle(self, *args, **options):
        total_categories = 0
        total_amenities = 0
        total_aliases = 0

        for category_name, amenities in CATALOG.items():
            category_slug = slugify(category_name)
            category, created = AmenityCategory.objects.get_or_create(
                slug=category_slug,
                defaults={
                    'name': category_name,
                    'icon': 'bi-grid-1x2',
                    'description': f'Categoría {category_name}',
                    'sort_order': total_categories,
                },
            )
            if created:
                total_categories += 1

            for index, (display_name, icon) in enumerate(amenities):
                amenity_slug = slugify(display_name)
                amenity, created_amenity = Amenity.objects.get_or_create(
                    slug=amenity_slug,
                    defaults={
                        'name': display_name.lower(),
                        'display_name': display_name,
                        'category': category,
                        'icon': icon,
                        'description': '',
                        'is_active': True,
                        'is_premium': category_name in {'Lujo / Premium'},
                        'priority_score': max(0, 100 - index),
                    },
                )
                if created_amenity:
                    total_amenities += 1
                else:
                    dirty = False
                    if amenity.category_id != category.id:
                        amenity.category = category
                        dirty = True
                    if amenity.display_name != display_name:
                        amenity.display_name = display_name
                        dirty = True
                    if not amenity.icon:
                        amenity.icon = icon
                        dirty = True
                    if dirty:
                        amenity.save()

        for amenity_slug, aliases in ALIASES.items():
            amenity = Amenity.objects.filter(slug=amenity_slug).first()
            if not amenity:
                continue
            for alias in aliases:
                alias_slug = slugify(alias)
                _, created_alias = AmenityAlias.objects.get_or_create(
                    alias_slug=alias_slug,
                    defaults={'amenity': amenity, 'alias_name': alias},
                )
                if created_alias:
                    total_aliases += 1

        self.stdout.write(self.style.SUCCESS(
            f'Catálogo listo. Categorías nuevas: {total_categories}, amenidades nuevas: {total_amenities}, aliases nuevos: {total_aliases}.'
        ))
