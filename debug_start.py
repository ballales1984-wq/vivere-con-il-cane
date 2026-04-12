#!/usr/bin/env python
import sys
import os

print("Step 1: Python version", file=sys.stderr)
print(sys.version, file=sys.stderr)
print("Step 2: Current dir", file=sys.stderr)
print(os.getcwd(), file=sys.stderr)
sys.stderr.flush()

print("Step 3: Setting DJANGO_SETTINGS_MODULE", file=sys.stderr)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
print("Step 4: Importing django", file=sys.stderr)
sys.stderr.flush()
import django

print("Step 5: django.setup()", file=sys.stderr)
sys.stderr.flush()
django.setup()
print("Step 6: Getting WSGI", file=sys.stderr)
sys.stderr.flush()
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
print("Step 7: WSGI app ready", file=sys.stderr)
sys.stderr.flush()

port = os.environ.get("PORT", "10000")
print(f"Step 8: Starting on port {port}", file=sys.stderr)
sys.stderr.flush()

from django.core.management import execute_from_command_line

execute_from_command_line(["manage.py", "runserver", f"0.0.0.0:{port}", "--noreload"])
