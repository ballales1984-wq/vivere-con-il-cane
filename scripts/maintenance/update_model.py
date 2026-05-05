with open('dog_profile/models.py') as f:
    content = f.read()

old = '''    notes = models.TextField(blank=True, help_text="Note aggiuntive")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Evento Medico"
        verbose_name_plural = "Eventi Medici"

    def __str__(self):
        return f"{self.get_event_type_display()} – {self.dog.dog_name} ({self.date})"


class VeterinaryMedia(models.Model):'''

new = '''    notes = models.TextField(blank=True, help_text="Note aggiuntive")
    registered_at = models.DateTimeField(default=timezone.now, help_text="Quando l'evento è stato registrato")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-registered_at"]
        verbose_name = "Evento Medico"
        verbose_name_plural = "Eventi Medici"

    def __str__(self):
        return f"{self.get_event_type_display()} – {self.dog.dog_name} ({self.date})"


class VeterinaryMedia(models.Model):'''

new_content = content.replace(old, new)
with open('dog_profile/models.py', 'w') as f:
    f.write(new_content)
print('Done!')
