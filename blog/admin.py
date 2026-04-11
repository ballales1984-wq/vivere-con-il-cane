from django.contrib import admin
from .models import Category, BlogPost


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "created_at", "published"]
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
