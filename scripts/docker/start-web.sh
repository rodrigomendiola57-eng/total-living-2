#!/usr/bin/env sh
set -eu

log() {
  printf '[start-web] %s\n' "$1"
}

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  log 'Aplicando migraciones...'
  python manage.py migrate --noinput
fi

if [ "${RUN_SEED_DEMO_CATALOG:-0}" = "1" ]; then
  log 'Ejecutando seed_demo_catalog...'
  python manage.py seed_demo_catalog
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
  log 'Ejecutando collectstatic...'
  python manage.py collectstatic --noinput
fi

if [ "${DEV_LIVE_RELOAD:-0}" = "1" ]; then
  log 'Iniciando Django runserver con autoreload...'
  exec python manage.py runserver 0.0.0.0:8000
fi

log 'Iniciando Gunicorn...'
exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-90}" \
  --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT:-30}" \
  --keep-alive "${GUNICORN_KEEPALIVE:-5}" \
  --access-logfile - \
  --error-logfile - \
  ${GUNICORN_RELOAD:+--reload} \
  total_living.wsgi:application
