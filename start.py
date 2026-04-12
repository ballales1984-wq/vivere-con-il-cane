#!/usr/bin/env python
import os
import sys
import django
import subprocess

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

print("Running migrations...")
result = subprocess.run(
    ["python", "manage.py", "migrate", "--noinput"], capture_output=True, text=True
)
if result.returncode != 0:
    print(f"Migration error: {result.stderr}")

port = os.environ.get("PORT", "10000")
print(f"Starting server on port {port}...")
os.execvp("gunicorn", ["gunicorn", "config.wsgi:application", f"--bind=0.0.0.0:{port}"])
