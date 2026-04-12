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


def blog_detail(request, slug):
    try:
        post = get_object_or_404(BlogPost, slug=slug, published=True)
    except Exception:
        from django.http import Http404

        raise Http404("Post not found")
    return render(request, "blog/detail.html", {"post": post})


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
