from django.test import TestCase
from django.urls import reverse
from django.test import Client


class FoodCalculatorTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request_returns_200(self):
        response = self.client.get("/tool/cibo/")
        self.assertEqual(response.status_code, 200)

    def test_post_with_valid_data(self):
        response = self.client.post(
            "/tool/cibo/", {"weight": 20, "age": "adult", "activity": "normal"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("result", response.context)

    def test_post_with_invalid_data(self):
        response = self.client.post("/tool/cibo/", {"weight": "invalid"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context.get("result"))

    def test_calculation_adult_normal(self):
        response = self.client.post(
            "/tool/cibo/", {"weight": 10, "age": "adult", "activity": "normal"}
        )
        result = response.context["result"]
        self.assertEqual(result["grams"], 10 * 30 + 70)

    def test_calculation_puppy(self):
        response = self.client.post(
            "/tool/cibo/", {"weight": 10, "age": "puppy", "activity": "normal"}
        )
        result = response.context["result"]
        self.assertEqual(result["grams"], (10 * 30 + 70) * 2)


class AgeCalculatorTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request_returns_200(self):
        response = self.client.get("/tool/eta/")
        self.assertEqual(response.status_code, 200)

    def test_post_with_valid_data(self):
        response = self.client.post("/tool/eta/", {"dog_age": 5, "size": "medium"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("result", response.context)

    def test_calculation_medium_dog(self):
        response = self.client.post("/tool/eta/", {"dog_age": 3, "size": "medium"})
        result = response.context["result"]
        self.assertEqual(result["human_age"], 24 + (3 - 2) * 9)

    def test_calculation_small_dog(self):
        response = self.client.post("/tool/eta/", {"dog_age": 3, "size": "small"})
        result = response.context["result"]
        self.assertEqual(result["human_age"], 24 + (3 - 2) * 10)

    def test_life_stage_puppy(self):
        response = self.client.post("/tool/eta/", {"dog_age": 0.3, "size": "medium"})
        result = response.context["result"]
        self.assertEqual(result["life_stage"], "Cucciolo")

    def test_life_stage_senior(self):
        response = self.client.post("/tool/eta/", {"dog_age": 10, "size": "medium"})
        result = response.context["result"]
        self.assertEqual(result["life_stage"], "Anziano")


class DogQuizTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request_returns_200(self):
        response = self.client.get("/tool/quiz/")
        self.assertEqual(response.status_code, 200)

    def test_quiz_correct_answers(self):
        response = self.client.post("/tool/quiz/", {"q1": "a", "q2": "c", "q3": "b"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Esperto", response.context["result"])

    def test_quiz_wrong_answers(self):
        response = self.client.post("/tool/quiz/", {"q1": "b", "q2": "a", "q3": "c"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Principiante", response.context["result"])


class ToolsIndexTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_returns_200(self):
        response = self.client.get("/tool/")
        self.assertEqual(response.status_code, 200)

    def test_index_contains_tools(self):
        response = self.client.get("/tool/")
        self.assertIn("Calcolatore Cibo", response.content.decode())


class LegalPagesTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_privacy_policy(self):
        response = self.client.get("/privacy/")
        self.assertEqual(response.status_code, 200)

    def test_terms_of_service(self):
        response = self.client.get("/terms/")
        self.assertEqual(response.status_code, 200)

    def test_cookie_policy(self):
        response = self.client.get("/cookie/")
        self.assertEqual(response.status_code, 200)
