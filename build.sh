#!/usr/bin/env bash
# Build en Render: dependencias + estáticos (WhiteNoise).
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
