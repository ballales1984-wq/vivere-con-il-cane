from django.test import TestCase
from django.test import Client
from knowledge.models import BreedInsight, Problem, Cause, Solution, DogAnalysis
from dog_profile.models import DogProfile


class BreedInsightModelTest(TestCase):
    def test_breed_insight_str(self):
        insight = BreedInsight(breed="Labrador")
        self.assertEqual(str(insight), "Labrador")

    def test_breed_insight_slug_auto_generated(self):
        insight = BreedInsight(breed="Golden Retriever")
        insight.save()
        self.assertEqual(insight.slug, "golden-retriever")

    def test_breed_insight_default_values(self):
        insight = BreedInsight(breed="Test")
        self.assertEqual(insight.energy_level, "medium")
        self.assertEqual(insight.social_level, "medium")


class ProblemModelTest(TestCase):
    def test_problem_str(self):
        problem = Problem(
            title="Ansia da separazione", category="behavior", description="Descrizione"
        )
        self.assertEqual(str(problem), "Ansia da separazione")

    def test_problem_slug_auto_generated(self):
        problem = Problem(title="Aggressività", category="behavior", description="Desc")
        problem.save()
        self.assertEqual(problem.slug, "aggressivita")

    def test_problem_default_severity(self):
        problem = Problem(title="Test", category="behavior", description="Desc")
        self.assertEqual(problem.severity, "medium")


class CauseModelTest(TestCase):
    def setUp(self):
        self.problem = Problem.objects.create(
            title="Test Problem", category="behavior", description="Desc"
        )

    def test_cause_str(self):
        cause = Cause(problem=self.problem, description="Causa principale")
        self.assertIn("Causa principale", str(cause))


class SolutionModelTest(TestCase):
    def setUp(self):
        self.problem = Problem.objects.create(
            title="Test Problem", category="behavior", description="Desc"
        )

    def test_solution_str(self):
        solution = Solution(
            problem=self.problem,
            solution_type="training",
            title="Training",
            description="Desc",
        )
        self.assertIn("Training", str(solution))


class DogAnalysisModelTest(TestCase):
    def setUp(self):
        self.profile = DogProfile.objects.create(
            name="Marco", dog_name="Fido", gender="male"
        )
        self.problem = Problem.objects.create(
            title="Test Problem", category="behavior", description="Desc"
        )

    def test_dog_analysis_str(self):
        analysis = DogAnalysis(
            dog=self.profile, problem=self.problem, user_description="Desc"
        )
        self.assertIn("Fido", str(analysis))


class KnowledgeViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_problem_list_view(self):
        response = self.client.get("/knowledge/problemi/")
        self.assertEqual(response.status_code, 200)

    def test_analyze_form_view(self):
        response = self.client.get("/knowledge/analizza/")
        self.assertEqual(response.status_code, 200)

    def test_breed_list_view(self):
        response = self.client.get("/knowledge/razze/")
        self.assertEqual(response.status_code, 200)
