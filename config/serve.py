#!/usr/bin/env python
import os
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

print("=== STARTING SERVE.PY ===", flush=True)
print(f"PORT={os.environ.get('PORT', '10000')}", flush=True)
print(f"sys.stderr: {sys.stderr}", flush=True)

sys.stderr.write("Starting Django setup...\n")
sys.stderr.flush()

try:
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    sys.stderr.write("WSGI app created\n")
    sys.stderr.flush()
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    sys.stderr.write(f"ERROR: {e}\n")
    sys.stderr.flush()
    raise

from waitress import serve

port = int(os.environ.get("PORT", "10000"))
sys.stderr.write(f"About to serve on port {port}\n")
sys.stderr.flush()

try:
    serve(application, host="0.0.0.0", port=port, threads=4)
except Exception as e:
    sys.stderr.write(f"ERROR in serve: {e}\n")
    sys.stderr.flush()
    raise
