#!/bin/sh
# Start script with database initialization check
# Usage: sh run.sh

echo "===================================================================="
echo "Vivere con il Cane - Startup Script"
echo "===================================================================="

# Ensure we're in the right directory
cd /vivere-con-il-cane

# Check if database exists
if [ ! -f "db.sqlite3" ]; then
    echo "[INFO] Database not found. Creating new database..."
    python manage.py migrate --noinput
    python manage.py loaddata knowledge/fixtures/knowledge_data.json --ignorenonexistent
    python manage.py loaddata blog/fixtures/blog_data.json --ignorenonexistent
    echo "[INFO] Database created successfully."
else
    echo "[INFO] Database found. Running migrations..."
    python manage.py migrate --noinput
fi

# Create admin if ADMIN_PASSWORD env var is provided (production use)
if [ -n "$ADMIN_PASSWORD" ]; then
  echo "[INFO] Creating admin user..."
  python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
admin, created = User.objects.get_or_create(
    username='admin@vivereconilcane.com',
    defaults={'email': 'admin@vivereconilcane.com', 'is_staff': True, 'is_superuser': True}
)
if created:
    admin.set_password(os.environ.get('ADMIN_PASSWORD'))
    admin.save()
    print('Admin user created')
"
fi
echo "===================================================================="
echo "Starting Gunicorn..."
echo "===================================================================="
echo ""

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --preload
