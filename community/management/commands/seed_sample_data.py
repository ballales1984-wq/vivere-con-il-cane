from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from community.models import Category, Discussion, Post, UserReputation
from dog_profile.models import DogProfile
import random


class Command(BaseCommand):
    help = "Crea dati di esempio per testare la community"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=5,
            help="Numero di utenti da creare",
        )
        parser.add_argument(
            "--discussions",
            type=int,
            default=10,
            help="Numero di discussioni da creare",
        )

    def handle(self, *args, **kwargs):
        num_users = kwargs["users"]
        num_discussions = kwargs["discussions"]

        self.stdout.write(f"*** Creazione di {num_users} utenti e {num_discussions} discussioni...")

        # Assicurati che le categorie esistano
        categories = list(Category.objects.filter(is_active=True))
        if not categories:
            self.stdout.write(self.style.WARNING("  ! Nessuna categoria trovata. Eseguire 'seed_community' prima."))
            return

        for i in range(num_users):
            username = f"utente{i+1}"
            email = f"utente{i+1}@example.com"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": f"Utente{i+1}",
                },
            )
            if created:
                user.set_password("password123")
                user.save()
                # Crea reputation
                UserReputation.objects.get_or_create(user=user)
                self.stdout.write(f"  + Utente creato: {username}")

                # Crea un cane per l'utente (50% delle volte)
                if random.random() > 0.5:
                    dog = DogProfile.objects.create(
                        owner=user,
                        name=f"Proprietario {user.first_name}",
                        dog_name=f"Cane{i+1}",
                        breed=random.choice(["Labrador", "Pastore Tedesco", "Golden Retriever", "Meticcio"]),
                        gender=random.choice(["male", "female"]),
                        is_neutered=random.choice([True, False]),
                        activity_level=random.choice(["low", "moderate", "high"]),
                    )
                    self.stdout.write(f"    + Cane creato: {dog.dog_name}")

        # Recupera tutti gli utenti
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR("  ! Nessun utente trovato."))
            return

        titles = [
            "Come gestire l'ansia da separazione?",
            "Consigli sul cibo per cuccioli",
            "Il mio cane abbaia sempre al postino",
            "Esercizi di obedience base",
            "Quale attività sportiva consigliate?",
            "Vaccini annuali - cosa include?",
            "Come socializzare un cane timido?",
            "Problemi di digestione con il cibo secco",
            "Addestramento al guinzaglio",
            "Cane iperattivo - come gestirlo?",
            "Sintomi di intolleranza alimentare",
            "Come insegnare il rientro a casa?",
            "Il mio cane non vuole uscire",
            "Erbe aromatiche sicure per cani?",
            "Come calcolare il peso ideale?",
        ]

        for i in range(num_discussions):
            title = random.choice(titles) + f" (Part {i+1})"
            author = random.choice(users)
            category = random.choice(categories)

            discussion = Discussion.objects.create(
                title=title,
                slug=f"sample-discussion-{i+1}",
                category=category,
                author=author,
                content=f"Questo è un contenuto di esempio per la discussione '{title}'. Descrivo brevemente il problema o la domanda che voglio porre alla community. Spero di ricevere consigli utili da altri appassionati di cani come me.",
                status="open",
                priority="normal",
                is_approved=True,
                view_count=random.randint(0, 100),
                like_count=0,
                reply_count=0,
            )

            # Aggiungi 0-3 risposte
            num_replies = random.randint(0, 3)
            for j in range(num_replies):
                replier = random.choice([u for u in users if u != author])
                Post.objects.create(
                    discussion=discussion,
                    author=replier,
                    content=f"Questa è una risposta di esempio #{j+1}. Condivido la mia esperienza e do qualche consiglio basato sulla mia situazione.",
                    parent=None,
                )

            # Aggiorna conteggio
            discussion.reply_count = discussion.posts.count()
            discussion.save()

            self.stdout.write(f"  + Discussione creata: {title[:50]}...")

        self.stdout.write(self.style.SUCCESS(f"\n== Dati di esempio creati con successo! =="))
        self.stdout.write(f"\nPer testare la community:")
        self.stdout.write(f"1. Accedi come uno degli utenti creati (username: utente1, utente2, ... - password: password123)")
        self.stdout.write(f"2. Vai a http://localhost:8000/community/")
        self.stdout.write(f"3. Esplora le {num_discussions} discussioni di esempio\n")
