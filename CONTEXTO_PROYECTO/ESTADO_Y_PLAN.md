# Estado actual y plan de trabajo

## Objetivo principal del proyecto

Reconstruir y consolidar el portal inmobiliario **Total Living** en un proyecto Django limpio (“TOTAL LIVING FINAL”), manteniendo funcionalidad y diseño alineados al legado VKR, con:

- **PostgreSQL** como objetivo en la nube (p. ej. RDS).
- **Almacenamiento de objetos** en producción orientado a **AWS S3** (API compatible también documentada para R2).
- **Sin Docker** como flujo oficial de desarrollo diario (scripts locales y CI en GitHub Actions).
- Reducción de deuda técnica: modelo de datos normalizado, CMS de inicio, restricciones DB, tests y CI.

## Modelo de permisos (negocio)

Sitio público de inventario + captación de leads; **panel interno para ~2 personas**. Cuentas internas Django con **`is_staff=True`**, acceso completo al panel (sin RBAC fino).

## Variables de entorno — por qué tantos archivos y qué hacer

**Por qué existe confusión:** en el repo hay **plantillas** (ejemplos sin secretos reales) y en tu disco sueles tener **copias locales** con contraseñas (`.env`, `.env.development`, `.env.production`). Además **`python-decouple` solo lee un archivo: `.env`** en la raíz al ejecutar comandos; los nombres `.env.development` / `.env.production` son **convención humana**: sirven como plantilla o respaldo, pero Django **no los abre solos** hasta que copies su contenido a `.env` (o uses herramientas externas).

**Qué dejar en Git (seguro, sin secretos):**

| Archivo | Rol |
|---------|-----|
| `.env.example` | Guía: qué copiar y cómo; **no** duplica todas las variables. |
| `.env.development.example` | Plantilla para **tu máquina local** → copiar a `.env`. |
| `.env.staging.example` | Plantilla **Mini-C / staging** → en servidor copiar a `.env` o inyectar vars. |
| `.env.production.example` | Plantilla **producción**; en AWS lo ideal es **sin archivo** en disco (Secrets Manager / vars del servicio). |

**Qué nunca subir a Git:** `.env`, `.env.development`, `.env.production`, `.env.staging`, `.env.local`, y la carpeta **`secrets/`** (certificados PEM, JSON de cuentas de servicio, copias de entorno). Todo eso ya está cubierto por `.gitignore`.

**Flujo recomendado:**

1. **Local:** `copy .env.development.example .env` y edita secretos solo en `.env`.
2. **Staging:** variables en el host o un `.env` **solo en el servidor**, fuera del repo.
3. **Producción:** preferible **AWS Secrets Manager** / **Parameter Store** + variables del proceso; si usas `.env`, permisos restrictivos y **no** copiarlo al repo.

**Nota técnica:** `manage.py` fija por defecto `DJANGO_SETTINGS_MODULE=total_living.settings.development`; `wsgi.py` usa `production`. La línea `DJANGO_SETTINGS_MODULE` dentro de `.env` **no cambia** eso salvo que arranques Gunicorn/uWSGI con la variable explícita (p. ej. staging: `total_living.settings.staging`).

## Plan integral — 7 días (versión sin Docker)

| Día | Enfoque | Estado |
|-----|---------|--------|
| **1** | Sanear repositorio y flujo Git | **Hecho** |
| **2** | Entorno local sin Docker (`PREFLIGHT.bat`, `iniciar_servidor.bat`) | **Hecho** |
| **3** | Manejo de errores y logging | **Hecho** |
| **4** | Tests `accounts` + `developments` | **Hecho** |
| **5** | Integración panel / propiedades / contacto / búsqueda | **Hecho** |
| **6–7** | Hardening producción + backup/restore + Go-Live | **Hecho** |

---

## Fase siguiente — Mini-C: «El espejo real» (staging antes de pulir CSS)

**Objetivo:** Tener un entorno de prueba **alineado con producción** (HTTPS, RDS PostgreSQL, S3) **antes** de invertir la mayor parte del tiempo en refinamiento visual. No tiene que ser público para el mundo, pero debe ser **operativo** para el equipo.

### 1. Despliegue de staging (mínimo viable)

- Instancia pequeña (EC2 u otro) detrás de **HTTPS** (ALB + ACM, o Caddy/nginx + Let’s Encrypt).
- **`DJANGO_SETTINGS_MODULE=total_living.settings.production`** (o un `staging.py` que herede de `production` si más adelante quieres diferencias solo de hosts).
- **`DATABASE_URL`** apuntando a **RDS** (misma versión mayor de Postgres que usarás en prod).
- **Bucket S3** dedicado a staging (prefijos `static/` y `media/` como en prod); IAM con permisos mínimos.
- Variables imprescindibles: ver **`.env.production.example`** (`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` con `https://staging.tudominio`, `SECRET_KEY` fuerte, claves AWS, `REDIS_URL` recomendado si hay más de un worker).
- Tras deploy: `migrate --noinput`, usuario staff de prueba, `collectstatic` con la configuración de static elegida (WhiteNoise o `USE_S3_STATIC=True`).

### 2. Validación de assets (estáticos + media)

| Qué | Cómo validar |
|-----|----------------|
| **CSS/JS/logo** | En el navegador (staging), pestaña Red: que los `.css` / `.js` carguen **200** desde WhiteNoise o desde URLs **https** del bucket/CDN; sin 404 en archivos con hash (`CompressedManifestStaticFilesStorage`). |
| **Media (fotos)** | Subir una imagen de prueba desde el **panel**; abrir la ficha pública y comprobar que la URL sea **https** del dominio S3 o firma correcta según `AWS_QUERYSTRING_AUTH`. Con **`USE_S3_MEDIA=True`**, **`SERVE_LOCAL_MEDIA=False`** en staging (coherente con prod). |
| **Health** | `https://staging.../health/live/` y `/health/ready/` → 200 con BD conectada. |

### 3. Leaflet / mapas bajo SSL (mixed content)

- **`MAP_TILE_URL`** en `.env` debe usar **`https://`** (el proyecto ya usa Plantillas Carto/OSM compatibles; evitar tiles solo `http://`).
- Revisar plantillas y JS propios: ningún `<script src="http://...">`, iframe ni tile **HTTP**.
- En Chrome: **Consola** → filtrar advertencias de **Mixed Content** al cargar página con mapa (`/search/`, fichas con mapa, etc.).
- Si el proxy termina TLS: confirmar cabecera **`X-Forwarded-Proto: https`** para que Django marque cookies/peticiones como seguras (`SECURE_PROXY_SSL_HEADER` ya está en `production`).

### 4. Criterio de «Mini-C listo»

Puedes pasar a la fase intensiva de **Fase A/B (UX/CSS)** cuando:

1. Staging responde por **HTTPS** con el mismo tipo de settings que usarás en prod.
2. **Al menos una** propiedad de prueba muestra **imagen desde S3** correctamente.
3. **Mapas** cargan tiles sin errores de mixed content.
4. **`/health/ready/`** da 200 contra RDS.

---

## Días 6–7 — Qué quedó implementado (producción primero)

### Seguridad y coherencia (`total_living/settings/production.py`)

- **`SESSION_COOKIE_HTTPONLY = True`** explícito.
- **Validación:** si **`USE_S3_MEDIA=True`** y **`SERVE_LOCAL_MEDIA=True`**, arranque rechazado (`ImproperlyConfigured`): el media no debe servirse por Django y por bucket a la vez.
- **SMTP:** `EMAIL_USE_TLS` y `EMAIL_USE_SSL` configurables por entorno (p. ej. puerto 465 con SSL).
- El resto ya existía: `SECURE_SSL_REDIRECT`, cookies seguras, HSTS, `SECURE_PROXY_SSL_HEADER`, `SECRET_KEY` fuerte (`ENFORCE_STRONG_SECRET_KEY`), WhiteNoise / S3 según flags.

