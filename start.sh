#!/bin/bash
set -e
cd "$(dirname "$0")"
python -c "
import sys, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
print('=== DJANGO START ===', flush=True)
try:
    import django
    print('Django imported, version:', django.get_version(), flush=True)
    django.setup()
    print('Django setup done', flush=True)
    from django.conf import settings
    print('Settings loaded', flush=True)
    from django.core.management import execute_from_command_line
    print('Running migrate...', flush=True)
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    print('Migrate done', flush=True)
    print('Starting server...', flush=True)
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:' + os.environ.get('PORT', '10000')])
except Exception as e:
    print('ERROR:', str(e), flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
"