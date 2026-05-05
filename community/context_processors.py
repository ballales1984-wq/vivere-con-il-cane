from django.core.cache import cache
from .models import Discussion, UserReputation, Notification

def community_stats(request):
    """Aggiunge statistiche della community al contesto del template."""
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = request.user.community_notifications.filter(is_read=False).count()

    discussions_total = cache.get('community_stats:discussions_total')
    if discussions_total is None:
        discussions_total = Discussion.objects.filter(is_approved=True).count()
        cache.set('community_stats:discussions_total', discussions_total, 300)

    top_contributors = cache.get('community_stats:top_contributors')
    if top_contributors is None:
        top_contributors = list(UserReputation.objects.all().order_by("-points")[:5])
        cache.set('community_stats:top_contributors', top_contributors, 300)

    return {
        "community_stats": {
            "discussions_total": discussions_total,
        },
        "top_contributors": top_contributors,
        "unread_notifications_count": unread_count,
    }
