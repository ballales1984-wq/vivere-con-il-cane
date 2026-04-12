from django.contrib import admin
from .models import DogProfile, HealthEvent, DailyLog


@admin.register(DogProfile)
class DogProfileAdmin(admin.ModelAdmin):
    list_display = ["dog_name", "name", "breed", "created_at"]
    search_fields = ["dog_name", "name"]


@admin.register(HealthEvent)
class HealthEventAdmin(admin.ModelAdmin):
    list_display = ["title", "dog", "event_type", "date"]
    list_filter = ["event_type", "date"]


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ["dog", "date", "sleep_hours", "play_minutes", "walk_minutes"]
    list_filter = ["date"]
