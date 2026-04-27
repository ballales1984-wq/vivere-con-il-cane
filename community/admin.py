from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Category,
    Discussion,
    Post,
    Like,
    Vote,
    Notification,
    UserReputation,
    Badge,
    UserBadge,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon", "color", "order", "is_active", "discussion_count"]
    list_editable = ["order", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}

    def discussion_count(self, obj):
        return obj.discussions.count()

    discussion_count.short_description = _("Discussioni")


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "category",
        "status",
        "priority",
        "view_count",
        "like_count",
        "reply_count",
        "last_activity",
        "is_approved",
    ]
    list_filter = ["status", "priority", "category", "is_approved", "created_at"]
    search_fields = ["title", "content", "author__username"]
    readonly_fields = ["view_count", "like_count", "reply_count", "last_activity", "created_at"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["dog"]

    fieldsets = (
        (_("Generale"), {
            "fields": ("title", "slug", "category", "author", "dog", "content")
        }),
        (_("Stato"), {
            "fields": ("status", "priority", "is_approved")
        }),
        (_("Statistiche"), {
            "fields": ("view_count", "like_count", "reply_count", "last_activity", "created_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "short_content",
        "author",
        "discussion",
        "is_solution",
        "is_edited",
        "like_count",
        "created_at",
    ]
    list_filter = ["is_solution", "is_edited", "created_at"]
    search_fields = ["content", "author__username", "discussion__title"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["discussion", "author", "parent"]

    def short_content(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    short_content.short_description = _("Contenuto")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "content_type", "get_target", "created_at"]
    list_filter = ["content_type", "created_at"]
    search_fields = ["user__username"]

    def get_target(self, obj):
        if obj.content_type == "discussion":
            return obj.discussion.title[:50]
        return f"Post {obj.post.id}"

    get_target.short_description = _("Target")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "vote_type", "created_at"]
    list_filter = ["vote_type", "created_at"]
    search_fields = ["user__username"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "recipient",
        "sender",
        "notification_type",
        "short_message",
        "is_read",
        "created_at",
    ]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["recipient__username", "sender__username", "message"]
    readonly_fields = ["created_at"]

    def short_message(self, obj):
        return obj.message[:80] + "..." if len(obj.message) > 80 else obj.message

    short_message.short_description = _("Messaggio")


@admin.register(UserReputation)
class UserReputationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "points",
        "level",
        "discussions_created",
        "posts_created",
        "solutions_provided",
        "helpful_votes_received",
    ]
    search_fields = ["user__username"]
    readonly_fields = ["level", "last_updated"]

    def has_add_permission(self, request):
        return False


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "badge_type", "requirement_type", "requirement_value", "is_active"]
    list_filter = ["badge_type", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ["user", "badge", "earned_at"]
    search_fields = ["user__username", "badge__name"]
    raw_id_fields = ["user", "badge"]
