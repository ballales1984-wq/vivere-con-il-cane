from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from .models import Discussion, Post, Like, Vote, Notification, UserReputation, UserBadge, Badge


def get_or_create_reputation(user):
    """Helper per ottenere o creare reputation di un utente."""
    if not user.is_authenticated:
        return None
    rep, created = UserReputation.objects.get_or_create(user=user)
    return rep


@receiver(post_save, sender=Discussion)
def discussion_created(sender, instance, created, **kwargs):
    """Aggiorna reputazione quando viene creata una discussione."""
    if created and instance.author:
        rep = get_or_create_reputation(instance.author)
        if rep:
            with transaction.atomic():
                rep.discussions_created += 1
                rep.points += 10
                rep.save()
                check_badges(instance.author)


@receiver(post_save, sender=Post)
def post_created(sender, instance, created, **kwargs):
    """Aggiorna reputazione quando viene creato un post."""
    if created and instance.author:
        rep = get_or_create_reputation(instance.author)
        if rep:
            with transaction.atomic():
                rep.posts_created += 1
                rep.points += 2
                rep.save()
                check_badges(instance.author)

        # Notifica autore discussione
        if instance.discussion.author != instance.author:
            Notification.objects.create(
                recipient=instance.discussion.author,
                sender=instance.author,
                discussion=instance.discussion,
                post=instance,
                notification_type="reply",
                message=f"{instance.author.username} ha risposto alla tua discussione '{instance.discussion.title[:50]}...'",
            )


@receiver(post_save, sender=Post)
def solution_marked(sender, instance, created, **kwargs):
    """Gestisce quando un post viene marcato come soluzione."""
    if instance.is_solution and not created:
        # Solo se il flag è stato appena impostato
        # Questo non cattura l'aggiornamento, ma gestiamo anche post_save
        rep = get_or_create_reputation(instance.author)
        if rep:
            with transaction.atomic():
                rep.solutions_provided += 1
                rep.points += 20  # +20 pt per soluzione accettata
                rep.save()
                check_badges(instance.author)

        # Notifica autore discussione
        Notification.objects.create(
            recipient=instance.discussion.author,
            sender=instance.author,
            discussion=instance.discussion,
            post=instance,
            notification_type="solution",
            message=f"La tua risposta è stata accettata come soluzione!",
        )


@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    """Rimuove punti se un post viene cancellato."""
    if instance.author:
        rep = get_or_create_reputation(instance.author)
        if rep:
            with transaction.atomic():
                rep.posts_created = max(0, rep.posts_created - 1)
                rep.points = max(0, rep.points - 2)
                rep.save()


@receiver(post_save, sender=Like)
def like_created(sender, instance, created, **kwargs):
    """Aggiorna conteggi like."""
    if created:
        if instance.content_type == "discussion":
            instance.discussion.like_count = instance.discussion.discussion_likes.count()
            instance.discussion.save(update_fields=["like_count"])
        elif instance.content_type == "post":
            instance.post.like_count = instance.post.post_likes.count()
            instance.post.save(update_fields=["like_count"])
            # +1 pt all'autore del post
            rep = get_or_create_reputation(instance.post.author)
            if rep:
                rep.likes_received += 1
                rep.points += 1
                rep.save()

        # Notifica autore (se non è chi ha messo like)
        if instance.content_type == "post" and instance.post.author != instance.user:
            Notification.objects.create(
                recipient=instance.post.author,
                sender=instance.user,
                discussion=instance.post.discussion,
                post=instance.post,
                notification_type="like",
                message=f"{instance.user.username} ha apprezzato il tuo post",
            )


@receiver(post_delete, sender=Like)
def like_deleted(sender, instance, **kwargs):
    """Rimuove like e aggiorna conteggi."""
    if instance.content_type == "discussion":
        instance.discussion.like_count = instance.discussion.discussion_likes.count()
        instance.discussion.save(update_fields=["like_count"])
    elif instance.content_type == "post":
        instance.post.like_count = instance.post.post_likes.count()
        instance.post.save(update_fields=["like_count"])
        rep = get_or_create_reputation(instance.post.author)
        if rep:
            rep.likes_received = max(0, rep.likes_received - 1)
            rep.points = max(0, rep.points - 1)
            rep.save()


@receiver(post_save, sender=Vote)
def vote_created(sender, instance, created, **kwargs):
    """Aggiorna reputazione per voti (solo upvote)."""
    if created and instance.vote_type == "up":
        rep = get_or_create_reputation(instance.post.author)
        if rep:
            rep.helpful_votes_received += 1
            rep.points += 5  # +5 pt per upvote
            rep.save()
            check_badges(instance.post.author)


def check_badges(user):
    """Controlla e assegna badge all'utente in base alla reputazione."""
    badges_to_award = []

    # Badge per discussione create
    rep = user.reputation
    if rep.discussions_created >= 1:
        badge = Badge.objects.filter(slug="prima-discussione").first()
        if badge:
            badges_to_award.append(badge)
    if rep.discussions_created >= 10:
        badge = Badge.objects.filter(slug="abile-conversatore").first()
        if badge:
            badges_to_award.append(badge)
    if rep.discussions_created >= 50:
        badge = Badge.objects.filter(slug="maestro-delle-discussioni").first()
        if badge:
            badges_to_award.append(badge)

    # Badge per post create
    if rep.posts_created >= 5:
        badge = Badge.objects.filter(slug="collaboratore").first()
        if badge:
            badges_to_award.append(badge)
    if rep.posts_created >= 25:
        badge = Badge.objects.filter(slug="esperto-comunitario").first()
        if badge:
            badges_to_award.append(badge)

    # Badge per soluzioni
    if rep.solutions_provided >= 1:
        badge = Badge.objects.filter(slug="risolutore").first()
        if badge:
            badges_to_award.append(badge)
    if rep.solutions_provided >= 5:
        badge = Badge.objects.filter(slug="eroe-della-comunita").first()
        if badge:
            badges_to_award.append(badge)

    # Badge per like ricevuti
    if rep.likes_received >= 10:
        badge = Badge.objects.filter(slug="popolare").first()
        if badge:
            badges_to_award.append(badge)
    if rep.likes_received >= 50:
        badge = Badge.objects.filter(slug="influencer").first()
        if badge:
            badges_to_award.append(badge)

    # Badge per voti utili
    if rep.helpful_votes_received >= 5:
        badge = Badge.objects.filter(slug="consigliere").first()
        if badge:
            badges_to_award.append(badge)
    if rep.helpful_votes_received >= 25:
        badge = Badge.objects.filter(slug="guru").first()
        if badge:
            badges_to_award.append(badge)

    # Assegna badge
    for badge in badges_to_award:
        UserBadge.objects.get_or_create(user=user, badge=badge)
