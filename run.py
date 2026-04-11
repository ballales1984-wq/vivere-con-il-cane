#!/usr/bin/env python
import os
import sys

print("=== Starting app ===", file=sys.stderr)
print("PYTHONPATH:", os.environ.get("PYTHONPATH"), file=sys.stderr)
print(
    "DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"), file=sys.stderr
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    from django.core.management import execute_from_command_line
except ImportError as e:
    print(f"ERROR importing Django: {e}", file=sys.stderr)
    sys.exit(1)

print(
    "Calling execute_from_command_line(['runserver', '0.0.0.0:$PORT'])", file=sys.stderr
)
execute_from_command_line(["runserver", "0.0.0.0:" + os.environ.get("PORT", "10000")])
