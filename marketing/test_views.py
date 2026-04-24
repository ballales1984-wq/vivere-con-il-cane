from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core import mail
from .models import NewsletterSubscriber
import uuid


class NewsletterSubscriberModelTest(TestCase):
    def test_str_returns_email(self):
        subscriber = NewsletterSubscriber(email="test@example.com")
        self.assertEqual(str(subscriber), "test@example.com")

    def test_unsubscribe_token_generated(self):
        subscriber = NewsletterSubscriber(email="test@example.com")
        subscriber.save()
        self.assertIsNotNone(subscriber.unsubscribe_token)
        # UUIDField returns a UUID object; check its string representation
        token_str = str(subscriber.unsubscribe_token)
        self.assertTrue(len(token_str) in [32, 36])  # 32 hex or 36 with hyphens

    def test_is_active_default_true(self):
        subscriber = NewsletterSubscriber(email="test@example.com")
        self.assertTrue(subscriber.is_active)


class SubscribeNewsletterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("subscribe_newsletter")

    def test_subscribe_post_valid_email(self):
        response = self.client.post(self.url, {"email": "newuser@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Benvenuto a bordo")
        self.assertTrue(
            NewsletterSubscriber.objects.filter(
                email="newuser@example.com", is_active=True
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Benvenuto", mail.outbox[0].subject)

    def test_subscribe_post_empty_email(self):
        response = self.client.post(self.url, {"email": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inserisci un indirizzo email")

    def test_subscribe_post_invalid_email(self):
        response = self.client.post(self.url, {"email": "notanemail"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email non valida")

    def test_subscribe_duplicate_active(self):
        NewsletterSubscriber.objects.create(
            email="existing@example.com", is_active=True
        )
        response = self.client.post(self.url, {"email": "existing@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sei già iscritto")

    def test_subscribe_reenables_inactive(self):
        NewsletterSubscriber.objects.create(email="old@example.com", is_active=False)
        response = self.client.post(self.url, {"email": "old@example.com"})
        self.assertEqual(response.status_code, 200)
        subscriber = NewsletterSubscriber.objects.get(email="old@example.com")
        self.assertTrue(subscriber.is_active)

    def test_subscribe_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertContains(response, "Metodo non permesso", status_code=405)


class UnsubscribeNewsletterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.subscriber = NewsletterSubscriber.objects.create(
            email="unsubscribe@example.com",
            is_active=True,
            unsubscribe_token=str(uuid.uuid4()),
        )
        self.url = reverse(
            "unsubscribe_newsletter",
            kwargs={"token": self.subscriber.unsubscribe_token},
        )

    def test_unsubscribe_valid_token(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Disiscritto")
        self.subscriber.refresh_from_db()
        self.assertFalse(self.subscriber.is_active)

    def test_unsubscribe_invalid_token_404(self):
        # Generate a random UUID that does not exist in DB
        import uuid as _uuid

        random_token = str(_uuid.uuid4())
        url = reverse("unsubscribe_newsletter", kwargs={"token": random_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe_post_also_works(self):
        """POST to unsubscribe endpoint also unsubscribes (view doesn't restrict method)."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.subscriber.refresh_from_db()
        self.assertFalse(self.subscriber.is_active)
