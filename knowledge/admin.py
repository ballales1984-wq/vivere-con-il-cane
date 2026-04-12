from django.contrib import admin
from .models import BreedInsight, Problem, Cause, Solution, DogAnalysis


@admin.register(BreedInsight)
class BreedInsightAdmin(admin.ModelAdmin):
    list_display = ["breed", "energy_level", "social_level"]
    search_fields = ["breed"]
    prepopulated_fields = {"slug": ("breed",)}


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "severity"]
    list_filter = ["category", "severity"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Cause)
class CauseAdmin(admin.ModelAdmin):
    list_display = ["problem", "description", "probability"]
    list_filter = ["probability"]


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ["problem", "title", "solution_type", "difficulty"]
    list_filter = ["solution_type", "difficulty"]


@admin.register(DogAnalysis)
class DogAnalysisAdmin(admin.ModelAdmin):
    list_display = ["dog", "problem", "result", "created_at"]
    list_filter = ["result", "created_at"]
    search_fields = ["dog__dog_name", "user_description"]
