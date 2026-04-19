import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()
url = reverse('canine_tools:tools_index')
print(f"Testing URL: {url}")
response = client.get(url)
print(f"Status Code: {response.status_code}")
if response.status_code == 302:
    print(f"Redirect Location: {response['Location']}")