### Salud del servicio (balanceadores / K8s / ALB)

- **`GET /health/live/`** — proceso vivo; respuesta JSON `{ "status": "live" }`.
- **`GET /health/ready/`** — `SELECT 1` a la base; 200 si OK, **503** si falla la BD (útil para readiness).

Implementación: `total_living/health_views.py`, rutas en `total_living/urls.py`. Tests en `search/tests.py` (`HealthEndpointTests`).

### Redis

- Con **`REDIS_URL`** en `.env`, la caché usa **django-redis** (rate limit y sesiones compartidas entre workers). Sin variable, sigue **LocMem** (solo un proceso).

### Object storage (S3 / R2)

- Producción ya discrimina **`OBJECT_STORAGE_PROVIDER`** `aws` vs `r2`, URLs de static/media y bucket; **`django-storages`** + **`boto3`** en `requirements.txt`.
- Tras `collectstatic` y bucket configurado, el front “habla” con URLs HTTPS del CDN/dominio que definas (`AWS_S3_CUSTOM_DOMAIN` opcional).

### Simulacro backup / restore (PostgreSQL)

1. **Físico (recomendado en RDS):** script **`scripts/pg_backup_restore.py`**
   - Requiere **`DATABASE_URL`** y **`pg_dump`** / **`pg_restore`** en PATH.
   - `python scripts/pg_backup_restore.py backup [--output ruta]`
   - `python scripts/pg_backup_restore.py restore --input archivo.dump --confirm`  
     (`--confirm` obligatorio: **restore** usa `--clean`; usar solo en **staging** o simulacro controlado).

2. Atajo Windows: **`scripts/SIMULACRO_BACKUP.bat`** (ejecuta `backup` con nombre por defecto bajo `backups/`).

3. **Lógico (sin cliente PostgreSQL):** respaldo de datos vía Django:
   - `python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > backups/datos.json`
   - Restauración orientativa: base vacía + migraciones + `loaddata` (revisar dependencias y archivos binarios/media por separado).

### Checklist Go-Live (operación)

- [ ] **Dominio y TLS:** certificado válido; **`ALLOWED_HOSTS`** y **`CSRF_TRUSTED_ORIGINS`** con `https://tudominio`.
- [ ] **Secretos:** `SECRET_KEY` larga y aleatoria; credenciales RDS y S3 fuera del repo.
- [ ] **RDS:** `DATABASE_URL` de producción; prueba migraciones: `migrate --noinput`.
- [ ] **S3:** bucket, políticas IAM mínimas, CORS si el front llama al bucket; subir media de prueba y ver URL en ficha.
- [ ] **Redis (opcional pero recomendado con varios workers):** `REDIS_URL` establecido.
- [ ] **Static:** `collectstatic`; si `USE_S3_STATIC=True`, verificar objetos en prefijo `static/`.
- [ ] **Health:** comprobar **`/health/live/`** y **`/health/ready/`** detrás del proxy (cabecera `X-Forwarded-Proto`).
- [ ] **Email:** SMTP real y `DEFAULT_FROM_EMAIL`.
- [ ] **Backups:** automatizar `pg_backup_restore.py backup` o snapshot RDS + probar **restore en staging** al menos una vez.
- [ ] **No usar** `robocopy /MIR` sobre el código en producción; despliegues por Git + pip + migrate.

### Regresión automatizada

`python manage.py test properties panel search contact accounts developments`

---

## Hitos de producto (resumen)

- Amenidades normalizadas, CMS Home + carrusel, áreas (construcción como referencia), integridad e imágenes, singleton CMS, coordenadas centralizadas, CI en GitHub Actions.

## Contexto de GitHub / repo “con paja”

Posponer repo nuevo limpio hasta cerrar el ciclo de diseño; el código ya tiene base operativa y tests.

## Transcripción de conversaciones previas

En la máquina del usuario (Cursor): carpeta `agent-transcripts` del proyecto.
