#!/bin/bash
set -e

echo "Starting Django check..."
python manage.py check || { echo "Check failed!"; exit 1; }

echo "Starting runserver..."
exec python manage.py runserver 0.0.0.0:$PORT