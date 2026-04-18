from django.db import models

class NewsletterSubscriber(models.Model):
    """Stores email addresses for the newsletter."""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Iscritto Newsletter"
        verbose_name_plural = "Iscritti Newsletter"
        ordering = ["-subscribed_at"]
