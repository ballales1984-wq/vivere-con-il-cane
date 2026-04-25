with open('dog_profile/models.py') as f:
    content = f.read()

old = '''    media = models.ManyToManyField(
        "VeterinaryMedia",
        blank=True,
        related_name="health_logs",
        help_text="Foto/video associati a questa osservazione",
    )

    # ── AI LAYER ──
    ai_tags = models.JSONField(
        default=list, blank=True, help_text="Tags auto-generati dal sistema AI"
    )
    ai_summary_suggestion = models.TextField(
        blank=True, help_text="Suggerimento AI per pattern recognition"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "Log Sanitario"
        verbose_name_plural = "Log Sanitari"
        indexes = [models.Index(fields=["dog", "date"])]

    def __str__(self):
        return f"{self.dog.dog_name} • {self.date} • {self.get_log_type_display()}"'''

new = '''    media = models.ManyToManyField(
        "VeterinaryMedia",
        blank=True,
        related_name="health_logs",
        help_text="Foto/video associati a questa osservazione",
    )
    registered_at = models.DateTimeField(default=timezone.now, help_text="Quando il log è stato registrato")

    # ── AI LAYER ──
    ai_tags = models.JSONField(
        default=list, blank=True, help_text="Tags auto-generati dal sistema AI"
    )
    ai_summary_suggestion = models.TextField(
        blank=True, help_text="Suggerimento AI per pattern recognition"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-registered_at"]
        verbose_name = "Log Sanitario"
        verbose_name_plural = "Log Sanitari"
        indexes = [models.Index(fields=["dog", "date"])]

    def __str__(self):
        return f"{self.dog.dog_name} • {self.date} • {self.get_log_type_display()}"'''

new_content = content.replace(old, new)
with open('dog_profile/models.py', 'w') as f:
    f.write(new_content)
print('Done!')
