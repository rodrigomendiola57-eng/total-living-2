# Riesgos operativos — qué no repetir

## Git y copias de carpetas

1. **No usar `robocopy /MIR`** sobre la raíz del proyecto activo (`C:\TOTAL LIVING`). Puede sobrescribir trabajo, mezclar ramas o dañar `.git`.
2. Preferir siempre flujo Git: `git status`, commits pequeños, pushes a remoto cuando corresponda.
3. Respaldos (`backups/`, dumps SQL) deben vivir ignorados por Git o fuera del repo; no mezclarlos con código “vivo”.

## Git corrupto o “not a git repository”

Si aparece ese error: **detener** cambios grandes y recuperar/reinicializar Git según `DIA1_GIT_OPERACION_SEGURA.md` antes de seguir desarrollando.

## Entorno local

- Flujo oficial: **sin Docker** para el día a día.
- Antes de reportar errores raros de migración o settings: ejecutar `PREFLIGHT.bat` y corregir lo que marque.

## Coherencia README vs settings

El `README.md` raíz puede mencionar R2 u otras notas históricas; la **intención actual del usuario** incluye preparación sólida para **PostgreSQL + S3** en producción. En caso de duda, mirar `total_living/settings/production.py` y `.env.production.example`.
