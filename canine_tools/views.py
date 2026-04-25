from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.utils import timezone
from django.urls import reverse
from .models import HeartSoundRecording
from dog_profile.models import DogProfile
import json
import math
import tempfile
import os


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def food_calculator(request):
    result = None
    if request.method == "POST":
        try:
            weight = float(request.POST.get("weight", 0))
            age = request.POST.get("age", "adult")
            activity = request.POST.get("activity", "normal")

            base_daily = weight * 30 + 70

            if age == "puppy":
                base_daily *= 2
            elif age == "senior":
                base_daily *= 0.8

            if activity == "high":
                base_daily *= 1.3
            elif activity == "low":
                base_daily *= 0.8

            result = {
                "grams": int(base_daily),
                "cups": round(base_daily / 350, 1),
                "weight": weight,
                "age": age,
                "activity": activity,
            }
        except (ValueError, TypeError):
            pass

    return render(request, "canine_tools/food_calculator.html", {"result": result})


def age_calculator(request):
    result = None
    if request.method == "POST":
        try:
            dog_age = float(request.POST.get("dog_age", 0))
            size = request.POST.get("size", "medium")

            if size == "small":
                if dog_age <= 1:
                    human_age = 15
                elif dog_age == 2:
                    human_age = 24
                else:
                    human_age = 24 + (dog_age - 2) * 10
            elif size == "large":
                if dog_age <= 1:
                    human_age = 15
                elif dog_age == 2:
                    human_age = 24
                else:
                    human_age = 24 + (dog_age - 2) * 7
            else:
                if dog_age <= 1:
                    human_age = 15
                elif dog_age == 2:
                    human_age = 24
                else:
                    human_age = 24 + (dog_age - 2) * 9

            if dog_age < 0.5:
                life_stage = "Cucciolo"
                advice = "Il cucciolo ha bisogno di socializzazione, vaccinazioni e tanto gioco!"
            elif dog_age < 7:
                life_stage = "Adulto"
                advice = "Il tuo cane è in forma! Mantienilo attivo con passeggiate e stimolazione mentale."
            else:
                life_stage = "Anziano"
                advice = "Il cane anziano ha bisogno di più riposo e controlli veterinari regolari."

            result = {
                "dog_age": dog_age,
                "human_age": int(human_age),
                "size": size,
                "life_stage": life_stage,
                "advice": advice,
            }
        except (ValueError, TypeError):
            pass

    return render(request, "canine_tools/age_calculator.html", {"result": result})


def dog_quiz(request):
    score = 0
    result = None
    answers = {}

    if request.method == "POST":
        q1 = request.POST.get("q1", "")
        q2 = request.POST.get("q2", "")
        q3 = request.POST.get("q3", "")

        answers = {"q1": q1, "q2": q2, "q3": q3}

        if q1 == "a":
            score += 1
        if q2 == "c":
            score += 1
        if q3 == "b":
            score += 1

        if score == 3:
            result = "Esperto! Conosci bene il linguaggio dei cani!"
        elif score == 2:
            result = "Buono! Hai buone basi, ma c'è ancora da imparare."
        else:
            result = "Principiante! Leggi i nostri articoli per saperne di più."

    return render(
        request, "canine_tools/quiz.html", {"result": result, "answers": answers}
    )


def tools_index(request):
    from django.utils.translation import gettext as _

    tools = [
        {
            "name": _("Calcolatore Cibo"),
            "url": "canine_tools:food_calculator",
            "icon": "🍖",
            "desc": _("Calcola le porzioni giornaliere"),
        },
        {
            "name": _("Età Umana"),
            "url": "canine_tools:age_calculator",
            "icon": "🎂",
            "desc": _("Conosci l'età del cane in anni umani"),
        },
        {
            "name": _("Quiz Linguaggio"),
            "url": "canine_tools:dog_quiz",
            "icon": "🧠",
            "desc": _("Testa la tua conoscenza"),
        },
        {
            "name": _("Registratore Cardiaco"),
            "url": "canine_tools:heart_recorder",
            "icon": "❤️",
            "desc": _("Registra e analizza i battiti del cuore"),
        },
    ]
    return render(request, "canine_tools/index.html", {"tools": tools})


def privacy_policy(request):
    return render(request, "canine_tools/privacy_policy.html")


def terms_of_service(request):
    return render(request, "canine_tools/terms_of_service.html")


def cookie_policy(request):
    return render(request, "canine_tools/cookie_policy.html")


def heart_recorder(request):
    """Pagina principale per registrare i battiti cardiaci."""
    dogs = []
    recordings = []
    if request.user.is_authenticated:
        dogs = DogProfile.objects.filter(owner=request.user)
        recordings = HeartSoundRecording.objects.filter(owner=request.user).order_by("-created_at")[:10]
    return render(request, "canine_tools/heart_recorder.html", {"dogs": dogs, "recordings": recordings})


@login_required
def heart_recording_detail(request, recording_id):
    """Dettaglio di una registrazione cardiaca."""
    recording = get_object_or_404(HeartSoundRecording, id=recording_id, owner=request.user)
    return render(request, "canine_tools/heart_recording_detail.html", {"recording": recording})


@login_required
@csrf_exempt
def heart_analyze(request):
    """
    Analizza un file audio e restituisce BPM, picchi, waveform.
    Accetta POST con file audio (WebM/OGG/WAV).
    """
    if request.method != "POST" or not request.FILES.get("audio"):
        return JsonResponse({"error": "POST with audio file required"}, status=400)

    audio_file = request.FILES["audio"]
    dog_id = request.POST.get("dog_id")
    notes = request.POST.get("notes", "")

    # Salva temporaneamente il file
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import tempfile
    import os

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, "recording.webm")
    
    with open(temp_path, "wb") as f:
        for chunk in audio_file.chunks():
            f.write(chunk)

    # Analisi audio
    try:
        analysis = analyze_heart_sound(temp_path)
        
        # Sposta file in permanente
        from django.utils import timezone
        filename = f"{request.user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.webm"
        permanent_path = os.path.join("heart_recordings", filename)
        saved_path = default_storage.save(permanent_path, ContentFile(open(temp_path, "rb").read()))
        
        # Crea record
        dog = None
        if dog_id:
            try:
                dog = DogProfile.objects.get(id=dog_id, owner=request.user)
            except DogProfile.DoesNotExist:
                pass

        recording = HeartSoundRecording.objects.create(
            owner=request.user,
            dog=dog,
            audio_file=saved_path,
            duration_seconds=analysis["duration"],
            estimated_bpm=analysis["bpm"],
            beat_count=analysis["beat_count"],
            confidence_score=analysis["confidence"],
            peak_times=analysis["peak_times"],
            amplitudes=analysis["amplitudes"],
            sample_rate=analysis["sample_rate"],
            notes=notes,
        )

        # Cleanup temp
        os.unlink(temp_path)
        os.rmdir(temp_dir)

        return JsonResponse({
            "success": True,
            "recording_id": recording.id,
            "bpm": analysis["bpm"],
            "beat_count": analysis["beat_count"],
            "confidence": analysis["confidence"],
            "duration": analysis["duration"],
            "peak_times": analysis["peak_times"],
            "amplitudes": analysis["amplitudes"],
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def analyze_heart_sound(filepath):
    """
    Analisi semplice di battiti cardiaci da file audio.
    Cerca picchi di ampiezza nel segnale.
    """
    try:
        # Prova a usare librosa se disponibile
        import librosa
        import numpy as np
        
        y, sr = librosa.load(filepath, sr=None, mono=True)
        duration = len(y) / sr
        
        # Normalizza
        y_norm = y / np.max(np.abs(y))
        
        # Trovare picchi: threshold su ampiezza assoluta
        threshold = 0.3  # Regolare in base al segnale
        peaks = []
        amplitudes = []
        for i in range(1, len(y_norm)-1):
            if y_norm[i] > threshold and y_norm[i] > y_norm[i-1] and y_norm[i] > y_norm[i+1]:
                peaks.append(i / sr)  # tempo in secondi
                amplitudes.append(float(y_norm[i]))
        
        if len(peaks) < 2:
            # Se non trova picchi, abbassa threshold
            threshold = 0.15
            peaks = []
            amplitudes = []
            for i in range(1, len(y_norm)-1):
                if y_norm[i] > threshold and y_norm[i] > y_norm[i-1] and y_norm[i] > y_norm[i+1]:
                    peaks.append(i / sr)
                    amplitudes.append(float(y_norm[i]))
        
        if len(peaks) < 2:
            # Ultimo tentativo con 0.1
            threshold = 0.1
            peaks = []
            amplitudes = []
            for i in range(1, len(y_norm)-1):
                if y_norm[i] > threshold and y_norm[i] > y_norm[i-1] and y_norm[i] > y_norm[i+1]:
                    peaks.append(i / sr)
                    amplitudes.append(float(y_norm[i]))
        
        beat_count = len(peaks)
        if beat_count >= 2:
            intervals = np.diff(peaks)
            avg_interval = np.mean(intervals)
            bpm = int(60 / avg_interval) if avg_interval > 0 else 0
            confidence = 0.8 if beat_count > 5 else 0.6
        else:
            bpm = 0
            confidence = 0.0
        
        return {
            "duration": round(duration, 2),
            "bpm": bpm,
            "beat_count": beat_count,
            "confidence": confidence,
            "peak_times": peaks,
            "amplitudes": amplitudes,
            "sample_rate": sr,
        }
        
    except ImportError:
        # Fallback: analisi molto semplice senza librosa
        import wave
        import struct
        
        with wave.open(filepath, 'rb') as wav:
            sr = wav.getframerate()
            n_frames = wav.getnframes()
            data = wav.readframes(n_frames)
            # Converti a array (mono)
            fmt = f"{n_frames}h"
            try:
                samples = list(struct.unpack(fmt, data))
            except:
                samples = [0] * n_frames
            
            duration = n_frames / sr
            # Semplice threshold
            threshold = 10000
            peaks = []
            for i in range(1, len(samples)-1):
                if abs(samples[i]) > threshold and abs(samples[i]) > abs(samples[i-1]) and abs(samples[i]) > abs(samples[i+1]):
                    peaks.append(i / sr)
            
            beat_count = len(peaks)
            if beat_count >= 2:
                intervals = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]
                avg_interval = sum(intervals)/len(intervals)
                bpm = int(60 / avg_interval)
            else:
                bpm = 0
            
            return {
                "duration": round(duration, 2),
                "bpm": bpm,
                "beat_count": beat_count,
                "confidence": 0.5 if beat_count > 2 else 0.0,
                "peak_times": peaks,
                "amplitudes": [1.0] * len(peaks),
                "sample_rate": sr,
            }
