# Módulos, archivos clave y decisiones técnicas

## Apps Django relevantes

- `total_living/` — URLs principales, settings (`base`, `development`, `production`), `home_view` / `about_view` con CMS singleton y carrusel combinado.
- `properties/` — Modelos de propiedad, imágenes, amenidades normalizadas; vistas públicas y PDF; formularios panel/alta.
- `panel/` — Panel interno: propiedades, desarrollos, CMS Home/Nosotros, carrusel, amenidades catálogo.
- `developments/` — Desarrollos inmobiliarios, modelos de unidades, panel asociado.
- `search/` — Búsqueda y ordenación usando `construction_area`.
- `contact/` — Formularios de contacto y asesorías.
- `accounts/` — Autenticación / usuarios (pendiente ampliar tests en Día 4).

## Archivos operativos locales (sin Docker)

- `PREFLIGHT.bat` → ejecuta `scripts/preflight_no_docker.py`
- `iniciar_servidor.bat` — preflight + `runserver 8090`
- `scripts/preflight_no_docker.py` — validaciones antes de arrancar

## Variables de entorno (referencia)

- Plantillas: `.env.example`, `.env.development.example`, `.env.production.example`
- Producción: flags de seguridad SSL/cookies, `ENFORCE_STRONG_SECRET_KEY`, object storage (`USE_OBJECT_STORAGE`, AWS/R2 según configuración), `REDIS_URL` opcional para caché distribuida (`django-redis`).

## Migraciones destacadas (concepto)

- Propiedades: copia `area` → `construction_area`, eliminación de `area`; deduplicación de imágenes principales + `UniqueConstraint`; índice en `construction_area`.
- Panel: `singleton_key` en Home/Nosotros con deduplicación previa.

## Módulos tocados en el refactor de errores (Día 3)

Sustitución de `except Exception` por excepciones más específicas y `logger.exception` donde aplica:

- `panel/views.py` — edición propiedad, alta/edición carrusel
- `properties/views.py` — alta propiedad, utilidades PDF
- `contact/views.py` — vistas de contacto / asesoría
- `developments/views.py` — API quiz, panel desarrollos/unidades, imágenes

## CI

- `.github/workflows/ci.yml` — Python 3.11, Postgres servicio, `manage.py check`, `migrate`, `test properties panel search contact`

## Objetivo de infraestructura futura

- **RDS PostgreSQL** para datos relacionales.
- **S3** (u objeto compatible) para media y estáticos gestionados como archivos de usuario.
- **Redis** opcional para caché/ratelimit en entornos multi-instancia.
