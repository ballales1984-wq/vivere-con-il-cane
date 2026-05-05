#!/bin/bash
python manage.py migrate --noinput
python manage.py loaddata blog/fixtures/blog_data.json knowledge/fixtures/knowledge_data.json --ignorenonexistent || true
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120