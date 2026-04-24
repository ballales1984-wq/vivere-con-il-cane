from django.db import models
from django.db.models import Avg, Sum, Count
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import date  # per proprietà DogProfile.get_age


class DogProfile(models.Model):
    """Complete digital twin of a dog — identity + medical + behavioral + lifestyle context."""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profiles", null=True, blank=True
    )

    # ── 1. IDENTITÀ BASE ──
    name = models.CharField(max_length=100)  # owner name
    dog_name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[("male", _("Maschio")), ("female", _("Femmina"))],
        blank=True,
    )
    is_neutered = models.BooleanField(default=False)
    microchip = models.CharField(
        max_length=50, blank=True, help_text="Microchip number se presente"
    )

    # ── 2. ALIMENTAZIONE STRUTTURATA ──
    food_type = models.CharField(
        max_length=200, blank=True, help_text="Es: Croccantino Royal Canin Medium Adult"
    )
    food_grams_per_day = models.IntegerField(
        null=True, blank=True, help_text="Grammi totali giornalieri"
    )
    meals_per_day = models.IntegerField(default=2, help_text="Numero pasti giornalieri")
    supplements = models.TextField(
        blank=True, help_text="Integratori: nome + dosaggio (es: Glucosamina 500mg ×2)"
    )
    diet_notes = models.TextField(
        blank=True, help_text="Intolleranze, allergie, cibi proibiti"
    )
    RAW_FOOD_CHOICES = [
        ("dry", _("Crocchette")),
        ("wet", _("Umido")),
        ("raw", _("Crudo (BARF)")),
        ("homemade", _("Casalingo")),
        ("mixed", _("Misto")),
    ]
    diet_type = models.CharField(
        max_length=20, choices=RAW_FOOD_CHOICES, default="dry", blank=True
    )

    # ── 3. FARMACI CORRENTI (JSON — lista strutturata) ──
    current_medications = models.JSONField(
        default=list,
        blank=True,
        help_text="""[{
            'name': 'Nome farmaco',
            'dosage': '5mg',
            'frequency': '2 volte/giorno',
            'start_date': '2024-01-15',
            'end_date': null,
            'reason': 'Motivo prescrizione',
            'vet_prescribed': true
        }]""",
    )

    # ── 4. ABITUDINI / ROUTINE ──
    ACTIVITY_CHOICES = [
        ("low", _("Basso – poco movimento")),
        ("moderate", _("Moderato – passeggiate normali")),
        ("high", _("Alto – molto attivo")),
        ("very_high", _("Molto alto – sportivo")),
    ]
    activity_level = models.CharField(
        max_length=20, choices=ACTIVITY_CHOICES, default="moderate"
    )
    typical_walk_minutes = models.IntegerField(
        null=True, blank=True, help_text="Minuti medi di passeggiata/giorno"
    )
    SLEEP_CHOICES = [
        ("normal", _("Normale")),
        ("excessive", _("Eccessivo")),
        ("restless", _("Agitato/insonne")),
        ("variable", _("Variabile")),
    ]
    sleep_pattern = models.CharField(
        max_length=20, choices=SLEEP_CHOICES, default="normal"
    )

    # ── 5. AMBIENTE & SOCIALIZZAZIONE ──
    is_indoor = models.BooleanField(
        default=True, help_text="Vive prevalentemente in casa?"
    )
    has_access_garden = models.BooleanField(default=False)
    socialization_level = models.CharField(
        max_length=30,
        choices=[
            ("friendly", _("Amichevole con tutti")),
            ("selective", _("Selettivo con alcuni")),
            ("protective", _("Protettivo/da guardia")),
            ("shy", _("Timido/riservato")),
            ("reactive", _("Reattivo/aggressivo")),
        ],
        default="friendly",
    )

    # ── 6. STORICO PESO (semplificato – per future analisi trend) ──
    weight_history = models.JSONField(
        default=list,
        blank=True,
        help_text="""[{'date': '2024-01', 'weight': 28.5}, …]""",
    )

    # ── NOTE LIBERE (ultimo campo, Retrocompatibilità) ──
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.dog_name} ({self.name})"

    def get_age(self):
        if not self.birth_date:
            return "?"
        from datetime import date

        today = date.today()
        age = today.year - self.birth_date.year
        if today.month < self.birth_date.month or (
            today.month == self.birth_date.month and today.day < self.birth_date.day
        ):
            age -= 1
        return str(age)

    @property
    def events_count(self):
        # If annotated via QuerySet.annotate(), use that value; otherwise compute.
        if hasattr(self, "_events_count"):
            return self._events_count
        return self.medical_events.count()

    @events_count.setter
    def events_count(self, value):
        self._events_count = value

    # ── PROPERTIES DI UTILITÀ ──
    @property
    def current_medications_structured(self):
        """Restituisce lista di dict con info essenziali dei farmaci attuali."""
        simplified = []
        for m in self.current_medications:
            simplified.append(
                {
                    "name": m.get("name", ""),
                    "dosage": m.get("dosage", ""),
                    "frequency": m.get("frequency", ""),
                    "start": m.get("start_date", ""),
                    "reason": m.get("reason", ""),
                }
            )
        return simplified

    @property
    def nutrition_summary(self):
        """Riassunto alimentare in una stringa."""
        parts = []
        if self.food_type:
            parts.append(f"{self.food_type}")
        if self.food_grams_per_day:
            parts.append(f"{self.food_grams_per_day}g/giorno")
        if self.meals_per_day:
            parts.append(f"{self.meals_per_day} pasti/giorno")
        if self.supplements:
            parts.append(f"Integratori: {self.supplements}")
        return " • ".join(parts) if parts else "Non specificato"

    def get_lifetime_stats(self):
        """Calcola aggregazioni e medie di tutta la vita del cane (per IA)."""
        routine_logs = self.health_logs.filter(log_type="routine")
        
        # Averages
        avgs = routine_logs.aggregate(
            avg_sleep=Avg('sleep_hours'),
            avg_walk=Avg('walk_minutes'),
            avg_play=Avg('play_minutes'),
            avg_food=Avg('food_grams')
        )
        
        # Totals
        total_days_logged = routine_logs.count()
        total_medical_events = self.medical_events.count()
        
        # Behavioral problems
        # We need to count unique problem types analyzed
        analyses = self.analyses.all() if hasattr(self, 'analyses') else []
        problem_counts = {}
        for a in analyses:
            if a.problem:
                problem_counts[a.problem.title] = problem_counts.get(a.problem.title, 0) + 1
                
        return {
            "total_days_tracked": total_days_logged,
            "averages": {
                "sleep_hours": round(avgs['avg_sleep'] or 0, 1),
                "walk_minutes": int(avgs['avg_walk'] or 0),
                "play_minutes": int(avgs['avg_play'] or 0),
                "food_grams": int(avgs['avg_food'] or 0)
            },
            "total_medical_events": total_medical_events,
            "behavioral_issues_analyzed": problem_counts
        }

    class Meta:
        verbose_name = "Profilo Cane"
        verbose_name_plural = "Profili Cani"


