#!/usr/bin/env python
import sys
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
print("Starting Django test...", file=sys.stderr)
try:
    import django

    django.setup()
    print("Django setup complete", file=sys.stderr)
    from django.core.management import call_command

    call_command("check", verbosity=2)
    print("All checks passed!", file=sys.stderr)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback

    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
print("Script completed successfully", file=sys.stderr)
