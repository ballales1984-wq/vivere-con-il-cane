"""
AI Article Generator for Vivere con il Cane

Cl features:
- Topic classification (importance, length)
- News aggregation from web
- Automated content generation

Usage:
    python manage.py generate_article "topic"
    python manage.py fetch_news
"""

import os
import re
import json
import requests
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from blog.models import BlogPost, Category


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"


class ArticleClassification:
    """Classify article based on topic."""

    IMPORTANCE_LEVELS = [
        ("high", "Alta - Guida completa o notizia importante"),
        ("medium", "Media - Consigli pratici"),
        ("low", "Basica - Informazioni rapide"),
    ]

    LENGTH_LEVELS = [
        ("short", "Breve - 300-500 parole"),
        ("medium", "Medio - 500-800 parole"),
        ("long", "Lungo - 800-1200 parole"),
        ("extended", "Esteso - 1200+ parole"),
    ]

    @classmethod
    def classify(cls, topic):
        """Classify a topic based on keywords."""
        topic_lower = topic.lower()

        if any(
            kw in topic_lower
            for kw in [
                "guida completa",
                "todo",
                "full",
                "emergency",
                "urgenza",
                "salute",
            ]
        ):
            importance = "high"
        elif any(
            kw in topic_lower
            for kw in ["notizia", "news", "studio", "ricerca", "nuovo"]
        ):
            importance = "medium"
        else:
            importance = "low"

        if any(kw in topic_lower for kw in ["breve", "quick", "tip", "consiglio"]):
            length = "short"
        elif any(kw in topic_lower for kw in ["completo", "guida", "guide", "full"]):
            length = "long"
        else:
            length = "medium"

        return importance, length


class DogNewsAggregator:
    """Fetch and aggregate dog news from the web."""

    NEWS_SOURCES = [
        {
            "name": "ANMVI",
            "url": "https://www.anmvi.it",
            "keywords": ["cane", "cani", "veterinario"],
        },
        {"name": "ENCI", "url": "https://www.enci.it", "keywords": ["cane", "razze"]},
    ]

    @classmethod
    def fetch_latest_news(cls, max_items=5):
        """Fetch latest dog-related news from web (simulated)."""
        news = []

        sample_news = [
            {
                "title": "Nuove linee guida sull'educazione cinofila",
                "summary": "L'ENCI ha pubblicato nuove linee guida per l'educazione dei cani.",
                "source": "ENCI",
                "date": datetime.now().date(),
                "url": "https://www.enci.it",
            },
            {
                "title": "Studio sui benefici della compagnia degli animali",
                "summary": "Nuova ricerca sui benefici psicologici della convivenza con i cani.",
                "source": "Research",
                "date": datetime.now().date(),
                "url": "https://www.pubmed.gov",
            },
            {
                "title": "Campagna antiparassitari 2026",
                "summary": "Consigli per la protezione dai parassiti stagionali.",
                "source": "ANMVI",
                "date": datetime.now().date(),
                "url": "https://www.anmvi.it",
            },
        ]

        for item in sample_news[:max_items]:
            news.append(item)

        return news


def generate_article(
    topic, category_name=None, importance=None, length=None, api_key=None
):
    """Generate an article using OpenAI API."""
    key = api_key or OPENAI_API_KEY

    if not importance or not length:
        imp, lng = ArticleClassification.classify(topic)
        importance = importance or imp
        length = length or lng

    length_words = {"short": "400", "medium": "700", "long": "1000", "extended": "1500"}
    word_count = length_words.get(length, "700")

    prompt = f"""Scrivi un articolo SEO in italiano per un blog sui cani chiamato "Vivere con il Cane".

Topic: {topic}

Requisiti:
- {word_count} parole
- linguaggio semplice e chiaro
- utile per chi vive con un cane
- evita contenuti generici
- usa esempi pratici

Struttura obbligatoria:
- Titolo coinvolgente
- Introduzione (2-3 righe)
- 4-6 sezioni con sottotitoli H2
- Liste puntate
- Conclusione pratica

Importanza: {importance}
Lunghezza: {length}
"""

    if not key:
        sample_content = f"""# {topic.title()}

Introduzione sul tema del {topic}. I cani sono compagni fedeli che arricchiscono la nostra quotidianità.

## Benefici della convivenza

Avere un cane porta numerosi benefici:
- Companionship e affetto
- Attività fisica quotidiana
- Riduzione dello stress

## Cura e attenzioni

Prendersi cura di un cane richiede:
- Alimentazione equilibrata
- Visite veterinarie regolari
- Attività fisica adeguata

## Conclusione

Un cane ben curato è un companions felice. Dedicate tempo e attenzione al vostro amico a quattro zampe.

Articolo generato automaticamente il {datetime.now().strftime("%d/%m/%Y")}"""
        return sample_content, importance, length, "sample"

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}

    data = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Sei un esperto di educazione cinofila italiana. Scrivi articoli utili e pratici per proprietari di cani.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )

        if response.status_code != 200:
            return f"Error API: {response.status_code}", importance, length, "error"

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return content, importance, length, "ai"

    except Exception as e:
        return f"Error: {str(e)}", importance, length, "error"


class Command(BaseCommand):
    help = "Generate a blog article using AI"

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="Topic for the article")
        parser.add_argument("--category", type=str, default=None, help="Category name")
        parser.add_argument(
            "--importance", type=str, default=None, help="Importance: high/medium/low"
        )
        parser.add_argument(
            "--length", type=str, default=None, help="Length: short/medium/long"
        )
        parser.add_argument("--save", action="store_true", help="Save to database")

    def handle(self, *args, **options):
        topic = options["topic"]
        category = options.get("category")
        importance = options.get("importance")
        length = options.get("length")
        save = options.get("save")

        self.stdout.write(f"Generating article: {topic}")
        self.stdout.write(f"Class: {importance or 'auto'} / {length or 'auto'}")

        content, imp, lng, source = generate_article(
            topic, category, importance, length
        )

        self.stdout.write(f"Source: {source}, Importance: {imp}, Length: {lng}")

        if save and source in ("ai", "sample"):
            lines = content.strip().split("\n")
            title = lines[0].strip("# ").strip() or topic.title()

            category_obj = None
            if category:
                category_obj = Category.objects.filter(name__icontains=category).first()

            post = BlogPost.objects.create(
                title=title, content=content, category=category_obj, published=True
            )

            self.stdout.write(
                self.style.SUCCESS(f"Saved: {post.title} (ID: {post.id})")
            )
        else:
            self.stdout.write(content[:500] + "...")


class CommandFetchNews(BaseCommand):
    help = "Fetch latest dog news"

    def handle(self, *args, **options):
        self.stdout.write("Fetching latest dog news...")

        news = DogNewsAggregator.fetch_latest_news()

        for item in news:
            self.stdout.write(f"- {item['title']}")
            self.stdout.write(f"  {item['summary']}")
            self.stdout.write(f"  Source: {item['source']} - {item['date']}")
            self.stdout.write("")

        self.stdout.write(self.style.SUCCESS(f"Found {len(news)} news items"))