class MedicalEvent(models.Model):
    """Evento medico VERO: visite, esami, diagnosi, terapie, interventi."""

    EVENT_CATEGORIES = [
        ("visit", _("Visita Veterinaria")),
        ("exam", _("Esame Diagnostico")),
        ("vaccine", _("Vaccinazione")),
        ("surgery", _("Intervento Chirurgico")),
        ("therapy_start", _("Inizio Terapia")),
        ("therapy_end", _("Fine Terapia")),
        ("emergency", _("Pronto Soccorso")),
        ("followup", _("Controllo")),
        ("other", _("Altro")),
    ]

    dog = models.ForeignKey(
        DogProfile, on_delete=models.CASCADE, related_name="medical_events"
    )
    event_type = models.CharField(max_length=30, choices=EVENT_CATEGORIES)
    date = models.DateField()
    title = models.CharField(
        max_length=200, blank=True, help_text="Titolo breve: es. 'Vaccino annuale'"
    )
    description = models.TextField(
        blank=True, help_text="Descrizione libera (compatibilità)"
    )  # retro
    vet_clinic = models.CharField(max_length=200, blank=True)
    vet_name = models.CharField(max_length=200, blank=True)

    # CONTENUTO STRUTTURATO
    diagnosis = models.TextField(blank=True, help_text="Diagnosi del veterinario")
    prescribed_medications = models.JSONField(
        default=list,
        blank=True,
        help_text="Farmaci prescritti: [{name, dosage, duration, notes}]",
    )
    prescribed_tests = models.TextField(blank=True, help_text="Esami prescritti")
    treatment_description = models.TextField(blank=True, help_text="Terapia applicata")
    outcome = models.TextField(blank=True, help_text="Risultato finale")
    next_event_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    notes = models.TextField(blank=True, help_text="Note aggiuntive")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Evento Medico"
        verbose_name_plural = "Eventi Medici"

    def __str__(self):
        return f"{self.get_event_type_display()} – {self.dog.dog_name} ({self.date})"


