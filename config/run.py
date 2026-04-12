#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    port = os.environ.get("PORT", "10000")
    print(f"Starting server on port {port}", file=sys.stderr)
    sys.stderr.flush()

    from django.core.management import execute_from_command_line

    execute_from_command_line(
        ["manage.py", "runserver", f"0.0.0.0:{port}", "--noreload"]
    )


if __name__ == "__main__":
    main()
