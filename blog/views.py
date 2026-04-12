from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from .models import BlogPost


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


def blog_detail(request, slug):
    try:
        post = get_object_or_404(BlogPost, slug=slug, published=True)
    except Exception:
        from django.http import Http404

        raise Http404("Post not found")
    return render(request, "blog/detail.html", {"post": post})
