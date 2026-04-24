from django.contrib.sitemaps import Sitemap
from blog.models import BlogPost
from knowledge.models import Problem, BreedInsight
from django.urls import reverse


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = "https"

    def items(self):
        return BlogPost.objects.filter(published=True).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("blog_detail", args=[obj.slug])


class ProblemSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return Problem.objects.all()

    def location(self, obj):
        return reverse("problem_detail", args=[obj.slug])


class BreedSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return BreedInsight.objects.all()

    def location(self, obj):
        return reverse("breed_detail", args=[obj.slug])


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return [
            "home",
            "blog_list",
            "tools_index",
            "problem_list",
            "breed_list",
            "about",
        ]

    def location(self, item):
        return reverse(item)
