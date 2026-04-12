#!/bin/sh

# Use database from repo if current DB is empty
python manage.py migrate --noinput || true

# Check if we have articles
ARTICLES=$(python manage.py shell -c "from blog.models import BlogPost; print(BlogPost.objects.count())" 2>/dev/null | tail -1)

if [ "$ARTICLES" = "0" ]; then
    echo "Loading fixtures..."
    python manage.py loaddata blog/fixtures/blog_data.json 2>/dev/null || true
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT