from django.urls import path
from . import views

urlpatterns = [
    path("problemi/", views.problem_list, name="problem_list"),
    path("problemi/<slug:slug>/", views.problem_detail, name="problem_detail"),
    path("razze/", views.breed_list, name="breed_list"),
    path("razze/<slug:slug>/", views.breed_detail, name="breed_detail"),
    path("analizza/", views.analyze_problem, name="analyze_problem"),
    path(
        "analizza/<int:analysis_id>/result/",
        views.update_analysis_result,
        name="update_analysis_result",
    ),
    path("history/<int:dog_id>/", views.analysis_history, name="analysis_history"),
    path("analizza/<int:analysis_id>/pdf/", views.download_analysis_pdf, name="download_analysis_pdf"),
]
