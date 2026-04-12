from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_list, name="blog_list"),
    path("<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("vote/<int:post_id>/", views.vote_post, name="vote_post"),
]
