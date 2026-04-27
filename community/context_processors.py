from django.contrib.auth.models import User
from .models import Discussion, UserReputation, Notification

def community_stats(request):
    """Aggiunge statistiche della community al contesto del template."""
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = request.user.community_notifications.filter(is_read=False).count()

    return {
        "community_stats": {
            "discussions_total": Discussion.objects.filter(is_approved=True).count(),
            "posts_total": sum(d.reply_count for d in Discussion.objects.filter(is_approved=True)),
        },
        "top_contributors": UserReputation.objects.all().order_by("-points")[:5],
        "unread_notifications_count": unread_count,
    }
