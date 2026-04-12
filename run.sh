#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput --run-syncdb

echo "Loading blog data..."
python manage.py loaddata blog/fixtures/blog_data.json --verbosity 2

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT