#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Loading blog data..."
python manage.py loaddata blog_data.json 2>/dev/null || true

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT