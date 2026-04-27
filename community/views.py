from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.utils.text import slugify

from .models import Discussion, Post, Like, Vote, Notification, UserReputation, Badge, UserBadge, Category
from .forms import DiscussionForm, PostForm, DiscussionSearchForm

User = get_user_model()

@require_GET
def discussion_list(request, category_slug=None):
    discussions = Discussion.objects.filter(is_approved=True).select_related("author", "category", "dog")
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug, is_active=True).first()
        if current_category:
            discussions = discussions.filter(category=current_category)
    search_form = DiscussionSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get("query")
        if query:
            discussions = discussions.filter(Q(title__icontains=query) | Q(content__icontains=query))
        form_category = search_form.cleaned_data.get("category")
        if form_category:
            discussions = discussions.filter(category=form_category)
        status = search_form.cleaned_data.get("status")
        if status:
            discussions = discussions.filter(status=status)
        my_dogs = search_form.cleaned_data.get("my_dogs")
        if my_dogs and request.user.is_authenticated:
            discussions = discussions.filter(dog__owner=request.user)
        my_posts = search_form.cleaned_data.get("my_posts")
        if my_posts and request.user.is_authenticated:
            user_post_ids = Post.objects.filter(author=request.user).values_list("discussion_id", flat=True)
            discussions = discussions.filter(id__in=user_post_ids)
    discussions = discussions.annotate(replies_count=Count("posts", distinct=True), likes_count=Count("discussion_likes", distinct=True))
    sort = request.GET.get("sort", "recent")
    if sort == "popular":
        discussions = discussions.order_by("-likes_count", "-last_activity")
    elif sort == "discussed":
        discussions = discussions.order_by("-replies_count", "-last_activity")
    elif sort == "views":
        discussions = discussions.order_by("-view_count", "-last_activity")
    else:
        discussions = discussions.order_by("-last_activity")
    paginator = Paginator(discussions, 15)
    page = request.GET.get("page")
    try:
        discussions_page = paginator.page(page)
    except PageNotAnInteger:
        discussions_page = paginator.page(1)
    except EmptyPage:
        discussions_page = paginator.page(paginator.num_pages)
    categories = Category.objects.filter(is_active=True).annotate(discussion_count=Count("discussions", filter=Q(discussions__is_approved=True)))
    top_contributors = UserReputation.objects.all().order_by("-points")[:5]
    return render(request, "community/list.html", {"discussions": discussions_page, "search_form": search_form, "categories": categories, "sort": sort, "current_category": current_category, "top_users": top_contributors})

@require_GET
def discussion_detail(request, slug):
    discussion = get_object_or_404(Discussion.objects.select_related("author", "category", "dog").prefetch_related("posts__author", "posts__post_votes"), slug=slug, is_approved=True)
    discussion.increment_views()
    posts = discussion.posts.filter(parent__isnull=True).select_related("author").order_by("created_at")
    user_liked_posts = set()
    user_votes = {}
    if request.user.is_authenticated:
        user_liked_posts = set(Like.objects.filter(user=request.user, content_type="post", post__in=posts).values_list("post_id", flat=True))
        user_vote_qs = Vote.objects.filter(user=request.user, post__in=posts)
        user_votes = {v.post_id: v.vote_type for v in user_vote_qs}
    for post in posts:
        post.score_value = post.score
    post_form = PostForm()
    notification_id = request.GET.get("notification")
    if notification_id and request.user.is_authenticated:
        Notification.objects.filter(id=notification_id, recipient=request.user).update(is_read=True)
    return render(request, "community/detail.html", {"discussion": discussion, "posts": posts, "post_form": post_form, "user_liked_posts": user_liked_posts, "user_votes": user_votes})

@login_required
@require_GET
def discussion_create(request):
    categories = Category.objects.filter(is_active=True).order_by("order", "name")
    dogs = request.user.profiles.all().order_by("dog_name") if request.user.is_authenticated else []
    return render(request, "community/create.html", {"categories": categories, "dogs": dogs})

@login_required
@require_POST
def discussion_create_submit(request):
    form = DiscussionForm(request.POST, user=request.user)
    if form.is_valid():
        discussion = form.save(commit=False)
        if not discussion.slug:
            discussion.slug = slugify(discussion.title)
        discussion.save()
        reputation, created = UserReputation.objects.get_or_create(user=request.user)
        reputation.discussions_created += 1
        reputation.points += 10
        reputation.update_reputation()
        messages.success(request, "Discussione creata con successo!")
        return redirect("community:discussion_detail", slug=discussion.slug)
    if request.headers.get("HX-Request"):
        return render(request, "community/_discussion_form.html", {"form": form})
    return render(request, "community/create.html", {"form": form, "categories": Category.objects.filter(is_active=True)})

@login_required
@require_GET
def post_create(request, discussion_slug):
    discussion = get_object_or_404(Discussion, slug=discussion_slug, is_approved=True)
    return redirect("community:discussion_detail", slug=discussion_slug)

@login_required
@require_POST
def post_create_submit(request, slug):
    discussion = get_object_or_404(Discussion, slug=slug, is_approved=True)
    if discussion.status == "closed":
        messages.error(request, "Questa discussione è chiusa.")
        return redirect("community:discussion_detail", slug=slug)
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.discussion = discussion
        post.author = request.user
        post.save()
        discussion.reply_count = discussion.posts.count()
        discussion.save(update_fields=["reply_count"])
        reputation, created = UserReputation.objects.get_or_create(user=request.user)
        reputation.posts_created += 1
        reputation.points += 2
        reputation.update_reputation()
        if discussion.author != request.user:
            Notification.objects.create(recipient=discussion.author, sender=request.user, discussion=discussion, post=post, notification_type="reply", message=f"{request.user.username} ha risposto alla tua discussione '{discussion.title[:50]}...'")
        messages.success(request, "Risposta inviata!")
        return redirect("community:discussion_detail", slug=slug)
    messages.error(request, "Errore nell'invio della risposta.")
    return redirect("community:discussion_detail", slug=slug)

