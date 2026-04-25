from django.db import models
from django.contrib.auth.models import User
from dog_profile.models import DogProfile


class HeartSoundRecording(models.Model):
    """Registrazione audio dei battiti cardiaci del cane con analisi."""
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="heart_recordings", null=True, blank=True
    )
    dog = models.ForeignKey(
        DogProfile, on_delete=models.CASCADE, related_name="heart_recordings", null=True, blank=True
    )
    
    # File audio registrato
    audio_file = models.FileField(upload_to="heart_recordings/%Y/%m/")
    
    # Risultati analisi
    duration_seconds = models.FloatField(help_text="Durata registrazione in secondi")
    estimated_bpm = models.IntegerField(help_text="Battiti per minuto stimati")
    beat_count = models.IntegerField(help_text="Numero totale battiti rilevati")
    confidence_score = models.FloatField(help_text="Confidenza dell'analisi (0-1)")
    
    # Dati aggregati per grafico
    peak_times = models.JSONField(help_text="Lista timestamp (secondi) dei picchi cardiaci")
    amplitudes = models.JSONField(help_text="Lista ampiezze normalizzate dei picchi")
    sample_rate = models.IntegerField(default=44100, help_text="Sample rate audio")
    
    # Note utente
    notes = models.TextField(blank=True, help_text="Note: a riposo, dopo attività, ecc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        dog_name = self.dog.dog_name if self.dog else "Senza cane"
        return f"Battiti {dog_name} - {self.estimated_bpm} BPM ({self.created_at.date()})"
