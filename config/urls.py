from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from blog import views as blog_views
from canine_tools import views as tools_views
from blog.sitemap import (
    BlogPostSitemap,
    ProblemSitemap,
    BreedSitemap,
    StaticViewSitemap,
)
from django.contrib.sitemaps.views import sitemap
from marketing import views as marketing_views

sitemaps = {
    "blog": BlogPostSitemap(),
    "problemi": ProblemSitemap(),
    "razze": BreedSitemap(),
    "static": StaticViewSitemap(),
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "manifest.json",
        TemplateView.as_view(
            template_name="pwa/manifest.json", content_type="application/json"
        ),
        name="manifest",
    ),
    path(
        "service-worker.js",
        TemplateView.as_view(
            template_name="pwa/service-worker.js", content_type="application/javascript"
        ),
        name="service_worker",
    ),
    path("ping/", blog_views.ping, name="ping"),
    path("health/", blog_views.health, name="health"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

urlpatterns += i18n_patterns(
    path("", blog_views.home_page, name="home"),
    path("chi-sono/", blog_views.about_page, name="about"),
    path("blog/", include("blog.urls")),
    path("tool/", include("canine_tools.urls", namespace="canine_tools")),
    path("privacy/", tools_views.privacy_policy, name="privacy_policy"),
    path("terms/", tools_views.terms_of_service, name="terms_of_service"),
    path("cookie/", tools_views.cookie_policy, name="cookie_policy"),
    path("cane/", include("dog_profile.urls")),
    path("knowledge/", include("knowledge.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("signup/", tools_views.signup, name="signup"),
    path(
        "newsletter/subscribe/",
        marketing_views.subscribe_newsletter,
        name="subscribe_newsletter",
    ),
    path(
        "unsubscribe/<uuid:token>/",
        marketing_views.unsubscribe_newsletter,
        name="unsubscribe_newsletter",
    ),
)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]
    )
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
