from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Categorie tematiche per le discussioni della community."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Emoji o icona (es: 🍖, 💊, 🎓)",
    )
    color = models.CharField(
        max_length=7,
        default="#059669",
        help_text="Colore esadecimale (es: #059669)",
    )
    order = models.IntegerField(default=0, help_text="Ordine di visualizzazione")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria Community"
        verbose_name_plural = "Categorie Community"
        ordering = ["order", "name"]


class Discussion(models.Model):
    """Discussione principale nella community."""

    STATUS_CHOICES = [
        ("open", _("Aperta")),
        ("closed", _("Chiusa")),
        ("archived", _("Archiviata")),
    ]

    PRIORITY_CHOICES = [
        ("normal", _("Normale")),
        ("pinned", _("Fissa")),
        ("important", _("Importante")),
    ]

    title = models.CharField(max_length=200, verbose_name=_("Titolo"))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="discussions",
        verbose_name=_("Categoria"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="discussions",
        verbose_name=_("Autore"),
    )
    dog = models.ForeignKey(
        "dog_profile.DogProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="discussions",
        verbose_name=_("Cane collegato"),
    )
    content = models.TextField(verbose_name=_("Contenuto"))
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="open",
        verbose_name=_("Stato"),
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="normal",
        verbose_name=_("Priorità"),
    )
    is_approved = models.BooleanField(
        default=True, verbose_name=_("Approved")
    )
    view_count = models.PositiveIntegerField(default=0, verbose_name=_("Visualizzazioni"))
    like_count = models.PositiveIntegerField(default=0, verbose_name=_("Mi piace"))
    reply_count = models.PositiveIntegerField(default=0, verbose_name=_("Risposte"))
    last_activity = models.DateTimeField(auto_now=True, verbose_name=_("Ultima attività"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creata il"))

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Discussion.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Discussione"
        verbose_name_plural = "Discussioni"
        ordering = ["-priority", "-last_activity"]
        indexes = [
            models.Index(fields=["category", "status"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["-last_activity"]),
        ]

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("community:discussion_detail", kwargs={"slug": self.slug})

    def increment_views(self):
        self.view_count += 1
        self.save(update_fields=["view_count"])


class Post(models.Model):
    """Risposta/post all'interno di una discussione."""

    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Discussione"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Autore"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("Post genitore"),
    )
    content = models.TextField(verbose_name=_("Contenuto"))
    is_edited = models.BooleanField(default=False, verbose_name=_("Modificato"))
    edit_reason = models.TextField(blank=True, verbose_name=_("Motivo modifica"))
    edited_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Modificato il"))
    is_solution = models.BooleanField(
        default=False, verbose_name=_("Soluzione")
    )
    like_count = models.PositiveIntegerField(default=0, verbose_name=_("Mi piace"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creato il"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Aggiornato il"))

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Post"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["discussion", "created_at"]),
            models.Index(fields=["author", "created_at"]),
        ]

    def __str__(self):
        return f"Post di {self.author.username} in {self.discussion.title[:30]}..."

    @property
    def score(self):
        """Calcola il punteggio (upvotes - downvotes)."""
        ups = self.post_votes.filter(vote_type="up").count()
        downs = self.post_votes.filter(vote_type="down").count()
        return ups - downs

    @property
    def upvotes_count(self):
        return self.post_votes.filter(vote_type="up").count()

    @property
    def downvotes_count(self):
        return self.post_votes.filter(vote_type="down").count()


class Like(models.Model):
    """Mi piace per discussioni e post."""

    LIKE_TYPES = [
        ("discussion", _("Discussione")),
        ("post", _("Post")),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name=_("Utente"),
    )
    content_type = models.CharField(
        max_length=10,
        choices=LIKE_TYPES,
        verbose_name=_("Tipo"),
    )
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="discussion_likes",
        verbose_name=_("Discussione"),
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="post_likes",
        verbose_name=_("Post"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creato il"))

    class Meta:
        verbose_name = "Mi piace"
        verbose_name_plural = "Mi piace"
        unique_together = ("user", "content_type", "discussion", "post")
        indexes = [
            models.Index(fields=["user", "content_type"]),
            models.Index(fields=["discussion"]),
            models.Index(fields=["post"]),
        ]

    def __str__(self):
        target = self.discussion if self.content_type == "discussion" else self.post
        return f"{self.user.username} likes {target}"


class Vote(models.Model):
    """Votazione per post (upvote/downvote)."""

    VOTE_CHOICES = [
        ("up", _("Su")),
        ("down", _("Giù")),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="votes",
        verbose_name=_("Utente"),
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_votes",
        verbose_name=_("Post"),
    )
    vote_type = models.CharField(
        max_length=4, choices=VOTE_CHOICES, verbose_name=_("Tipo voto")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creato il"))

    class Meta:
        verbose_name = "Voto"
        verbose_name_plural = "Voti"
        unique_together = ("user", "post")
        indexes = [models.Index(fields=["post", "vote_type"])]

    def __str__(self):
        return f"{self.user.username} voted {self.vote_type} on post {self.post.id}"


class Notification(models.Model):
    """Notifiche per attività community (risposte, menzioni, ecc)."""

    NOTIFICATION_TYPES = [
        ("reply", _("Nuova risposta")),
        ("mention", _("Menzione")),
        ("like", _("Mi piace")),
        ("solution", _("Soluzione accettata")),
        ("badge", _("Badge ottenuto")),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="community_notifications",
        verbose_name=_("Destinatario"),
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        verbose_name=_("Mittente"),
        null=True,
        blank=True,
    )
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        verbose_name=_("Discussione"),
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Post"),
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, verbose_name=_("Tipo")
    )
    message = models.TextField(verbose_name=_("Messaggio"))
    is_read = models.BooleanField(default=False, verbose_name=_("Letta"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creata il"))

    class Meta:
        verbose_name = "Notifica"
        verbose_name_plural = "Notifiche"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"Notifica per {self.recipient.username}: {self.notification_type}"


class UserReputation(models.Model):
    """Reputazione utente basata su attività community."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="reputation",
        primary_key=True,
        verbose_name=_("Utente"),
    )

    # Punti totali
    points = models.IntegerField(default=0, verbose_name=_("Punti"))

    # Livello calcolato automaticamente
    level = models.IntegerField(default=1, verbose_name=_("Livello"))

    # Statistiche per calcolare la reputazione
    discussions_created = models.PositiveIntegerField(
        default=0, verbose_name=_("Discussioni create")
    )
    posts_created = models.PositiveIntegerField(
        default=0, verbose_name=_("Post creati")
    )
    solutions_provided = models.PositiveIntegerField(
        default=0, verbose_name=_("Soluzioni provide")
    )
    helpful_votes_received = models.PositiveIntegerField(
        default=0, verbose_name=_("Voti utili ricevuti")
    )
    likes_received = models.PositiveIntegerField(
        default=0, verbose_name=_("Mi piace ricevuti")
    )

    # Bonus/malus
    moderation_strikes = models.PositiveIntegerField(
        default=0, verbose_name=_("Strike moderazione")
    )

    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("Ultimo aggiornamento"))

    def __str__(self):
        return f"{self.user.username} - Livello {self.level} ({self.points} pt)"

    def calculate_level(self):
        """Calcola il livello basato sui punti (formula: sqrt(points / 100))."""
        import math

        return max(1, int(math.sqrt(self.points / 100)) + 1)

    def update_reputation(self):
        """Aggiorna自动amente punti e livello."""
        self.level = self.calculate_level()
        self.save(update_fields=["level", "last_updated"])

    class Meta:
        verbose_name = "Reputazione Utente"
        verbose_name_plural = "Reputazioni Utenti"
        ordering = ["-points"]


class Badge(models.Model):
    """Badge/achievement per utenti della community."""

    BADGE_TYPES = [
        ("bronze", _("Bronzo")),
        ("silver", _("Argento")),
        ("gold", _("Oro")),
        ("platinum", _("Platino")),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(verbose_name=_("Descrizione"))
    badge_type = models.CharField(
        max_length=10, choices=BADGE_TYPES, verbose_name=_("Tipo")
    )
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icona"))
    requirement_type = models.CharField(
        max_length=50, verbose_name=_("Tipo requisito")
    )
    requirement_value = models.IntegerField(verbose_name=_("Valore requisito"))
    is_active = models.BooleanField(default=True, verbose_name=_("Attivo"))
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badge"
        ordering = ["badge_type", "name"]


class UserBadge(models.Model):
    """Badge assegnati agli utenti."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="badges",
        verbose_name=_("Utente"),
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="earned_by",
        verbose_name=_("Badge"),
    )
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Guadagnato il"))

    class Meta:
        verbose_name = "Badge Utente"
        verbose_name_plural = "Badge Utenti"
        unique_together = ("user", "badge")
        ordering = ["-earned_at"]

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
