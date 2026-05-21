# Dia 2 - Entorno local reproducible sin Docker

Este flujo deja el entorno de desarrollo consistente y verificable antes de arrancar.

## Comandos oficiales desde hoy

- Validar entorno:
  - `PREFLIGHT.bat`
- Iniciar servidor (incluye preflight):
  - `iniciar_servidor.bat`

## Que valida el preflight

1. Python 3.11+ disponible.
2. `manage.py` presente en el root.
3. Archivo de entorno base disponible (`.env.development`, `.env` o `.env.example`).
4. `django` instalado.
5. `python manage.py check` sin errores.
6. `python manage.py migrate --check` sin migraciones pendientes.

## Flujo diario recomendado

1. Abrir terminal en `C:\TOTAL LIVING`.
2. Ejecutar `PREFLIGHT.bat`.
3. Si todo pasa, usar `iniciar_servidor.bat`.
4. Antes de cerrar bloque de trabajo:
   - guardar cambios
   - validar preflight nuevamente

## Notas operativas

- Este flujo es para desarrollo local sin Docker.
- Si `migrate --check` falla, ejecutar:
  - `python manage.py migrate`
- Si falta entorno, copiar base:
  - `copy .env.development.example .env.development`
