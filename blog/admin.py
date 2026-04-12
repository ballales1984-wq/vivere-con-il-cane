from django.contrib import admin
from .models import Category, BlogPost, PostVote


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "created_at", "published", "votes_count"]
    list_filter = ["category", "created_at", "published"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (
            "Contenuto",
            {"fields": ("title", "slug", "content", "category", "published")},
        ),
        ("Immagine", {"fields": ("image",)}),
    )


@admin.register(PostVote)
class PostVoteAdmin(admin.ModelAdmin):
    list_display = ["post", "ip_address", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["post__title"]
