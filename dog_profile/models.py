from django.db import models
from django.utils.text import slugify


class DogProfile(models.Model):
    """Owner with their dog profile."""

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
