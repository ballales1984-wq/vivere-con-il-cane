from django.contrib import admin
from .models import (
    DogProfile,
    MedicalEvent,
    HealthLog,
    VeterinaryRequest,
    VeterinaryMedia,
)


@admin.register(DogProfile)
class DogProfileAdmin(admin.ModelAdmin):
    list_display = [
        "dog_name",
        "name",
        "breed",
        "weight",
        "get_age",
        "activity_level",
        "created_at",
    ]
    search_fields = ["dog_name", "name", "breed"]
    list_filter = ["is_neutered", "activity_level", "diet_type"]
    readonly_fields = ["created_at", "updated_at", "get_age"]

    fieldsets = [
        (
            "Identità",
            {
                "fields": [
                    "name",
                    "dog_name",
                    "breed",
                    "birth_date",
                    "weight",
                    "gender",
                    "is_neutered",
                    "microchip",
                ]
            },
        ),
        (
            "Alimentazione",
            {
                "fields": [
                    "food_type",
                    "food_grams_per_day",
                    "meals_per_day",
                    "diet_type",
                    "supplements",
                    "diet_notes",
                ]
            },
        ),
        (
            "Stile di vita",
            {
                "fields": [
                    "activity_level",
                    "typical_walk_minutes",
                    "sleep_pattern",
                    "is_indoor",
                    "has_access_garden",
                    "socialization_level",
                ]
            },
        ),
        (
            "Farmaci correnti (JSON)",
            {"fields": ["current_medications"], "classes": ["collapse"]},
        ),
        (
            "Storico peso (JSON)",
            {"fields": ["weight_history"], "classes": ["collapse"]},
        ),
        ("Note", {"fields": ["notes"]}),
        ("Metadata", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]


@admin.register(MedicalEvent)
class MedicalEventAdmin(admin.ModelAdmin):
    list_display = ["dog", "event_type", "title", "date", "vet_name"]
    list_filter = ["event_type", "date"]
    search_fields = ["dog__dog_name", "title", "diagnosis"]
    readonly_fields = ["created_at"]


@admin.register(HealthLog)
class HealthLogAdmin(admin.ModelAdmin):
    list_display = ["dog", "date", "log_type", "severity", "short_description"]
    list_filter = ["log_type", "severity", "date"]
    search_fields = ["dog__dog_name", "description", "ai_tags"]
    readonly_fields = ["created_at", "ai_tags", "ai_summary_suggestion"]

    def short_description(self, obj):
        return (
            obj.description[:80] + "…" if len(obj.description) > 80 else obj.description
        )

    short_description.short_description = "Descrizione"


@admin.register(VeterinaryRequest)
class VeterinaryRequestAdmin(admin.ModelAdmin):
    list_display = ["dog", "status", "vet_name", "created_at", "sent_at"]
    list_filter = ["status", "created_at", "sent_at"]
    search_fields = ["dog__dog_name", "problem_description", "ai_summary"]


@admin.register(VeterinaryMedia)
class VeterinaryMediaAdmin(admin.ModelAdmin):
    list_display = ["request", "media_type", "caption", "upload_order", "uploaded_at"]
    list_filter = ["media_type", "uploaded_at"]
    readonly_fields = ["uploaded_at"]
