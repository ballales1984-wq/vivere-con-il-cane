from django.urls import path
from . import views
from .api import (
    wp_blog_posts,
    wp_blog_categories,
    wp_blog_stats,
    wp_blog_recent,
    wp_dog_tools,
    wp_problems,
    wp_newsletter_subscribe,
    wp_api_health,
    wp_blog_detail_meta,
)

urlpatterns = [
    path("", views.blog_list, name="blog_list"),
    path("<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("vote/<int:post_id>/", views.vote_post, name="vote_post"),
    
    # API WordPress (Marketing)
    path("api/posts/", wp_blog_posts, name="wp_api_posts"),
    path("api/categories/", wp_blog_categories, name="wp_api_categories"),
    path("api/stats/", wp_blog_stats, name="wp_api_stats"),
    path("api/recent/", wp_blog_recent, name="wp_api_recent"),
    path("api/tools/", wp_dog_tools, name="wp_api_tools"),
    path("api/problems/", wp_problems, name="wp_api_problems"),
    path("api/newsletter/subscribe/", wp_newsletter_subscribe, name="wp_api_newsletter"),
    path("api/health/", wp_api_health, name="wp_api_health"),
    path("api/posts/<slug:slug>/meta/", wp_blog_detail_meta, name="wp_api_post_meta"),
]
