#!/bin/bash
set -e

echo "=== Django Deployment ===" >&2
echo "Python: $(python --version)" >&2
echo "PORT: $PORT" >&2

echo "Running migrate..." >&2
python manage.py migrate --noinput || true

echo "Starting server..." >&2
exec python manage.py runserver 0.0.0.0:$PORT