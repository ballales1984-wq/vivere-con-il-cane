"""
Comprehensive tests for untested dog_profile views to increase coverage.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import translation, timezone
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from dog_profile.models import (
    DogProfile,
    MedicalEvent,
    HealthLog,
    VeterinaryRequest,
    VeterinaryMedia,
)
from knowledge.models import DogAnalysis
from datetime import date, timedelta
import io


class DogProfileBaseTestCase(TestCase):
    """Base setup for dog_profile view tests."""

    def setUp(self):
        self.client = Client()
        translation.activate("it")
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@example.com"
        )
        self.client.login(username="testuser", password="testpass")
        self.dog = DogProfile.objects.create(
            owner=self.user,
            name="Mario",
            dog_name="Rex",
            breed="Labrador Retriever",
            gender="male",
            weight=25.5,
        )


class ProfileListViewTest(DogProfileBaseTestCase):
    def test_profile_list_view(self):
        response = self.client.get(reverse("profile_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rex")


class ProfileDetailViewTest(DogProfileBaseTestCase):
    def setUp(self):
        super().setUp()
        # Add some medical events and logs
        self.event = MedicalEvent.objects.create(
            dog=self.dog,
            event_type="visit",
            date=date.today() - timedelta(days=10),
            title="Vaccinazione annuale",
            description="Vaccino antirabbico",
        )
        self.log = HealthLog.objects.create(
            dog=self.dog,
            date=date.today(),
            log_type="routine",
            walk_minutes=30,
            sleep_hours=8,
            food_grams=300,
        )

    def test_profile_detail_view(self):
        response = self.client.get(
            reverse("profile_detail", kwargs={"profile_id": self.dog.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rex")
        self.assertContains(response, "Vaccinazione annuale")
        self.assertIn("events", response.context)
        self.assertIn("logs", response.context)


class MyDogRedirectTest(DogProfileBaseTestCase):
    def test_my_dog_redirects_to_detail(self):
        response = self.client.get(reverse("my_dog"))
        self.assertRedirects(
            response, reverse("profile_detail", kwargs={"profile_id": self.dog.id})
        )

    def test_my_dog_redirects_to_new_if_no_profile(self):
        # Delete the dog and ensure redirect to profile_new
        self.dog.delete()
        response = self.client.get(reverse("my_dog"))
        self.assertRedirects(response, reverse("profile_new"))


class ProfileDossierViewTest(DogProfileBaseTestCase):
    def setUp(self):
        super().setUp()
        # Add some events and analyses
        self.event = MedicalEvent.objects.create(
            dog=self.dog,
            event_type="visit",
            date=date.today() - timedelta(days=5),
            title="Visita di controllo",
            description="Tutto ok",
        )
        self.analysis = DogAnalysis.objects.create(
            dog=self.dog,
            problem=None,
            user_description="Test analysis",
            ai_response="AI suggerisce dieta equilibrata",
            result="success",
        )

    def test_profile_dossier_view(self):
        response = self.client.get(
            reverse("profile_dossier", kwargs={"profile_id": self.dog.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rex")
        self.assertContains(response, "Visita di controllo")
        self.assertIn("timeline", response.context)
        self.assertIn("whatsapp_url", response.context)


class ExportDossierPDFViewTest(DogProfileBaseTestCase):
    def setUp(self):
        super().setUp()
        self.event = MedicalEvent.objects.create(
            dog=self.dog,
            event_type="vaccine",
            date=date.today(),
            title="Vaccino",
            description="",
        )

    @patch("dog_profile.views.pisa.CreatePDF")
    def test_export_dossier_pdf_returns_pdf(self, mock_createpdf):
        # Mock pisa to avoid actual PDF generation
        mock_createpdf.return_value = MagicMock(err=False, dest=io.BytesIO())
        response = self.client.get(
            reverse("export_dossier_pdf", kwargs={"profile_id": self.dog.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")


class VeterinaryRequestViewsTest(DogProfileBaseTestCase):
    """Tests for the veterinary request workflow."""

    def setUp(self):
        super().setUp()
        self.analysis = DogAnalysis.objects.create(
            dog=self.dog,
            problem=None,
            user_description="Problema di pelle",
            ai_response="Ripeti visita",
        )

    def test_vet_request_start_get(self):
        response = self.client.get(
            reverse("vet_request_start", kwargs={"dog_id": self.dog.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invia al Veterinario")

    def test_vet_request_start_post_creates_request(self):
        response = self.client.post(
            reverse("vet_request_start", kwargs={"dog_id": self.dog.id}),
            {
                "problem_description": "Il cane ha prurito intenso",
            },
        )
        self.assertEqual(response.status_code, 302)  # redirect
        vet_req = VeterinaryRequest.objects.get(dog=self.dog)
        self.assertEqual(vet_req.problem_description, "Il cane ha prurito intenso")
        self.assertEqual(vet_req.status, "draft")
        self.assertTrue(vet_req.ai_summary)  # AI summary generated

    def test_vet_request_start_with_analysis_id(self):
        response = self.client.get(
            reverse("vet_request_start", kwargs={"dog_id": self.dog.id})
            + f"?analysis_id={self.analysis.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.analysis.user_description)

    def test_vet_request_upload_get(self):
        vet_req = VeterinaryRequest.objects.create(
            dog=self.dog,
            analysis=self.analysis,
            problem_description="Prurito",
            status="draft",
        )
        response = self.client.get(
            reverse(
                "vet_request_upload",
                kwargs={"dog_id": self.dog.id, "request_id": vet_req.id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carica")

    def test_vet_request_upload_post_photos(self):
        vet_req = VeterinaryRequest.objects.create(
            dog=self.dog,
            analysis=self.analysis,
            problem_description="Prurito",
            status="draft",
        )
        # Create a simple in-memory file
        from django.core.files.uploadedfile import SimpleUploadedFile

        img = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")
        response = self.client.post(
            reverse(
                "vet_request_upload",
                kwargs={"dog_id": self.dog.id, "request_id": vet_req.id},
            ),
            {"photos": [img], "photo_caption": "Test photo"},
        )
        self.assertEqual(response.status_code, 302)  # redirect to review
        vet_req.refresh_from_db()
        self.assertEqual(vet_req.status, "ready")
        self.assertEqual(VeterinaryMedia.objects.count(), 1)

    def test_vet_request_review_get(self):
        vet_req = VeterinaryRequest.objects.create(
            dog=self.dog,
            analysis=self.analysis,
            problem_description="Prurito",
            status="ready",
        )
        response = self.client.get(
            reverse(
                "vet_request_review",
                kwargs={"dog_id": self.dog.id, "request_id": vet_req.id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rivedi Richiesta")

    def test_vet_request_detail_get(self):
        vet_req = VeterinaryRequest.objects.create(
            dog=self.dog,
            analysis=self.analysis,
            problem_description="Prurito",
            status="draft",
        )
        response = self.client.get(
            reverse(
                "vet_request_detail",
                kwargs={"dog_id": self.dog.id, "request_id": vet_req.id},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prurito")

    def test_vet_request_list(self):
        VeterinaryRequest.objects.create(
            dog=self.dog, problem_description="Test1", status="draft"
        )
        VeterinaryRequest.objects.create(
            dog=self.dog, problem_description="Test2", status="ready"
        )
        response = self.client.get(reverse("vet_request_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test1")
        self.assertContains(response, "Test2")
