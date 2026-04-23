from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone, translation
from django.contrib.auth.models import User
from datetime import date
from dog_profile.models import (
    DogProfile,
    MedicalEvent,
    HealthLog,
    VeterinaryRequest,
    VeterinaryMedia,
)


class DogProfileModelTest(TestCase):
    def test_dog_profile_str(self):
        profile = DogProfile(name="Marco", dog_name="Fido")
        self.assertEqual(str(profile), "Fido (Marco)")

    def test_get_age_no_birth_date(self):
        profile = DogProfile(name="Marco", dog_name="Fido")
        self.assertEqual(profile.get_age(), "?")

    def test_get_age_with_birth_date(self):
        profile = DogProfile(
            name="Marco", dog_name="Fido", birth_date=date(2020, 5, 15)
        )
        age = profile.get_age()
        self.assertIn(age, ["5", "6"])


class MedicalEventModelTest(TestCase):
    def setUp(self):
        self.profile = DogProfile.objects.create(name="Marco", dog_name="Fido")

    def test_medical_event_str(self):
        event = MedicalEvent(
            dog=self.profile, title="Vaccino", event_type="vaccine", date=date.today()
        )
        self.assertIn("Vaccino", str(event))

    def test_medical_event_default_ordering(self):
        MedicalEvent.objects.create(
            dog=self.profile, title="Old Event", date=date(2024, 1, 1)
        )
        MedicalEvent.objects.create(
            dog=self.profile, title="New Event", date=date(2025, 1, 1)
        )
        events = list(MedicalEvent.objects.filter(dog=self.profile))
        self.assertEqual(events[0].title, "New Event")


class HealthLogModelTest(TestCase):
    def setUp(self):
        self.profile = DogProfile.objects.create(name="Marco", dog_name="Fido")

    def test_health_log_str(self):
        log = HealthLog(dog=self.profile, date=date.today())
        self.assertIn("Fido", str(log))


class DogProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        translation.activate("it")
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        self.profile = DogProfile.objects.create(
            owner=self.user, name="Marco", dog_name="Fido", breed="Labrador"
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_profile_create_view(self):
        response = self.client.get(reverse("profile_new"))
        self.assertEqual(response.status_code, 200)

    def test_profile_form_submission(self):
        response = self.client.post(
            reverse("profile_new"),
            {
                "name": "Luca",
                "dog_name": "Rex",
                "breed": "Golden Retriever",
                "gender": "male",
            },
        )
        self.assertEqual(DogProfile.objects.filter(dog_name="Rex").count(), 1)


class MedicalEventViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        translation.activate("it")
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        self.profile = DogProfile.objects.create(
            owner=self.user, name="Marco", dog_name="Fido"
        )

    def test_add_event_view(self):
        response = self.client.get(
            reverse("profile_add_event", kwargs={"profile_id": self.profile.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_add_event_form_submission(self):
        response = self.client.post(
            reverse("profile_add_event", kwargs={"profile_id": self.profile.id}),
            {
                "event_type": "vaccine",
                "title": "Vaccino annuale",
                "description": "Vaccino annuale antirabbica",
                "date": "2025-04-15",
            },
        )
        self.assertEqual(
            MedicalEvent.objects.filter(title="Vaccino annuale").count(), 1
        )


class HealthLogViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        translation.activate("it")
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.login(username="testuser", password="password123")
        self.profile = DogProfile.objects.create(
            owner=self.user, name="Marco", dog_name="Fido"
        )

    def test_add_log_view(self):
        response = self.client.get(
            reverse("profile_add_log", kwargs={"profile_id": self.profile.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_add_log_form_submission(self):
        response = self.client.post(
            reverse("profile_add_log", kwargs={"profile_id": self.profile.id}),
            {
                "date": "2025-04-12",
                "sleep_hours": 8,
                "play_minutes": 30,
                "walk_minutes": 60,
                "food_grams": 400,
            },
        )
        self.assertEqual(HealthLog.objects.filter(dog=self.profile).count(), 1)


    def test_medical_events_relationship(self):
        """Test that dog.medical_events relationship works after migration"""
        dog = DogProfile.objects.create(
            owner=self.user,
            dog_name="TestDog",
            breed="Test Breed"
        )
        event = MedicalEvent.objects.create(
            dog=dog,
            event_type="visit",
            date="2024-01-15",
            title="Test Visit"
        )
        self.assertEqual(dog.medical_events.count(), 1)
        self.assertEqual(dog.medical_events.first().title, "Test Visit")