class VeterinaryMedia(models.Model):
    """Media files (photos/videos) attached to veterinary request."""

    MEDIA_TYPES = [
        ("photo", _("Foto")),
        ("video", _("Video")),
    ]

    request = models.ForeignKey(
        "VeterinaryRequest", on_delete=models.CASCADE, related_name="media_files"
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to="veterinary_requests/%Y/%m/")
    caption = models.CharField(max_length=200, blank=True)
    upload_order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_media_type_display()}: {self.caption or self.file.name}"


class VeterinaryRequest(models.Model):
    """Structured request sent to veterinarian with AI summary and curated media."""

    REQUEST_STATUS = [
        ("draft", _("Bozza")),
        ("ready", _("Pronto")),
        ("sent", _("Inviato")),
    ]

    dog = models.ForeignKey(
        DogProfile, on_delete=models.CASCADE, related_name="vet_requests"
    )
    analysis = models.ForeignKey(
        "knowledge.DogAnalysis",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vet_requests",
    )
    problem_description = models.TextField(help_text="Descrizione del problema")
    ai_summary = models.TextField(blank=True, help_text="Riassunto AI generato")
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default="draft")
    vet_name = models.CharField(max_length=200, blank=True)
    vet_email = models.EmailField(blank=True)
    vet_phone = models.CharField(max_length=50, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Richiesta vet per {self.dog.dog_name} - {self.created_at.date()}"


class HealthLog(models.Model):
    """Log giornaliero/sintomo/comportamento — la TIMELINE CONTINUA del cane."""

    LOG_TYPES = [
        ("routine", _("Routine Giornaliera")),
        ("symptom", _("Sintomo Osservato")),
        ("behavior", _("Comportamento Anomalo")),
        ("diet", _("Variazione Alimentare")),
        ("medication", _("Somministrazione Farmaco")),
        ("vital_signs", _("Segni Vitali (temperatura, frequenza…)")),
        ("note", _("Nota Libera")),
    ]
    SEVERITY_LEVELS = [
        ("1", _("Lieve – monitorare")),
        ("2", _("Moderato – attenzione")),
        ("3", _("Severo – consultare")),
    ]

    dog = models.ForeignKey(
        DogProfile, on_delete=models.CASCADE, related_name="health_logs"
    )
    date = models.DateField()
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, default="routine")
    severity = models.CharField(max_length=1, choices=SEVERITY_LEVELS, default="1")

    # ── DATI STRUTTURATI PER TIPO ──
    duration_hours = models.FloatField(
        null=True, blank=True, help_text="Durata (ore) se sintomo/comportamento"
    )
    frequency = models.IntegerField(
        null=True, blank=True, help_text="Frequenza episodi nella giornata"
    )
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Temperatura °C",
    )
    heart_rate = models.IntegerField(null=True, blank=True, help_text="Battiti/minuto")
    respiratory_rate = models.IntegerField(
        null=True, blank=True, help_text="Respiri/minuto"
    )

    description = models.TextField(help_text="Descrizione dettagliata")

    # ── METRICHE GIORNALIERE (solo per log_type='routine') ──
    sleep_hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Ore sonno (24h)",
    )
    play_minutes = models.IntegerField(
        null=True, blank=True, help_text="Minuti di gioco/attività"
    )
    walk_minutes = models.IntegerField(
        null=True, blank=True, help_text="Minuti passeggiata"
    )
    food_grams = models.IntegerField(
        null=True, blank=True, help_text="Grammi cibo totale"
    )

    # ── COLLEGAMENTI ──
    # Un log può essere collegato a un evento medico (visita) se questo log ha contribuito alla visita
    related_event = models.ForeignKey(
        "MedicalEvent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_logs",
        help_text="Evento medico collegato (se applicabile)",
    )
    media = models.ManyToManyField(
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
        return f"{self.dog.dog_name} • {self.date} • {self.get_log_type_display()}"
