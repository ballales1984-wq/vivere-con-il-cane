#!/bin/sh
echo "==> Running database migrations..."
python manage.py migrate --noinput
echo "==> Collecting static files..."
python manage.py collectstatic --noinput
echo "==> Loading knowledge data fixtures..."
python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent
echo "==> Loading blog data fixtures..."
python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent
echo "==> Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120