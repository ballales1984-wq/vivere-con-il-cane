#!/bin/bash
echo "Starting gunicorn..."
python -c "import django; print('Django version:', django.get_version())"
echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 60