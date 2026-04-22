from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("lista/", views.profile_list, name="profile_list"),
    path("nuovo/", views.profile_new, name="profile_new"),
    path("<int:profile_id>/", views.profile_detail, name="profile_detail"),
    path("<int:profile_id>/evento/", views.profile_add_event, name="profile_add_event"),
    path("<int:profile_id>/log/", views.profile_add_log, name="profile_add_log"),
    path("<int:profile_id>/dossier/", views.profile_dossier, name="profile_dossier"),
    path("miod cane/", views.my_dog, name="my_dog"),
    # Veterinary Requests
    path(
        "<int:dog_id>/vet/request/start/",
        views.vet_request_start,
        name="vet_request_start",
    ),
    path(
        "<int:dog_id>/vet/request/<int:request_id>/upload/",
        views.vet_request_upload,
        name="vet_request_upload",
    ),
    path(
        "<int:dog_id>/vet/request/<int:request_id>/review/",
        views.vet_request_review,
        name="vet_request_review",
    ),
    path(
        "<int:dog_id>/vet/request/<int:request_id>/",
        views.vet_request_detail,
        name="vet_request_detail",
    ),
    path("vet/requests/", views.vet_request_list, name="vet_request_list"),
]
