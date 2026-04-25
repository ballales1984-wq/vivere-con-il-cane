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
    path("api/heart/analyze/", views.heart_analyze, name="heart_analyze"),
]
