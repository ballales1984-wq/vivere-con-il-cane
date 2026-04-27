from django.core.management.base import BaseCommand
from django.db import transaction
from community.models import UserReputation, Discussion, Post, Like, Vote
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Ricalcola la reputazione di tutti gli utenti da zero"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="Username specifico per cui ricalcolare la reputazione",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra cosa verrebbe fatto senza salvare",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        target_username = options.get("user")

        users = User.objects.all()
        if target_username:
            users = users.filter(username=target_username)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f"Utente '{target_username}' non trovato."))
                return

        self.stdout.write(f"Ricalcolo reputazione per {users.count()} utenti...")

        for user in users:
            rep, created = UserReputation.objects.get_or_create(user=user)

            # Calcola statistiche
            discussions_count = Discussion.objects.filter(author=user, is_approved=True).count()
            posts_count = Post.objects.filter(author=user).count()
            solutions_count = Post.objects.filter(author=user, is_solution=True).count()
            likes_received = Like.objects.filter(post__author=user, content_type="post").count()
            helpful_votes = Vote.objects.filter(post__author=user, vote_type="up").count()

            # Calcola punti totali
            total_points = (
                discussions_count * 10 +  # +10 per discussione
                posts_count * 2 +          # +2 per post
                solutions_count * 20 +     # +20 per soluzione
                likes_received * 1 +       # +1 per like ricevuto
                helpful_votes * 5          # +5 per upvote ricevuto
            )

            if not dry_run:
                with transaction.atomic():
                    rep.discussions_created = discussions_count
                    rep.posts_created = posts_count
                    rep.solutions_provided = solutions_count
                    rep.likes_received = likes_received
                    rep.helpful_votes_received = helpful_votes
                    rep.points = total_points
                    rep.update_reputation()

                self.stdout.write(
                    f"  + {user.username}: {discussions_count} disc, {posts_count} post, {solutions_count} sol, {total_points} pt (liv {rep.level})"
                )
            else:
                self.stdout.write(
                    f"  -> {user.username}: {discussions_count} disc, {posts_count} post, {solutions_count} sol, {total_points} pt (liv ?)"
                )

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry-run: nessun dato salvato."))
        else:
            self.stdout.write(self.style.SUCCESS("\n== Reputazioni ricalcolate con successo! =="))
