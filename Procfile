release: python manage.py migrate --run-syncdb
web: python manage.py check --deploy && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT