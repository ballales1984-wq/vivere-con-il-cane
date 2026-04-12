import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

print("WSGI: Starting Django setup...", file=sys.stderr)
sys.stderr.flush()

try:
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    print("WSGI: Django setup complete", file=sys.stderr)
except Exception as e:
    print(f"WSGI Error: {e}", file=sys.stderr)
    raise
