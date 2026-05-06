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

# Check if admin user exists
ADMIN_COUNT=$(python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
count = User.objects.filter(email='admin@vivereconilcane.com').count()
print(count)
")

if [ "$ADMIN_COUNT" -eq 0 ]; then
    echo "[INFO] Creating admin user..."
    python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.create_user(
    username='admin@vivereconilcane.com',
    email='admin@vivereconilcane.com',
    password='Admin123!'
)
admin.is_staff = True
admin.is_superuser = True
admin.save()
print('Admin user created')
"
else
    echo "[INFO] Admin user exists."
fi

echo ""
echo "===================================================================="
echo "Starting Gunicorn..."
echo "===================================================================="
echo "Default credentials:"
echo "  Admin: admin@vivereconilcane.com / Admin123!"
echo "  Test:  test@vivereconilcane.com / Test123!"
echo "===================================================================="
echo ""

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
