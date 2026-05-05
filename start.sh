#!/bin/sh
# Script di avvio: esegue migrate e poi avvia gunicorn
echo "==> Running database migrations..."
python manage.py migrate --noinput
echo "==> Loading knowledge data fixtures..."
python manage.py loaddata knowledge/fixtures/knowledge_data.json
echo "==> Loading blog data fixtures..."
python manage.py loaddata blog/fixtures/blog_data.json
echo "==> Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120