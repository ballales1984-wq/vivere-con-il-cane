from django.test import TestCase, Client
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User
from unittest.mock import patch
from .models import HeartSoundRecording, HealthConnectToken, HealthDataPoint