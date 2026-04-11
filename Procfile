release: python manage.py migrate --run-syncdb
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT