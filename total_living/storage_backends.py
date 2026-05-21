"""
Backends de almacenamiento compatible API S3 (Amazon S3, Cloudflare R2, etc.).

Mismo bucket configurable vía settings, prefijos distintos (`AWS_STATIC_LOCATION` / `AWS_MEDIA_LOCATION`).
Media usa URLs firmadas cuando el bucket es privado (ver MediaStorage).
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = getattr(settings, 'AWS_STATIC_LOCATION', 'static')
    default_acl = None
    file_overwrite = True


class MediaStorage(S3Boto3Storage):
    location = getattr(settings, 'AWS_MEDIA_LOCATION', 'media')
    # Bucket privado: forzar URL firmada S3 en lugar de URL pública por custom_domain.
    custom_domain = None
    querystring_auth = True
    default_acl = None
    file_overwrite = False
