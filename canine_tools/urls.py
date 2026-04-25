from django.urls import path
from . import views

app_name = "canine_tools"

urlpatterns = [
    path("", views.tools_index, name="tools_index"),
    path("cibo/", views.food_calculator, name="food_calculator"),
    path("eta/", views.age_calculator, name="age_calculator"),
    path("quiz/", views.dog_quiz, name="dog_quiz"),
    path("cuore/", views.heart_recorder, name="heart_recorder"),
    path("cuore/<int:recording_id>/", views.heart_recording_detail, name="heart_recording_detail"),
    path("cuore/<int:recording_id>/csv/", views.heart_recording_export_csv, name="heart_recording_export_csv"),
    path("cuore/<int:recording_id>/ai/", views.heart_analyze_ai, name="heart_analyze_ai"),
    path("cuore/api/analyze/", views.heart_analyze, name="heart_analyze"),
    # Google Health/Fit
    path("google/fit/auth/", views.google_fit_auth_start, name="google_fit_auth"),
    path("google/fit/callback/", views.google_fit_callback, name="google_fit_callback"),
    path("google/fit/sync/", views.health_sync, name="health_sync"),
    path("google/fit/sync/api/", views.sync_health_data, name="sync_health_data"),
    path("dog/<int:dog_id>/health/", views.health_data_history, name="health_data_history"),
]
