from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class DogProfile(models.Model):
    """Owner with their dog profile."""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profiles", null=True, blank=True
    )

    name = models.CharField(max_length=100)
    dog_name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=[("male", "Maschio"), ("female", "Femmina")], blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.dog_name} ({self.name})"

    def get_age(self):
        if not self.birth_date:
            return "?"
        from datetime import date

        today = date.today()
        age = today.year - self.birth_date.year
        if today.month < self.birth_date.month or (
            today.month == self.birth_date.month and today.day < self.birth_date.day
        ):
            age -= 1
        return str(age)

    @property
    def events_count(self):
        return self.events.count()

    class Meta:
        verbose_name = "Profilo Cane"
        verbose_name_plural = "Profili Cani"


class HealthEvent(models.Model):
    """Health events for a dog."""

    EVENT_TYPES = [
        ("vaccine", "Vaccino"),
        ("checkup", "Visita"),
        ("medicine", "Medicina"),
        ("illness", "Malattia"),
        ("injury", "Infortunio"),
        ("other", "Altro"),
    ]

    dog = models.ForeignKey(DogProfile, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    next_date = models.DateField(blank=True, null=True)
    veterinarian = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.dog.dog_name}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Evento Salute"
        verbose_name_plural = "Eventi Salute"


class VeterinaryMedia(models.Model):
    """Media files (photos/videos) attached to veterinary request."""

    MEDIA_TYPES = [
        ("photo", "Foto"),
        ("video", "Video"),
    ]

    request = models.ForeignKey(
        "VeterinaryRequest", on_delete=models.CASCADE, related_name="media_files"
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to="veterinary_requests/%Y/%m/")
    caption = models.CharField(max_length=200, blank=True)
    upload_order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_media_type_display()}: {self.caption or self.file.name}"


class VeterinaryRequest(models.Model):
    """Structured request sent to veterinarian with AI summary and curated media."""

    REQUEST_STATUS = [
        ("draft", "Bozza"),
        ("ready", "Pronto"),
        ("sent", "Inviato"),
    ]

    dog = models.ForeignKey(
        DogProfile, on_delete=models.CASCADE, related_name="vet_requests"
    )
    analysis = models.ForeignKey(
        "knowledge.DogAnalysis",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vet_requests",
    )
    problem_description = models.TextField(help_text="Descrizione del problema")
    ai_summary = models.TextField(blank=True, help_text="Riassunto AI generato")
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default="draft")
    vet_name = models.CharField(max_length=200, blank=True)
    vet_email = models.EmailField(blank=True)
    vet_phone = models.CharField(max_length=50, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Richiesta vet per {self.dog.dog_name} - {self.created_at.date()}"


class DailyLog(models.Model):
    """Daily activity log for the dog."""

    dog = models.ForeignKey(
        DogProfile, on_delete=models.CASCADE, related_name="daily_logs"
    )
    date = models.DateField()
    sleep_hours = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    play_minutes = models.IntegerField(default=0)
    walk_minutes = models.IntegerField(default=0)
    food_grams = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dog.dog_name} - {self.date}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Registro Giornaliero"
        verbose_name_plural = "Registri Giornalieri"
