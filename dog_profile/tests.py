from django.test import TestCase
from django.test import Client
from django.utils import timezone
from datetime import date
from dog_profile.models import DogProfile, HealthEvent, DailyLog


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

    def test_events_count(self):
        profile = DogProfile.objects.create(name="Marco", dog_name="Fido")
        self.assertEqual(profile.events_count, 0)


class HealthEventModelTest(TestCase):
    def setUp(self):
        self.profile = DogProfile.objects.create(name="Marco", dog_name="Fido")

    def test_health_event_str(self):
        event = HealthEvent(
            dog=self.profile, title="Vaccino", event_type="vaccine", date=date.today()
        )
        self.assertIn("Vaccino", str(event))
        self.assertIn("Fido", str(event))

    def test_health_event_default_ordering(self):
        event1 = HealthEvent.objects.create(
            dog=self.profile, title="Old Event", date=date(2024, 1, 1)
        )
        event2 = HealthEvent.objects.create(
            dog=self.profile, title="New Event", date=date(2025, 1, 1)
        )
        events = list(HealthEvent.objects.filter(dog=self.profile))
        self.assertEqual(events[0].title, "New Event")


class DailyLogModelTest(TestCase):
    def setUp(self):
        self.profile = DogProfile.objects.create(name="Marco", dog_name="Fido")

    def test_daily_log_str(self):
        log = DailyLog(dog=self.profile, date=date.today())
        self.assertIn("Fido", str(log))

    def test_daily_log_default_values(self):
        log = DailyLog(dog=self.profile, date=date.today())
        self.assertEqual(log.sleep_hours, 0)
        self.assertEqual(log.play_minutes, 0)
        self.assertEqual(log.walk_minutes, 0)
        self.assertEqual(log.food_grams, 0)


class DogProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = DogProfile.objects.create(
            name="Marco", dog_name="Fido", breed="Labrador"
        )

    def test_dashboard_view(self):
        response = self.client.get("/cane/")
        self.assertEqual(response.status_code, 200)

    def test_profile_create_view(self):
        response = self.client.get("/cane/nuovo/")
        self.assertEqual(response.status_code, 200)

    def test_profile_form_submission(self):
        response = self.client.post(
            "/cane/nuovo/",
            {
                "name": "Luca",
                "dog_name": "Rex",
                "breed": "Golden Retriever",
                "gender": "male",
            },
        )
        self.assertEqual(DogProfile.objects.filter(dog_name="Rex").count(), 1)


class HealthEventViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = DogProfile.objects.create(name="Marco", dog_name="Fido")

    def test_add_event_view(self):
        response = self.client.get(f"/cane/{self.profile.id}/evento/")
        self.assertEqual(response.status_code, 200)

    def test_add_event_form_submission(self):
        response = self.client.post(
            f"/cane/{self.profile.id}/evento/",
            {
                "event_type": "vaccine",
                "title": "Vaccino annuale",
                "description": "Vaccino annuale antirabbica",
                "date": "2025-04-15",
            },
        )
        self.assertEqual(HealthEvent.objects.filter(title="Vaccino annuale").count(), 1)


class DailyLogViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = DogProfile.objects.create(name="Marco", dog_name="Fido")

    def test_add_log_view(self):
        response = self.client.get(f"/cane/{self.profile.id}/log/")
        self.assertEqual(response.status_code, 200)

    def test_add_log_form_submission(self):
        response = self.client.post(
            f"/cane/{self.profile.id}/log/",
            {
                "date": "2025-04-12",
                "sleep_hours": 8,
                "play_minutes": 30,
                "walk_minutes": 60,
                "food_grams": 400,
            },
        )
        self.assertEqual(DailyLog.objects.filter(dog=self.profile).count(), 1)
