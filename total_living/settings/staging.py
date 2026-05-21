"""
Configuración para entorno de staging
"""
from .production import *
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
