"""
Sube static/videos/nosotros-hero.mp4 al prefijo static/ del bucket R2 (misma ruta que collectstatic).

Requisitos: producción con USE_S3_STATIC=True, credenciales R2 en .env.

  python manage.py upload_nosotros_hero_video

Al terminar, copia la URL que imprime a NOSOTROS_HERO_VIDEO_URL si el navegador no reproduce
(política pública del objeto o CORS con GET/HEAD y Range).
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Sube nosotros-hero.mp4 a R2 (StaticStorage).'

    def handle(self, *args, **options):
        if settings.STATICFILES_STORAGE != 'total_living.storage_backends.StaticStorage':
            raise CommandError(
                'Activa USE_S3_STATIC=True y configura R2 (o sirve el MP4 desde /static/ tras collectstatic).'
            )

        from total_living.storage_backends import StaticStorage

        rel_key = 'videos/nosotros-hero.mp4'
        src = Path(settings.BASE_DIR) / 'static' / rel_key
        if not src.is_file():
            raise CommandError(f'No existe: {src}')

        storage = StaticStorage()
        self.stdout.write(f'Subiendo {src.name} (~{src.stat().st_size // (1024 * 1024)} MB)...')
        with src.open('rb') as fh:
            saved = storage.save(rel_key, File(fh))

        url = storage.url(saved)
        self.stdout.write(self.style.SUCCESS(url))
        self.stdout.write('Añade en .env si hace falta: NOSOTROS_HERO_VIDEO_URL=' + url)
