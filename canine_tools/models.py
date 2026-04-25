from django.db import models
from django.contrib.auth.models import User
from dog_profile.models import DogProfile


class HealthConnectToken(models.Model):
    """Token OAuth 2.0 per Google Health/Connect API."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="health_connect_token"
    )
    access_token = models.TextField(help_text="Token di accesso OAuth")
    refresh_token = models.TextField(help_text="Token di refresh (per rinnovo)")
    token_expiry = models.DateTimeField(help_text="Scadenza del token")
    scopes = models.TextField(help_text="Scope autorizzati (JSON list)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Token per {self.user.username} (scade: {self.token_expiry})"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() >= self.token_expiry


class HealthDataPoint(models.Model):
    """Dati sincronizzati da Google Health/Connect associati a un cane."""
    SOURCE_CHOICES = [
        ('steps', 'Passi'),
        ('heart_rate', 'Frequenza Cardiaca'),
        ('distance', 'Distanza'),
        ('calories', 'Calorie'),
        ('weight', 'Peso'),
        ('sleep', 'Sonno'),
    ]

    dog = models.ForeignKey(
        DogProfile, on_delete=models.CASCADE, related_name="health_data_points"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    
    # Dati punto
    start_time = models.DateTimeField(help_text="Inizio misurazione")
    end_time = models.DateTimeField(help_text="Fine misurazione")
    value = models.FloatField(help_text="Valore misurato")
    unit = models.CharField(max_length=20, help_text="Unità di misura (es. 'steps', 'bpm', 'm')")
    
    # Metadati
    data_source_name = models.CharField(max_length=200, blank=True, help_text="Fonte dati Google")
    raw_data = models.JSONField(help_text="JSON completo della risposta API", default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["dog", "source_type", "-start_time"]),
        ]
        unique_together = [("dog", "source_type", "start_time")]

    def __str__(self):
        return f"{self.dog.dog_name} - {self.get_source_type_display()}: {self.value} {self.unit} ({self.start_time.date()})"


class HeartSoundRecording(models.Model):
    """Registrazione audio dei battiti cardiaci del cane con analisi."""
    RECORDING_CONTEXT_CHOICES = [
        ('rest', 'A riposo'),
        ('after_activity', 'Dopo attività'),
        ('before_meal', 'Prima del pasto'),
        ('after_meal', 'Dopo il pasto'),
        ('during_sleep', 'Durante il sonno'),
        ('stress', 'Situazione di stress'),
    ]
    
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="heart_recordings", null=True, blank=True
    )
    dog = models.ForeignKey(
        DogProfile, on_delete=models.CASCADE, related_name="heart_recordings", null=True, blank=True
    )
    
    # File audio registrato
    audio_file = models.FileField(upload_to="heart_recordings/%Y/%m/")
    
    # Contesto della registrazione
    recording_context = models.CharField(
        max_length=20,
        choices=RECORDING_CONTEXT_CHOICES,
        blank=True,
        help_text="Contesto in cui è stata effettuata la registrazione"
    )
    
    # Risultati analisi
    duration_seconds = models.FloatField(help_text="Durata registrazione in secondi")
    estimated_bpm = models.IntegerField(help_text="Battuti per minuto stimati")
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

