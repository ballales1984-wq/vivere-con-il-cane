#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Alessio. All Rights Reserved.
#
# Licensed under the Private Use License.
# This software may only be used for private, non-commercial purposes.
# Redistribution, reproduction, or commercial use is strictly prohibited
# without express written permission from the copyright holder.
#
import os
import sys

# Ensure output goes to the right place
sys.stdout = sys.stderr

print("=" * 50, flush=True)
print("STARTING DJANGO APP", flush=True)
print("=" * 50, flush=True)

# Set settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ["DEBUG"] = "True"

try:
    print("Importing Django...", flush=True)
    import django

    print("Django version:", django.get_version(), flush=True)

    print("Setting up Django...", flush=True)
    django.setup()
    print("Django setup complete", flush=True)

    print("Getting WSGI application...", flush=True)
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    print("WSGI application loaded!", flush=True)

    print("=" * 50, flush=True)
    print("STARTING WAITRESS SERVER", flush=True)
    print("=" * 50, flush=True)

    from waitress import serve

    port = int(os.environ.get("PORT", 10000))
    print(f"Starting on port {port}", flush=True)
    serve(application, host="0.0.0.0", port=port)

except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback

    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
