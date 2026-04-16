from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from .models import BlogPost, PostVote


def ping(request):
    return HttpResponse(f"pong {datetime.now().isoformat()}", content_type="text/plain")


def health(request):
    return JsonResponse({"status": "healthy"})


def blog_list(request):
    posts = []
    try:
        posts = list(BlogPost.objects.filter(published=True).order_by("-created_at"))
    except Exception as e:
        print(f"DB Error: {e}")
    return render(request, "blog/list.html", {"posts": posts})


def home_page(request):
    """Homepage: AI-first with problems and recent posts."""
    posts = []
    problems = []
    try:
        posts = list(
            BlogPost.objects.filter(published=True).order_by("-created_at")[:3]
        )
    except Exception as e:
        print(f"DB Error: {e}")

    try:
        from knowledge.models import Problem

        problems = list(Problem.objects.all().order_by("pk")[:6])
    except Exception as e:
        print(f"Knowledge DB Error: {e}")

    return render(
        request,
        "home.html",
        {"recent_posts": posts, "problems": problems},
    )


def about_page(request):
    """About / Chi Sono page."""
    return render(request, "pages/about.html")


def blog_detail(request, slug):
    try:
        post = get_object_or_404(BlogPost, slug=slug, published=True)
    except Exception:
        from django.http import Http404

        raise Http404("Post not found")

    # Articoli correlati: stessa categoria, escludi l'attuale
    related_posts = []
    if post.category:
        related_posts = list(
            BlogPost.objects.filter(published=True, category=post.category)
            .exclude(id=post.id)
            .order_by("-created_at")[:3]
        )

    return render(
        request,
        "blog/detail.html",
        {"post": post, "related_posts": related_posts},
    )


def vote_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    ip = get_client_ip(request)

    existing_vote = PostVote.objects.filter(post=post, ip_address=ip).exists()
    if existing_vote:
        return JsonResponse({"voted": True, "votes": post.votes_count})

    PostVote.objects.create(post=post, ip_address=ip)
    post.votes_count += 1
    post.save()

    return JsonResponse({"voted": True, "votes": post.votes_count})


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
