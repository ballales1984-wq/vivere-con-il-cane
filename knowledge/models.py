from django.db import models
from django.utils.text import slugify


class BreedInsight(models.Model):
    """Insights about specific dog breeds."""

    breed = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    energy_level = models.CharField(
        max_length=20,
        choices=[
            ("low", "Basso"),
            ("medium", "Medio"),
            ("high", "Alto"),
            ("very_high", "Molto Alto"),
        ],
        default="medium",
    )

    social_level = models.CharField(
        max_length=20,
        choices=[
            ("low", "Basso"),
            ("medium", "Medio"),
            ("high", "Alto"),
            ("very_high", "Molto Alto"),
        ],
        default="medium",
    )

    common_problems = models.TextField(blank=True, help_text="Comma-separated list")
    traits = models.TextField(blank=True, help_text="Caratteristiche tipiche")
    care_tips = models.TextField(blank=True, help_text="Consigli di cura")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.breed)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.breed

    class Meta:
        verbose_name = "Razza"
        verbose_name_plural = "Razze"


class Problem(models.Model):
    """Common dog problems."""

    CATEGORY_CHOICES = [
        ("behavior", "Comportamento"),
        ("health", "Salute"),
        ("nutrition", "Alimentazione"),
        ("training", "Educazione"),
        ("lifestyle", "Vita Quotidiana"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Basso"),
        ("medium", "Medio"),
        ("high", "Alto"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    severity = models.CharField(
        max_length=10, choices=SEVERITY_CHOICES, default="medium"
    )
    common_breeds = models.TextField(blank=True, help_text="Razze più colpite")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Problema"
        verbose_name_plural = "Problemi"


class Cause(models.Model):
    """Causes for each problem."""

    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="causes"
    )
    description = models.CharField(max_length=200)
    probability = models.CharField(
        max_length=20,
        choices=[
            ("rare", "Rara"),
            ("possible", "Possibile"),
            ("common", "Comune"),
            ("very_common", "Molto Comune"),
        ],
        default="common",
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.problem.title} - {self.description}"

    class Meta:
        verbose_name = "Causa"
        verbose_name_plural = "Cause"


class Solution(models.Model):
    """Solutions for each problem."""

    SOLUTION_TYPES = [
        ("training", "Training"),
        ("environment", "Ambiente"),
        ("nutrition", "Alimentazione"),
        ("health", "Salute"),
        ("behavior", "Comportamento"),
    ]

    DIFFICULTY_LEVELS = [
        ("easy", "Facile"),
        ("medium", "Media"),
        ("hard", "Difficile"),
    ]

    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="solutions"
    )
    solution_type = models.CharField(max_length=20, choices=SOLUTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_LEVELS, default="medium"
    )
    time_needed = models.CharField(
        max_length=50, blank=True, help_text="Es: 2 settimane"
    )
    success_rate = models.CharField(
        max_length=20,
        choices=[
            ("low", "Basso"),
            ("medium", "Medio"),
            ("high", "Alto"),
        ],
        default="medium",
    )
    warnings = models.TextField(blank=True, help_text="Cose da evitare")

    def __str__(self):
        return f"{self.problem.title} - {self.title}"

    class Meta:
        verbose_name = "Soluzione"
        verbose_name_plural = "Soluzioni"


class DogAnalysis(models.Model):
    """User interactions and AI analyses saved."""

    dog = models.ForeignKey(
        "dog_profile.DogProfile", on_delete=models.CASCADE, related_name="analyses"
    )
    problem = models.ForeignKey(
        Problem, on_delete=models.SET_NULL, null=True, blank=True
    )
    user_description = models.TextField(
        help_text="Descrizione del problema data dall'utente"
    )

    ai_response = models.TextField(blank=True)
    suggested_solution = models.ForeignKey(
        Solution, on_delete=models.SET_NULL, null=True, blank=True
    )

    result = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Da provare"),
            ("improved", "Migliorato"),
            ("no_change", "Nessun cambiamento"),
            ("worse", "Peggiorato"),
        ],
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analisi di {self.dog.dog_name} - {self.problem.title if self.problem else 'Generale'}"

    class Meta:
        verbose_name = "Analisi"
        verbose_name_plural = "Analisi"
        ordering = ["-created_at"]
