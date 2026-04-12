#!/usr/bin/env python
import os
import sys
import time
import signal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

print(f"=== Server Starting ===", file=sys.stderr)
print(f"PORT: {os.environ.get('PORT', 'not set')}", file=sys.stderr)
print(f"Python: {sys.version}", file=sys.stderr)
sys.stderr.flush()

try:
    from django.core.management import execute_from_command_line
except Exception as e:
    print(f"ERROR importing django: {e}", file=sys.stderr)
    sys.stderr.flush()
    raise

port = os.environ.get("PORT", "10000")

try:
    execute_from_command_line(
        ["manage.py", "runserver", f"0.0.0.0:{port}", "--noreload", "--threaded"]
    )
except Exception as e:
    print(f"ERROR during runserver: {e}", file=sys.stderr)
    sys.stderr.flush()
    raise

print("Server starting complete", file=sys.stderr)

signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

while True:
    time.sleep(1)
