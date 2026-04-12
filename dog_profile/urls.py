from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile_list, name="profile_list"),
    path("nuovo/", views.profile_new, name="profile_new"),
    path("<int:profile_id>/", views.profile_detail, name="profile_detail"),
    path("<int:profile_id>/evento/", views.profile_add_event, name="profile_add_event"),
    path("<int:profile_id>/log/", views.profile_add_log, name="profile_add_log"),
    path("miod cane/", views.my_dog, name="my_dog"),
]
