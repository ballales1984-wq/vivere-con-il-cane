from django.contrib.sitemaps import Sitemap
from blog.models import BlogPost
from knowledge.models import Problem, BreedInsight
from django.urls import reverse


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated_at


class ProblemSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Problem.objects.all()


class BreedSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BreedInsight.objects.all()


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return [
            "home",
            "blog_list",
            "tools_index",
            "dashboard",
            "problem_list",
            "breed_list",
        ]

    def location(self, item):
        return reverse(item)
