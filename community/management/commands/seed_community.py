from django.core.management.base import BaseCommand
from django.utils.text import slugify
from community.models import Category, Badge


class Command(BaseCommand):
    help = "Crea categorie e badge iniziali per la community"

    def handle(self, *args, **kwargs):
        # Categorie predefinite
        categories_data = [
            {
                "name": "Alimentazione",
                "description": "Domande e consigli sull'alimentazione del tuo cane: crocchette, diete, integratori, intolleranze.",
                "icon": "🍖",
                "color": "#059669",
                "order": 1,
            },
            {
                "name": "Salute",
                "description": "Discussioni su salute, malattie, vaccinazioni, visite veterinarie e benessere generale.",
                "icon": "💊",
                "color": "#dc2626",
                "order": 2,
            },
            {
                "name": "Comportamento",
                "description": "Problematiche comportamentali: ansia, aggressività, socializzazione, abbaio, morsi.",
                "icon": "🧠",
                "color": "#7c3aed",
                "order": 3,
            },
            {
                "name": "Educazione",
                "description": "Consigli per l'educazione e l'addestramento: base, avanzato, obedience, tricks.",
                "icon": "🎓",
                "color": "#2563eb",
                "order": 4,
            },
            {
                "name": "Attività & Sport",
                "description": "Agility, canicross, trekking, nuoto e altre attività da fare con il tuo cane.",
                "icon": "🏃",
                "color": "#ea580c",
                "order": 5,
            },
            {
                "name": "Cuccioli",
                "description": "Tutto quello che serve sapere per crescere un cucciolo: socializzazione, educazione, cure.",
                "icon": "🐾",
                "color": "#eab308",
                "order": 6,
            },
            {
                "name": "Generale",
                "description": "Discussioni libere su qualsiasi argomento relativo alla vita con il cane.",
                "icon": "💬",
                "color": "#64748b",
                "order": 99,
            },
        ]

        self.stdout.write("*** Creazione categorie...")
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "slug": slugify(cat_data["name"]),
                    "description": cat_data["description"],
                    "icon": cat_data["icon"],
                    "color": cat_data["color"],
                    "order": cat_data["order"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Categoria creata: {cat.name}"))
            else:
                self.stdout.write(f"  = Categoria esistente: {cat.name}")

        # Badge predefiniti
        badges_data = [
            # Badge Discussioni
            {
                "name": "Prima Discussione",
                "slug": "prima-discussione",
                "description": "Hai creato la tua prima discussione nella community.",
                "badge_type": "bronze",
                "icon": "🎉",
                "requirement_type": "discussions_created",
                "requirement_value": 1,
            },
            {
                "name": "Abile Conversatore",
                "slug": "abile-conversatore",
                "description": "Hai creato 10 discussioni nella community.",
                "badge_type": "silver",
                "icon": "💬",
                "requirement_type": "discussions_created",
                "requirement_value": 10,
            },
            {
                "name": "Maestro delle Discussoni",
                "slug": "maestro-delle-discussioni",
                "description": "Hai creato 50 discussioni nella community.",
                "badge_type": "gold",
                "icon": "👑",
                "requirement_type": "discussions_created",
                "requirement_value": 50,
            },
            # Badge Post
            {
                "name": "Collaboratore",
                "slug": "collaboratore",
                "description": "Hai scritto 5 post utili nella community.",
                "badge_type": "bronze",
                "icon": "🤝",
                "requirement_type": "posts_created",
                "requirement_value": 5,
            },
            {
                "name": "Esperto Comunitario",
                "slug": "esperto-comunitario",
                "description": "Hai scritto 25 post utili nella community.",
                "badge_type": "silver",
                "icon": "🎯",
                "requirement_type": "posts_created",
                "requirement_value": 25,
            },
            # Badge Soluzioni
            {
                "name": "Risolutore",
                "slug": "risolutore",
                "description": "La tua prima risposta è stata accettata come soluzione.",
                "badge_type": "bronze",
                "icon": "✅",
                "requirement_type": "solutions_provided",
                "requirement_value": 1,
            },
            {
                "name": "Eroe della Comunità",
                "slug": "eroe-della-comunita",
                "description": "Hai fornito 5 soluzioni accettate.",
                "badge_type": "gold",
                "icon": "🦸",
                "requirement_type": "solutions_provided",
                "requirement_value": 5,
            },
            # Badge Like
            {
                "name": "Popolare",
                "slug": "popolare",
                "description": "Hai ricevuto 10 mi piace sui tuoi post.",
                "badge_type": "bronze",
                "icon": "❤️",
                "requirement_type": "likes_received",
                "requirement_value": 10,
            },
            {
                "name": "Influencer",
                "slug": "influencer",
                "description": "Hai ricevuto 50 mi piace sui tuoi post.",
                "badge_type": "silver",
                "icon": "⭐",
                "requirement_type": "likes_received",
                "requirement_value": 50,
            },
            # Badge Voti Utili
            {
                "name": "Consigliere",
                "slug": "consigliere",
                "description": "Hai ricevuto 5 voti utili (upvote) sui tuoi post.",
                "badge_type": "bronze",
                "icon": "👍",
                "requirement_type": "helpful_votes_received",
                "requirement_value": 5,
            },
            {
                "name": "Guru",
                "slug": "guru",
                "description": "Hai ricevuto 25 voti utili (upvote) sui tuoi post.",
                "badge_type": "platinum",
                "icon": "🧙",
                "requirement_type": "helpful_votes_received",
                "requirement_value": 25,
            },
        ]

        self.stdout.write("\n*** Creazione badge...")
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                slug=badge_data["slug"],
                defaults={
                    "name": badge_data["name"],
                    "description": badge_data["description"],
                    "badge_type": badge_data["badge_type"],
                    "icon": badge_data["icon"],
                    "requirement_type": badge_data["requirement_type"],
                    "requirement_value": badge_data["requirement_value"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Badge creato: {badge.name}"))
            else:
                self.stdout.write(f"  = Badge esistente: {badge.name}")

        self.stdout.write(self.style.SUCCESS("\n== Community inizializzata con successo! =="))
