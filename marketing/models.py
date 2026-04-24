from django.db import models
import uuid


class NewsletterSubscriber(models.Model):
    """Stores email addresses for the newsletter."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribe_token = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )
    welcome_sent = models.BooleanField(default=False)
    followup_step = models.IntegerField(default=0, help_text="Current step in the onboarding sequence (1-3)")
    last_email_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Iscritto Newsletter"
        verbose_name_plural = "Iscritti Newsletter"
        ordering = ["-subscribed_at"]
