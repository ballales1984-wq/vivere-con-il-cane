from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog import views as blog_views
from canine_tools import views as tools_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ping/", blog_views.ping, name="ping"),
    path("health/", blog_views.health, name="health"),
    path("", blog_views.blog_list, name="home"),
    path("blog/", include("blog.urls")),
    path("tool/", tools_views.tools_index, name="tools_index"),
    path("tool/cibo/", tools_views.food_calculator, name="food_calculator"),
    path("tool/eta/", tools_views.age_calculator, name="age_calculator"),
    path("tool/quiz/", tools_views.dog_quiz, name="dog_quiz"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]
    )
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
