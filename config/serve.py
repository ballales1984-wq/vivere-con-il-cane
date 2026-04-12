#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

print(f"=== Starting with Waitress ===", file=sys.stderr)
print(f"PORT: {os.environ.get('PORT', '10000')}", file=sys.stderr)
sys.stderr.flush()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from waitress import serve

port = int(os.environ.get("PORT", "10000"))
print(f"Serving on port {port}", file=sys.stderr)
sys.stderr.flush()

serve(application, host="0.0.0.0", port=port, threads=4)
