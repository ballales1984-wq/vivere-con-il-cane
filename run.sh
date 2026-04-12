#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput --run-syncdb

echo "Checking for fixture file..."
ls -la blog/fixtures/blog_data.json

echo "Loading blog data..."
python -c "
import os, sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.getcwd())
django.setup()

from django.core.management import call_command
try:
    call_command('loaddata', 'blog/fixtures/blog_data.json')
    print('Fixtures loaded successfully')
except Exception as e:
    print(f'Error loading fixtures: {e}')

from blog.models import BlogPost
print(f'Articles count: {BlogPost.objects.count()}')
"

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT