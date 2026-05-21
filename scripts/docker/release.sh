#!/usr/bin/env sh
set -eu

printf '[release] migrate\n'
python manage.py migrate --noinput

if [ "${RUN_SEED_DEMO_CATALOG:-0}" = "1" ]; then
  printf '[release] seed_demo_catalog\n'
  python manage.py seed_demo_catalog
fi

printf '[release] collectstatic\n'
python manage.py collectstatic --noinput

printf '[release] ok\n'
