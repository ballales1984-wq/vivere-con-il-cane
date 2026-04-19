import os
import django
from django.utils import translation

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

test_string = "Capisci e risolvi il comportamento del tuo cane"

print(f"Current language: {translation.get_language()}")

with translation.override('en'):
    print(f"Active language: {translation.get_language()}")
    translated = translation.gettext(test_string)
    print(f"String: {test_string}")
    print(f"Translated: {translated}")
    
    if translated == test_string:
        print("FAIL: Translation not found or identical.")
    else:
        print("SUCCESS: Translation working!")

# Check locale paths
from django.conf import settings
print(f"Locale paths: {settings.LOCALE_PATHS}")
for path in settings.LOCALE_PATHS:
    mo_path = os.path.join(path, 'en', 'LC_MESSAGES', 'django.mo')
    print(f"Checking {mo_path}: {'Exists' if os.path.exists(mo_path) else 'Missing'}")
