import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

try:
    from django.core.management import call_command

    call_command("migrate", "--run-syncdb", verbosity=0)
    print("Migrations completed")
except Exception as e:
    print(f"Migration error: {e}")
