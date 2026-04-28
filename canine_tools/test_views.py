from django.test import TestCase, Client
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User
from .models import HeartSoundRecording, HealthConnectToken, HealthDataPoint


class SignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_get_returns_200(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_post_creates_user(self):
        response = self.client.post(
            reverse("signup"),
            {"username": "testuser", "password1": "testpass123", "password2": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_signup_post_invalid_data_returns_200(self):
        response = self.client.post(
            reverse("signup"),
            {"username": "testuser", "password1": "testpass123", "password2": "different"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="testuser").exists())


class HealthConnectAuthTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_connect_auth_redirect(self):
        response = self.client.get(reverse("canine_tools:health_connect_auth"))
        self.assertEqual(response.status_code, 302)

    def test_health_connect_callback_get_returns_400(self):
        response = self.client.get(reverse("canine_tools:health_connect_callback"))
        self.assertEqual(response.status_code, 400)

    def test_health_connect_data_requires_login(self):
        response = self.client.get(reverse("canine_tools:health_connect_data"))
        self.assertEqual(response.status_code, 302)


class HeartSoundUploadTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="test")
        self.client.login(username="tester", password="test")

    def test_heart_sound_upload_get_returns_200(self):
        response = self.client.get(reverse("canine_tools:heart_sound_upload"))
        self.assertEqual(response.status_code, 200)

    @patch('canine_tools.views.process_audio_file')
    def test_heart_sound_upload_post_creates_recording(self, mock_process):
        mock_process.return_value = None
        wav_content = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        response = self.client.post(
            reverse("canine_tools:heart_sound_upload"),
            {"audio_file": wav_content}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(HeartSoundRecording.objects.filter(user=self.user).exists())

    def test_heart_sound_result_view(self):
        recording = HeartSoundRecording.objects.create(
            user=self.user,
            audio_file="dummy.wav",
            subject_type="dog"
        )
        response = self.client.get(reverse("canine_tools:heart_sound_result", args=[recording.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BPM")


class DisconnectHealthConnectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="test")
        self.client.login(username="tester", password="test")

    def test_disconnect_health_connect_removes_token(self):
        HealthConnectToken.objects.create(
            user=self.user,
            access_token="test_token",
            refresh_token="refresh"
        )
        response = self.client.post(reverse("canine_tools:disconnect_health_connect"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(HealthConnectToken.objects.filter(user=self.user).exists())
