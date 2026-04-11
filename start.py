#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

print("Python starting...", file=sys.stderr)
sys.stdout.flush()

try:
    import django

    print("Django version:", django.get_version(), file=sys.stderr)
    sys.stdout.flush()

    django.setup()
    print("Django setup complete", file=sys.stderr)
    sys.stdout.flush()

    from django.core.management import execute_from_command_line

    print("Starting runserver on 0.0.0.0:10000", file=sys.stderr)
    sys.stdout.flush()

    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:10000"])
except Exception as e:
    print("ERROR:", str(e), file=sys.stderr)
    sys.stdout.flush()
    import traceback

    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
