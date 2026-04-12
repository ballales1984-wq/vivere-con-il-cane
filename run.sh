#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput || true

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT