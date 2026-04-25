from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from dog_profile.models import DogProfile, HealthLog, MedicalEvent
from knowledge.models import BreedInsight
import random
from datetime import date, timedelta
from decimal import Decimal

COMMON_MEDICATIONS = [
    {"name": "Antibiotico", "dosage": "500mg", "frequency": "2 volte/giorno"},
    {"name": "Antinfiammatorio", "dosage": "10mg", "frequency": "1 volta/giorno"},
    {"name": "Antiparassitario", "dosage": "pipetta spot-on", "frequency": "1 volta/mese"},
    {"name": "Probiotico", "dosage": "compresse", "frequency": "1 volta/giorno"},
]

DOG_NAMES = [
    "Bella", "Max", "Charlie", "Lucy", "Cooper", "Daisy", "Rocky", "Luna",
    "Bailey", "Molly", "Duke", "Sadie", "Tucker", "Maggie", "Bear",
    "Sophie", "Oliver", "Rosie", "Murphy", "Abby", "Winston", "Penny",
    "Zeus", "Stella", "Gunnar", "Willow", "Jasper", "Cleo", "Kai", "Lily",
    "Leo", "Nala", "Oscar", "Zoe", "Henry", "Ruby", "Finn", "Piper",
    "Toby", "Mia", "Jax", "Roxy", "Sam", "Coco", "Bandit", "Peanut", "Milo", "Buster"
]

DOG_FOODS = [
    "Royal Canin Medium Adult", "Hill's Science Plan Adult",
    "Pro Plan Medium Adult", "Monge Grain Free",
    "Acana Original", "Orijen Six Fish",
    "BARF Dieta Cruda", "Casalingo con verdure"
]

BREED_WEIGHT_RANGES = {
    "Labrador": {"male": (29, 36), "female": (25, 32)},
    "Golden Retriever": {"male": (30, 34), "female": (25, 29)},
    "Pastore Tedesco": {"male": (30, 40), "female": (22, 32)},
    "Chihuahua": {"male": (1.5, 3), "female": (1.5, 2.5)},
    "Bulldog Francese": {"male": (9, 14), "female": (8, 12)},
    "Border Collie": {"male": (14, 20), "female": (12, 19)},
    "Beagle": {"male": (10, 11), "female": (9, 10)},
    "Cocker Spaniel": {"male": (12, 15), "female": (11, 14)},
    "Jack Russell Terrier": {"male": (5, 7), "female": (5, 6)},
    "Meticcio": {"male": (10, 25), "female": (8, 22)},
}

ACTIVITY_LEVELS = ["low", "moderate", "high", "very_high"]
SLEEP_PATTERNS = ["normal", "excessive", "restless", "variable"]
SOCIALIZATION = ["friendly", "selective", "protective", "shy", "reactive"]
DIET_TYPES = ["dry", "wet", "mixed", "raw", "homemade"]

def generate_weight(breed, gender):
    ranges = BREED_WEIGHT_RANGES.get(breed, BREED_WEIGHT_RANGES["Meticcio"])
    rg = ranges.get(gender, ranges.get("male"))
    w = random.uniform(float(rg[0]), float(rg[1]))
    if gender == "female":
        w *= 0.88
    return Decimal(str(round(max(1.0, w), 1)))

def generate_grams(weight, activity):
    base = 30
    fac = {"low": 0.7, "moderate": 1.0, "high": 1.4, "very_high": 1.8}.get(activity, 1.0)
    return int(float(weight) * base * fac)

def generate_walk_minutes(activity, age_years):
    base = {"low": 20, "moderate": 45, "high": 90, "very_high": 120}.get(activity, 45)
    if age_years >= 8:
        base = int(base * 0.6)
    elif age_years < 2:
        base = int(base * 0.7)
    return max(10, base + random.randint(-20, 30))

def generate_sleep(activity):
    s = {"low": 14, "moderate": 12, "high": 10, "very_high": 9}.get(activity, 12)
    return round(s + random.uniform(-1.5, 1.5), 1)

class Command(BaseCommand):
    help = "Genera dati realistici per cani"

    def add_arguments(self, parser):
        parser.add_argument("--num-dogs", type=int, default=100)
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--events", type=int, default=3)

    def handle(self, *args, **options):
        num_dogs = options["num_dogs"]
        num_days = options["days"]
        avg_events = options["events"]

        owner, created = User.objects.get_or_create(
            username="test_user_dog_data",
            defaults={"email": "test.dog.data@example.com", "first_name": "Test", "last_name": "User"}
        )
        if created:
            owner.set_password("test123456")
            owner.save()
            self.stdout.write(self.style.WARNING("Creato utente test (password: test123456)"))

        all_breeds = list(BREED_WEIGHT_RANGES.keys())
        breed_insights = list(BreedInsight.objects.all())
        if breed_insights:
            available_breeds = [bi.breed for bi in breed_insights]
        else:
            available_breeds = all_breeds

        created_dogs = 0
        updated_dogs = 0
        total_events = 0
        total_logs = 0

        self.stdout.write(self.style.SUCCESS(
            f"=== Generazione {num_dogs} cani realistici ==="
            f"\nGiorni log: {num_days} | Eventi medi: {avg_events}"
            f"\nRazze: {', '.join(available_breeds[:5])}..."
            f"\n==========================================\n"
        ))

        for i in range(num_dogs):
            breed = available_breeds[i % len(available_breeds)]
            gender = random.choice(["male", "female"])
            age_years = random.choices(range(1, 13), weights=[15, 20, 20, 15, 10, 8, 5, 3, 2, 1, 1, 0.5])[0]
            birth_date = date.today() - timedelta(days=age_years * 365 + random.randint(-90, 90))
            weight = generate_weight(breed, gender)
            activity = random.choices(ACTIVITY_LEVELS, weights=[10, 45, 30, 15])[0]
            if age_years >= 8:
                activity = random.choices(ACTIVITY_LEVELS, weights=[35, 40, 20, 5])[0]
            walk_min = generate_walk_minutes(activity, age_years)
            diet = random.choice(DIET_TYPES)
            grams = generate_grams(weight, activity)

            profile, created = DogProfile.objects.update_or_create(
                owner=owner,
                dog_name=random.choice(DOG_NAMES),
                birth_date=birth_date,
                defaults={
                    "name": f"{owner.first_name} {owner.last_name[:1]}.",
                    "breed": breed,
                    "weight": weight,
                    "gender": gender,
                    "is_neutered": random.random() < 0.6 if age_years >= 1 else False,
                    "microchip": f"MC{random.randint(100000, 999999)}" if random.random() < 0.5 else "",
                    "food_type": random.choice(DOG_FOODS),
                    "food_grams_per_day": grams,
                    "meals_per_day": 2 if age_years >= 1 else 3,
                    "diet_type": diet,
                    "activity_level": activity,
                    "typical_walk_minutes": walk_min,
                    "sleep_pattern": random.choice(SLEEP_PATTERNS),
                    "is_indoor": random.random() < 0.85,
                    "has_access_garden": random.random() < 0.4,
                    "socialization_level": random.choice(SOCIALIZATION),
                    "notes": f"Generato per test - {age_years} anni"
                }
            )
            if created:
                created_dogs += 1
            else:
                updated_dogs += 1

            # Eventi medici con timestamp di registrazione automatica
            n_events = random.randint(0, avg_events * 2)
            for _ in range(n_events):
                months_ago = random.randint(1, max(1, age_years * 12))
                ed = date.today() - timedelta(days=months_ago * 30)
                et = random.choice(["visit", "vaccine", "exam", "followup", "therapy_start"])
                costs = {"vaccine": 60, "visit": 90, "exam": 150, "followup": 50, "therapy_start": 200}
                MedicalEvent.objects.create(
                    dog=profile, event_type=et, date=ed,
                    title=random.choice(["Visita controllo", "Esami sangue", "Vaccino", "Controllo follow-up"]),
                    description="Esame clinico completo.",
                    vet_clinic=random.choice(["Clinica Vet Centrale", "Studio Vet", "Ambulatorio"]),
                    vet_name=random.choice(["Dr. Rossi", "Dr. Bianchi", "Dr. Verdi"]),
                    diagnosis="Valutazione clinica.",
                    prescribed_medications=COMMON_MEDICATIONS[:random.randint(0, 2)],
                    treatment_description="Terapia indicata.",
                    outcome="In corso" if et == "therapy_start" else "Soddisfacente",
                    cost=Decimal(str(costs.get(et, 80))),
                    notes="Nessuna complicazione.",
                    registered_at=timezone.now() - timedelta(days=random.randint(0, months_ago*30))
                )
                total_events += 1

            # Log sanitari con timestamp di registrazione automatica
            if not HealthLog.objects.filter(dog=profile).exists():
                logs = []
                for d in range(num_days):
                    ld = date.today() - timedelta(days=d)
                    age_days = (ld - birth_date).days
                    age_y = age_days / 365.25
                    sm = 1.3 if age_y < 1 else (0.8 if age_y > 10 else 1.0)
                    pm = 0.8 if age_y < 1 else (0.6 if age_y > 10 else 1.0)
                    logs.append(HealthLog(
                        dog=profile, date=ld, log_type="routine", severity="1",
                        sleep_hours=round(generate_sleep(activity) * sm * random.uniform(0.8, 1.2), 1),
                        play_minutes=int(generate_walk_minutes(activity, age_y) * 0.4 * pm * random.uniform(0.7, 1.3)),
                        walk_minutes=int(walk_min * random.uniform(0.6, 1.3)),
                        food_grams=grams,
                        description="Routine giornaliera normale.",
                        ai_tags=["routine"],
                        ai_summary_suggestion="Parametri nella norma.",
                        registered_at=timezone.now() - timedelta(days=d, hours=random.randint(0, 23))
                    ))
                HealthLog.objects.bulk_create(logs)
                total_logs += len(logs)

            if (i + 1) % 20 == 0:
                self.stdout.write(f"  Generati {i + 1}/{num_dogs}...")

        self.stdout.write(self.style.SUCCESS(
            f"\n=== Completato ==="
            f"\nNuovi profili: {created_dogs}"
            f"\nAggiornati: {updated_dogs}"
            f"\nEventi medici: {total_events}"
            f"\nLog sanitari: {total_logs}"
            f"\nTotali in DB: {DogProfile.objects.count()} cani"
            f"\n==================\n"
        ))
