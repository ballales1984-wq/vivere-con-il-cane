from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import BlogPost, Category
import requests
import os


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


IMPORTANCE_LEVELS = [
    ("high", "Alta"),
    ("medium", "Media"),
    ("low", "Basica"),
]

LENGTH_LEVELS = [
    ("short", "Breve"),
    ("medium", "Medio"),
    ("long", "Lungo"),
    ("extended", "Esteso"),
]


class Command(BaseCommand):
    help = "Generate a blog article using AI"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Topic for the article")
        parser.add_argument("--category", type=str, default=None, help="Category name")
        parser.add_argument("--save", action="store_true", help="Save to database")

    def handle(self, *args, **options):
        topic = options["topic"]
        category_name = options.get("category")

        self.stdout.write(f"Generating: {topic}")

        if not OPENAI_API_KEY:
            content = self._sample_article(topic)
        else:
            content = self._generate_with_ai(topic)

        if options.get("save"):
            post = BlogPost.objects.create(
                title=topic.title(),
                content=content,
                category=Category.objects.filter(name__icontains=category_name).first()
                if category_name
                else None,
                published=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Saved: {post.title}"))
        else:
            self.stdout.write(content[:300])

    def _sample_article(self, topic):
        return f"""#{topic.title()}

Introduzione sul {topic}. I cani sono compagni fedeli.

## Perché è importante

Avere un cane arricchisce la vita quotidiana.

## Consigli pratici

1. Dedicate tempo alla cura
2. Fate attività fisica
3. Consultate il veterinario

## Conclusione

Un cane felice è un padrone felice."""

    def _generate_with_ai(self, topic):
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Scrivi articoli utili per proprietari di cani.",
                        },
                        {"role": "user", "content": f"Articolo su: {topic}"},
                    ],
                },
                timeout=60,
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {e}"
