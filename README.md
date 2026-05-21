# Total Living — Portal inmobiliario

Sistema web Django para catálogo público de propiedades, captación de leads, desarrollos y panel interno de administración.

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.11+, Django 4.2 |
| Base de datos | PostgreSQL (local, RDS en producción) |
| Estáticos | WhiteNoise (`collectstatic`) o prefijo S3 (`USE_S3_STATIC`) |
| Media | Disco local en desarrollo; **Amazon S3** o Cloudflare R2 en producción |
| Servidor app | Gunicorn (Docker/scripts) o `runserver` en desarrollo |
| CI | GitHub Actions (Postgres + `check` + `migrate` + tests) |

La configuración canónica de producción está en `total_living/settings/production.py` y `.env.production.example`.

## Inicio rápido (desarrollo, sin Docker)

1. Entorno virtual e dependencias:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Variables de entorno (solo se lee `.env` en la raíz):

```bash
copy .env.development.example .env
```

3. Base de datos y datos iniciales:

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Validar y arrancar:

```bash
PREFLIGHT.bat
iniciar_servidor.bat
```

Servidor por defecto: **http://127.0.0.1:8090**

Rutas internas (personalizables en `.env`): panel staff y admin Django con paths no obvios (`PANEL_URL_PATH`, `ADMIN_URL_PATH`).

## Estáticos para producción / staging

Con WhiteNoise (recomendado si no subes CSS/JS al bucket):

```bash
python manage.py collectstatic --noinput
```

En producción con `USE_S3_STATIC=True`, `collectstatic` sube al bucket configurado. Tras cambiar CSS/JS, vuelve a ejecutar `collectstatic` antes del deploy.

## Tests y calidad

```bash
python manage.py check
python manage.py test properties panel search contact accounts developments
```

CI (`.github/workflows/ci.yml`) ejecuta lo mismo contra PostgreSQL 16.

Health checks (ALB / monitoreo): `GET /health/live/` y `GET /health/ready/`.

## Estructura principal

- `total_living/` — settings, URLs, storage backends, health
- `properties/` — inventario, imágenes, carrusel, amenidades
- `search/` — búsqueda avanzada
- `panel/` — CMS inicio/nosotros, propiedades, inbox, carrusel
- `contact/` — formularios y buzón
- `developments/` — desarrollos y quiz de leads
- `regions/` — regiones/zonas
- `CONTEXTO_PROYECTO/` — estado del proyecto, Go-Live, riesgos operativos

## Fases del proyecto (estado actual)

| Fase | Contenido | Estado |
|------|-----------|--------|
| **Base** | Apps, settings modulares, panel, búsqueda, mapas, PDF | ✅ |
| **Estabilidad** | Decimal en precios/áreas, `construction_area` obligatorio, integridad imágenes | ✅ en código |
| **Pre-deploy (Mini-C)** | Staging HTTPS + RDS + S3 + Redis + checklist manual | ⏳ operación |
| **Producción** | Dominio, secretos AWS, backups RDS, SMTP | ⏳ operación |

Detalle operativo y checklist de staging: [`CONTEXTO_PROYECTO/ESTADO_Y_PLAN.md`](CONTEXTO_PROYECTO/ESTADO_Y_PLAN.md).

## Despliegue (resumen)

1. Copiar plantilla: `.env.production.example` → variables en servidor o Secrets Manager (no subir `.env` con secretos a Git).
2. `DJANGO_SETTINGS_MODULE=total_living.settings.production`
3. `DATABASE_URL` → RDS PostgreSQL.
4. Activar almacenamiento: `USE_OBJECT_STORAGE=True`, bucket S3, `SERVE_LOCAL_MEDIA=False`.
5. Con varios workers Gunicorn: configurar `REDIS_URL`.
6. Arranque: `migrate --noinput`, `collectstatic --noinput`, Gunicorn (`scripts/docker/start-web.sh` o servicio equivalente).

Docker (`Dockerfile`, `docker-compose.prod.yml`) es **opcional** para empaquetar el mismo flujo; el desarrollo diario oficial sigue siendo **sin Docker** (`PREFLIGHT.bat` / `iniciar_servidor.bat`).

## Notas importantes

- No uses `robocopy /MIR` sobre la carpeta del proyecto activo (riesgo de sobrescribir `.git` y trabajo local). Ver `CONTEXTO_PROYECTO/RIESGOS_OPERACION.md`.
- Respaldos PostgreSQL: `scripts/pg_backup_restore.py` y `scripts/SIMULACRO_BACKUP.bat`.
