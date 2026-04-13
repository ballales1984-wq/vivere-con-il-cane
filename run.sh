#!/bin/sh

python manage.py migrate --noinput || true

echo "Loading blog..."
python manage.py loaddata blog/fixtures/blog_data.json --verbosity 1 || true

echo "Loading knowledge..."
python manage.py loaddata knowledge/fixtures/knowledge_data.json --verbosity 1 || true

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT