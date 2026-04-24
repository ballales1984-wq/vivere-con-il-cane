from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class BreedInsight(models.Model):
    """Insights about specific dog breeds."""

    breed = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    energy_level = models.CharField(
        max_length=20,
        choices=[
            ("low", _("Basso")),
            ("medium", _("Medio")),
            ("high", _("Alto")),
            ("very_high", _("Molto Alto")),
        ],
        default="medium",
    )

    social_level = models.CharField(
        max_length=20,
        choices=[
            ("low", _("Basso")),
            ("medium", _("Medio")),
            ("high", _("Alto")),
            ("very_high", _("Molto Alto")),
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
        ("behavior", _("Comportamento")),
        ("health", _("Salute")),
        ("nutrition", _("Alimentazione")),
        ("training", _("Educazione")),
        ("lifestyle", _("Vita Quotidiana")),
    ]

    SEVERITY_CHOICES = [
        ("low", _("Basso")),
        ("medium", _("Medio")),
        ("high", _("Alto")),
    ]

    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, help_text="English title")
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    description_en = models.TextField(blank=True, help_text="English description")
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

    def get_title(self):
        """Return title in current language, fallback to Italian."""
        from django.utils import translation

        lang = translation.get_language() or "it"
        if lang == "en" and self.title_en:
            return self.title_en
        return self.title

    def get_description(self):
        """Return description in current language, fallback to Italian."""
        from django.utils import translation

        lang = translation.get_language() or "it"
        if lang == "en" and self.description_en:
            return self.description_en
        return self.description

    class Meta:
        verbose_name = "Problema"
        verbose_name_plural = "Problemi"


class Cause(models.Model):
    """Causes for each problem."""

    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="causes"
    )
    description = models.CharField(max_length=200)
    description_en = models.CharField(
        max_length=200, blank=True, help_text="English description"
    )
    probability = models.CharField(
        max_length=20,
        choices=[
            ("rare", _("Rara")),
            ("possible", _("Possibile")),
            ("common", _("Comune")),
            ("very_common", _("Molto Comune")),
        ],
        default="common",
    )
    notes = models.TextField(blank=True)
    notes_en = models.TextField(blank=True, help_text="English notes")

    def __str__(self):
        return f"{self.problem.title} - {self.description}"

    def get_description(self):
        from django.utils import translation

        lang = translation.get_language() or "it"
        if lang == "en" and self.description_en:
            return self.description_en
        return self.description

    def get_notes(self):
        from django.utils import translation

        lang = translation.get_language() or "it"
        if lang == "en" and self.notes_en:
            return self.notes_en
        return self.notes

    class Meta:
        verbose_name = "Causa"
        verbose_name_plural = "Cause"


class Solution(models.Model):
    """Solutions for each problem."""

    SOLUTION_TYPES = [
        ("training", _("Training")),
        ("environment", _("Ambiente")),
        ("nutrition", _("Alimentazione")),
        ("health", _("Salute")),
        ("behavior", _("Comportamento")),
    ]

    DIFFICULTY_LEVELS = [
        ("easy", _("Facile")),
        ("medium", _("Media")),
        ("hard", _("Difficile")),
    ]

    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="solutions"
    )
    solution_type = models.CharField(max_length=20, choices=SOLUTION_TYPES)
    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, help_text="English title")
    description = models.TextField()
    description_en = models.TextField(blank=True, help_text="English description")
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_LEVELS, default="medium"
    )
    time_needed = models.CharField(
        max_length=50, blank=True, help_text="Es: 2 settimane"
    )
    time_needed_en = models.CharField(
        max_length=50, blank=True, help_text="English time needed (e.g. 2 weeks)"
    )
    success_rate = models.CharField(
        max_length=20,
        choices=[
            ("low", _("Basso")),
            ("medium", _("Medio")),
            ("high", _("Alto")),
        ],
        default="medium",
    )
    warnings = models.TextField(blank=True, help_text="Cose da evitare")
    warnings_en = models.TextField(blank=True, help_text="English warnings")

    def __str__(self):
        return f"{self.problem.title} - {self.title}"

    def get_title(self):
        from django.utils import translation

        lang = translation.get_language() or "it"
        if lang == "en" and self.title_en:
            return self.title_en
        return self.title

    def get_description(self):
        from django.utils import translation

        lang = translation.get_language() or "it"
        if lang == "en" and self.description_en:
            return self.description_en
        return self.description

    def get_time_needed(self):
        from django.utils import translation

        lang = translation.get_language() or "it"
        if lang == "en" and self.time_needed_en:
            return self.time_needed_en
        return self.time_needed

    def get_warnings(self):
        from django.utils import translation

        lang = translation.get_language() or "it"
        if lang == "en" and self.warnings_en:
            return self.warnings_en
        return self.warnings

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


class VeterinaryDocument(models.Model):
    """Internal veterinary knowledge base documents for AI RAG context."""

    title = models.CharField(max_length=200, help_text="Titolo o Argomento Medico")
    content = models.TextField(
        help_text="Contenuto integrale del documento, linee guida o posologia."
    )
    keywords = models.CharField(
        max_length=255,
        help_text="Parole chiave separate da virgole (es: cioccolato, teobromina)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[VetDB] {self.title}"

    class Meta:
        verbose_name = "Documento Veterinario"
        verbose_name_plural = "Documenti Veterinari"


class LifetimeMacroAnalysis(models.Model):
    """Stores the comprehensive, long-term AI check-up for a dog."""

    dog = models.ForeignKey(
        "dog_profile.DogProfile", on_delete=models.CASCADE, related_name="macro_analyses"
    )
    context_snapshot = models.JSONField(
        help_text="I dati (medie, eventi) usati per generare questo report."
    )
    ai_report_html = models.TextField(
        help_text="Il referto generato in formato HTML."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Macro-Analisi {self.dog.dog_name} ({self.created_at.date()})"

    class Meta:
        verbose_name = "Macro-Analisi IA"
        verbose_name_plural = "Macro-Analisi IA"
        ordering = ["-created_at"]