@require_POST
@login_required
def like_toggle(request):
    content_type = request.POST.get("type")
    target_id = request.POST.get("target_id")
    if not content_type or not target_id:
        return JsonResponse({"error": "Parametri mancanti"}, status=400)
    if content_type == "discussion":
        target = get_object_or_404(Discussion, id=target_id)
    elif content_type == "post":
        target = get_object_or_404(Post, id=target_id)
    else:
        return JsonResponse({"error": "Tipo non valido"}, status=400)
    like = Like.objects.filter(user=request.user, content_type=content_type, **{content_type: target}).first()
    if like:
        like.delete()
        liked, delta = False, -1
    else:
        Like.objects.create(user=request.user, content_type=content_type, **{content_type: target})
        liked, delta = True, 1
        if content_type == "post":
            reputation, created = UserReputation.objects.get_or_create(user=target.author)
            reputation.likes_received += 1
            reputation.points += 1
            reputation.update_reputation()
            if target.author != request.user:
                Notification.objects.create(recipient=target.author, sender=request.user, discussion=target.discussion, post=target, notification_type="like", message=f"{request.user.username} ha apprezzato il tuo post")
    if content_type == "discussion":
        target.like_count = target.discussion_likes.count()
    else:
        target.like_count = target.post_likes.count()
    target.save(update_fields=["like_count"])
    return JsonResponse({"liked": liked, "count": target.like_count, "delta": delta})

@require_POST
@login_required
def vote_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    vote_value = request.POST.get("vote")
    if vote_value not in ["up", "down"]:
        return JsonResponse({"error": "Voto non valido"}, status=400)
    user_vote = Vote.objects.filter(user=request.user, post=post).first()
    if user_vote and user_vote.vote_type == vote_value:
        user_vote.delete()
        voted = None
    elif user_vote:
        user_vote.vote_type = vote_value
        user_vote.save()
        voted = vote_value
    else:
        Vote.objects.create(user=request.user, post=post, vote_type=vote_value)
        voted = vote_value
    upvotes = post.post_votes.filter(vote_type="up").count()
    downvotes = post.post_votes.filter(vote_type="down").count()
    score = upvotes - downvotes
    if voted == "up":
        reputation, created = UserReputation.objects.get_or_create(user=post.author)
        reputation.helpful_votes_received += 1
        reputation.points += 5
        reputation.update_reputation()
    return JsonResponse({"voted": voted, "score": score, "upvotes": upvotes, "downvotes": downvotes})

@require_GET
@login_required
def notification_list(request):
    notifications = request.user.community_notifications.all()[:50]
    unread_count = request.user.community_notifications.filter(is_read=False).count()
    return render(request, "community/notifications.html", {"notifications": notifications, "unread_count": unread_count})

@require_POST
@login_required
def notification_mark_read(request):
    notification_id = request.POST.get("notification_id")
    if notification_id:
        Notification.objects.filter(id=notification_id, recipient=request.user).update(is_read=True)
        return JsonResponse({"success": True})
    request.user.community_notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({"success": True})

@require_GET
def category_list(request):
    categories = Category.objects.filter(is_active=True).annotate(discussion_count=Count("discussions", filter=Q(discussions__is_approved=True)), last_post=Count("discussions__posts")).order_by("order", "name")
    stats = {"total": Discussion.objects.filter(is_approved=True).count(), "categories_count": categories.count(), "users_active": User.objects.filter(discussions__is_approved=True).distinct().count()}
    return render(request, "community/categories.html", {"categories": categories, "stats": stats})

@require_GET
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    reputation, created = UserReputation.objects.get_or_create(user=user)
    discussions = Discussion.objects.filter(author=user, is_approved=True).order_by("-created_at")[:5]
    posts = Post.objects.filter(author=user).order_by("-created_at")[:5]
    return render(request, "community/user_profile.html", {"profile_user": user, "reputation": reputation, "recent_discussions": discussions, "recent_posts": posts})

@require_GET
def search_ajax(request):
    query = request.GET.get("q", "")
    if len(query) < 3:
        return JsonResponse({"results": []})
    discussions = Discussion.objects.filter(Q(title__icontains=query) | Q(content__icontains=query), is_approved=True).values("id", "title", "slug")[:10]
    results = [{"id": d["id"], "title": d["title"], "url": reverse("community:discussion_detail", kwargs={"slug": d["slug"]})} for d in discussions]
    return JsonResponse({"results": results})

@require_POST
@login_required
def mark_solution(request, slug):
    discussion = get_object_or_404(Discussion, slug=slug)
    post_id = request.POST.get("post_id")
    if discussion.author != request.user:
        return JsonResponse({"success": False, "error": "Non autorizzato"}, status=403)
    if discussion.status == "closed":
        return JsonResponse({"success": False, "error": "Discussione chiusa"}, status=400)
    post = get_object_or_404(Post, id=post_id, discussion=discussion)
    with transaction.atomic():
        Post.objects.filter(discussion=discussion, is_solution=True).update(is_solution=False)
        post.is_solution = True
        post.save()
        discussion.status = "closed"
        discussion.save()
    return JsonResponse({"success": True})

@require_GET
def discussion_counts(request):
    data = {"total": Discussion.objects.filter(is_approved=True).count(), "recent": Discussion.objects.filter(is_approved=True, created_at__gte=timezone.now() - timezone.timedelta(days=7)).count()}
    return JsonResponse(data)
