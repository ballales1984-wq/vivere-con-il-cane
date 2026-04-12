#!/usr/bin/env python
"""Startup script that runs migrations before starting Gunicorn."""

import os
import sys
import subprocess

APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, APP_DIR)

print("=" * 50)
print("Starting Vivere con il Cane...")
print("=" * 50)

print("\n[1] Running migrate...")
result = subprocess.run(
    [sys.executable, "manage.py", "migrate", "--noinput"],
    cwd=APP_DIR,
    capture_output=True,
    text=True,
)
if result.stdout:
    print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Migrate return code:", result.returncode)

print("\n[2] Setting up Django...")
import django

django.setup()

print("\n[3] Starting Gunicorn...")
port = os.environ.get("PORT", "10000")
os.execvp(
    "gunicorn", ["gunicorn", "config.wsgi:application", "--bind", f"0.0.0.0:{port}"]
)
