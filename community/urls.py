from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    # Lista discussioni
    path("", views.discussion_list, name="discussion_list"),
    path("discussioni/", views.discussion_list, name="discussions"),
    path("categorie/", views.category_list, name="category_list"),
    path("categoria/<slug:category_slug>/", views.discussion_list, name="discussions_by_category"),
    path("search/", views.search_ajax, name="search_ajax"),

    # Creazione discussione
    path("nuova/", views.discussion_create, name="discussion_create"),
    path("nuova/crea/", views.discussion_create_submit, name="discussion_create_submit"),

    # Risposte
    path("<slug:slug>/rispondi/", views.post_create_submit, name="post_create"),

    # Azioni
    path("like/toggle/", views.like_toggle, name="like_toggle"),
    path("vota/<int:post_id>/", views.vote_post, name="vote_post"),

    # Profilo utente
    path("utente/<str:username>/", views.user_profile, name="user_profile"),

    # Notifiche
    path("notifiche/", views.notification_list, name="notifications"),
    path("notifiche/leggi/", views.notification_mark_read, name="notification_mark_read"),

    # API
    path("api/counts/", views.discussion_counts, name="discussion_counts"),

    # Dettaglio discussione - DEVE ESSERE PER ULTIMO (cattura tutto)
    path("<slug:slug>/", views.discussion_detail, name="discussion_detail"),
    path("<slug:slug>/segna-soluzione/", views.mark_solution, name="mark_solution"),
]
