from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorie"
        ordering = ["name"]


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ("draft", "Bozza"),
        ("published", "Pubblicato"),
        ("archived", "Archiviato"),
    ]

    IMPORTANCE_CHOICES = [
        ("high", "Alta"),
        ("medium", "Media"),
        ("low", "Basica"),
    ]

    LENGTH_CHOICES = [
        ("short", "Breve"),
        ("medium", "Medio"),
        ("long", "Lungo"),
    ]

    SOURCE_CHOICES = [
        ("ai", "AI Generato"),
        ("manual", "Manuale"),
        ("news", "Notizia"),
        ("translated", "Tradotto"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="blog/", blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="published"
    )
    importance = models.CharField(
        max_length=10, choices=IMPORTANCE_CHOICES, default="medium"
    )
    length = models.CharField(max_length=10, choices=LENGTH_CHOICES, default="medium")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="manual")
    publish_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    published = models.BooleanField(default=True)
    votes_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class PostVote(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="votes")
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "ip_address")
        verbose_name = "Voto"
        verbose_name_plural = "Voti"

    def __str__(self):
        return f"Voto per {self.post.title}"
