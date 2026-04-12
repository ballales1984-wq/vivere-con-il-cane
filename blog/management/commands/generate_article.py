from django.core.management.base import BaseCommand
from blog.models import BlogPost, Category
import requests
import os


GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
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
    help = "Generate a blog article using Grok or OpenAI AI"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Topic for the article")
        parser.add_argument("--category", type=str, default=None, help="Category name")
        parser.add_argument("--save", action="store_true", help="Save to database")
        parser.add_argument(
            "--importance",
            type=str,
            default="medium",
            help="Importance: high/medium/low",
        )
        parser.add_argument(
            "--length", type=str, default="medium", help="Length: short/medium/long"
        )
        parser.add_argument(
            "--source", type=str, default="ai", help="Source: ai/manual/news/translated"
        )

    def handle(self, *args, **options):
        topic = options["topic"]
        category_name = options.get("category")
        importance = options.get("importance")
        length = options.get("length")
        source = options.get("source")

        self.stdout.write(f"Generating: {topic}")
        self.stdout.write(f"Importance: {importance}, Length: {length}")

        if GROK_API_KEY and GROK_API_KEY != "your_grok_key_here":
            content = self._generate_grok(topic)
        elif OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_key_here":
            content = self._generate_openai(topic)
        else:
            content = self._sample_article(topic)

        if options.get("save"):
            category = None
            if category_name:
                category = Category.objects.filter(
                    name__icontains=category_name
                ).first()

            post = BlogPost.objects.create(
                title=topic.title(),
                content=content,
                category=category,
                importance=importance,
                length=length,
                source=source,
                published=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Saved: {post.title} (ID: {post.id})")
            )
        else:
            self.stdout.write(content[:500])

    def _generate_grok(self, topic):
        """Generate using Grok API (xAI)"""
        prompt = f"""Scrivi un articolo SEO in italiano per un blog sui cani chiamato "Vivere con il Cane".

Topic: {topic}

Requisiti:
- 500-800 parole
- linguaggio semplice e chiaro
- utile per chi vive con un cane
- usa esempi pratici

Struttura:
- Titolo
- Introduzione (2-3 righe)
- Sezioni con sottotitoli
- Liste puntate
- Conclusione pratica"""

        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GROK_API_KEY}",
                },
                json={
                    "model": "grok-2-1212",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Sei un esperto di educazione cinofila italiana. Scrivi articoli utili e pratici per proprietari di cani.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=60,
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error with Grok: {e}"

    def _generate_openai(self, topic):
        """Generate using OpenAI API"""
        prompt = f"""Scrivi un articolo SEO in italiano per un blog sui cani.

Topic: {topic}

Requisiti:
- 500-800 parole
- linguaggio semplice
- utile per proprietari di cani"""

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
                        {"role": "system", "content": "Esperto di cani."},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=60,
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {e}"

    def _sample_article(self, topic):
        """Fallback sample article"""
        return f"""#{topic.title()}

## Introduzione
Il {topic} è un tema importante per tutti i proprietari di cani.

## Perché è importante
Avere un cane richiede attenzione e cura quotidiana.

## Consigli pratici
1. Dedicate tempo alla cura
2. Fate attività fisica
3. Consultate il veterinario regolarmente

## Conclusione
Un cane ben curato è un compagno felice."""
