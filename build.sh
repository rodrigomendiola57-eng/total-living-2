#!/usr/bin/env bash
# Build en Render: dependencias + estáticos (WhiteNoise).
set -o errexit

export DJANGO_SETTINGS_MODULE=total_living.settings.production
export ENVIRONMENT=production

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
