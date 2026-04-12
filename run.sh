#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput || true

echo "Loading data..."
python manage.py loaddata blog/fixtures/blog_data.json 2>/dev/null || echo "Loading dog_profile..."
python manage.py loaddata dog_profile.json 2>/dev/null || true

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT