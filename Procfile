web: python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.core.management import execute_from_command_line
execute_from_command_line(['runserver', '0.0.0.0:10000', '--noreload'])
"