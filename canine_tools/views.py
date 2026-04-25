from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from .models import HeartSoundRecording, HealthConnectToken, HealthDataPoint
from dog_profile.models import DogProfile
import json
import math
import tempfile
import os
from datetime import datetime, timedelta, date

# Google OAuth / Health Connect
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


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
        {
            "name": _("Google Health Sync"),
            "url": "canine_tools:health_sync",
            "icon": "💙",
            "desc": _("Sincronizza passi e dati salute da Google"),
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


# Google Health/Fit OAuth
@login_required
def google_fit_auth_start(request):
    """Inizia il flusso OAuth per Google Fit/Health."""
    # Usa gli scope Health API se disponibile, altrimenti Fit
    scopes = getattr(settings, 'GOOGLE_HEALTH_SCOPES', settings.GOOGLE_FIT_SCOPES)
    
    # Costruisci il flusso OAuth
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
            }
        },
        scopes=scopes,
        redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI,
    )
    
    # Aggiungi state per CSRF protection
    from django.core import signing
    state = signing.dumps({'user_id': request.user.id}, salt='google-oauth')
    flow.params['state'] = state
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return redirect(authorization_url)


@login_required
def google_fit_callback(request):
    """Callback OAuth da Google - salva token e inizializza sincronizzazione."""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code:
        return JsonResponse({"error": " Nessun code ricevuto"}, status=400)
    
    # Verifica state
    from django.core import signing
    try:
        data = signing.loads(state, salt='google-oauth', max_age=600)
        if data.get('user_id') != request.user.id:
            return JsonResponse({"error": "User mismatch"}, status=403)
    except signing.BadSignature:
        return JsonResponse({"error": "State invalid"}, status=400)
    
    # Scambia code con token
    scopes = getattr(settings, 'GOOGLE_HEALTH_SCOPES', settings.GOOGLE_FIT_SCOPES)
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
            }
        },
        scopes=scopes,
        redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI,
    )
    
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
    except Exception as e:
        return JsonResponse({"error": f"Token exchange failed: {str(e)}"}, status=400)
    
    # Salva token nelDB
    token, created = HealthConnectToken.objects.update_or_create(
        user=request.user,
        defaults={
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token or '',
            'token_expiry': credentials.expiry,
            'scopes': json.dumps(credentials.scopes),
        }
    )
    
    # Reindirizza alla pagina sync
    return redirect('canine_tools:health_sync')


@login_required
def health_sync(request):
    """Pagina per sincronizzare i dati da Google Health/Fit."""
    token_exists = hasattr(request.user, 'health_connect_token')
    return render(request, "canine_tools/health_sync.html", {
        "token_exists": token_exists,
        "recent_sync": HealthDataPoint.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5] if token_exists else []
    })


@login_required
@csrf_exempt
def sync_health_data(request):
    """
    Endpoint API per sincronizzare i dati da Google Health/Fit.
    Supporta sia Health API che Fitness API (retrocompatibilità).
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST richiesto"}, status=405)
    
    # Verifica token
    try:
        token_obj = HealthConnectToken.objects.get(user=request.user)
    except HealthConnectToken.DoesNotExist:
        return JsonResponse({"error": "Token non trovato. Connettiti prima."}, status=400)
    
    # Costruisci credenziali
    creds = Credentials(
        token=token_obj.access_token,
        refresh_token=token_obj.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=json.loads(token_obj.scopes),
    )
    
    # Refresh token se scaduto
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_obj.access_token = creds.token
        token_obj.token_expiry = creds.expiry
        token_obj.save()
    
    # Scegli API: Health Connect ( nuova) o Fit (legacy)
    use_health_api = True  # Default a Health API
    
    # Prova Health Connect API
    try:
        if use_health_api:
            result = sync_via_health_api(creds, request.user)
        else:
            result = sync_via_fitness_api(creds, request.user)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({
        "success": True,
        "saved_points": result['saved'],
        "skipped": result['skipped'],
        "errors": result['errors'],
    })


def build_time_range(days=7):
    """Costruisce l'intervallo di tempo per l'API (da oggi - 7 giorni a oggi)."""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    # Converti in timestamp nanoseconds
    start_ns = int(start_time.timestamp() * 1e9)
    end_ns = int(end_time.timestamp() * 1e9)
    return start_ns, end_ns


def sync_via_health_api(creds, user):
    """
    Sincronizza usando Google Health Connect API.
    https://developers.google.com/health/reference/rest
    """
    from googleapiclient.discovery import build
    
    # Costruisci servizio Health
    service = build('health', 'v1alpha', credentials=creds, static_discovery=False)
    
    saved_count = 0
    skipped = 0
    errors = []
    
    # Per ogni cane dell'utente, sincronizza gli ultimi 7 giorni
    dogs = DogProfile.objects.filter(owner=user)
    
    for dog in dogs:
        try:
            # Richiesta dati passi (steps)
            start_ns, end_ns = build_time_range(30)  # ultimi 30 giorni
            
            # Esempio: leggere dati passi
            # Health API usa dataset diverso da Fit
            #Endpoint: health.fitness.v1alpha
            # Docs: https://developers.google.com/health/reference/rest/v1alpha/datasets/batchGet
            
            # NOTA: Health API è ancora in anteprima, endpoint potrebbe cambiare
            # Per ora placeholder
            
            # Simuliamo lettura dati per test
            # In produzione: chiama service.users().dataSources().list etc.
            
            saved_count += 0  # Da implementare con API reale
            
        except Exception as e:
            errors.append(f"Cane {dog.dog_name}: {str(e)}")
            skipped += 1
    
    return {"saved": saved_count, "skipped": skipped, "errors": errors}


def sync_via_fitness_api(creds, user):
    """
    Sincronizza usando Google Fit API (legacy, ma ancora funzionante).
    Recupera passi, distanza, calorie, frequenza cardiaca.
    """
    from googleapiclient.discovery import build
    
    service = build('fitness', 'v1', credentials=creds)
    
    saved_count = 0
    skipped = 0
    errors = []
    start_ns, end_ns = build_time_range(30)  # ultimi 30 giorni
    
    dogs = DogProfile.objects.filter(owner=user)
    
    for dog in dogs:
        try:
            # STEP 1: Lista data sources
            ds_response = service.users().dataSources().list(userId='me').execute()
            data_sources = ds_response.get('dataSource', [])
            
            # STEP 2: Aggrega dati per tipo
            # Usiamo aggregate endpoint per ottenere totali giornalieri
            # https://developers.google.com/fit/rest/v1/reference/users/dataset/aggregate
            
            aggregate_body = {
                "aggregateBy": [{
                    "dataTypeName": "com.google.step_count.delta"
                }],
                "bucketByTime": { "durationMillis": 86400000 },  # 1 giorno
                "startTimeMillis": int(start_ns / 1e6),
                "endTimeMillis": int(end_ns / 1e6),
            }
            
            try:
                agg_response = service.users().dataset().aggregate(
                    userId='me',
                    body=aggregate_body
                ).execute()
                
                # Processa bucket
                for bucket in agg_response.get('bucket', []):
                    start_ms = int(bucket.get('startTimeMillis', 0))
                    end_ms = int(bucket.get('endTimeMillis', 0))
                    
                    # Estrai valore passi
                    steps = 0
                    for point in bucket.get('point', []):
                        for value in point.get('value', []):
                            if 'intVal' in value:
                                steps += value['intVal']
                    
                    if steps > 0:
                        start_dt = datetime.utcfromtimestamp(start_ms / 1000)
                        end_dt = datetime.utcfromtimestamp(end_ms / 1000)
                        
                        # Salva o aggiorna
                        HealthDataPoint.objects.update_or_create(
                            dog=dog,
                            user=user,
                            source_type='steps',
                            start_time=start_dt,
                            end_time=end_dt,
                            defaults={
                                'value': float(steps),
                                'unit': 'steps',
                                'data_source_name': 'Google Fit (aggregated)',
                            }
                        )
                        saved_count += 1
            
            except Exception as api_err:
                errors.append(f"Steps API error: {str(api_err)}")
            
            # STEP 3: Heart rate (frequenza cardiaca)
            # Nota: per cani, heart rate è rilevante
            try:
                hr_body = {
                    "aggregateBy": [{
                        "dataTypeName": "com.google.heart_rate.bpm"
                    }],
                    "bucketByTime": { "durationMillis": 86400000 },  
                    "startTimeMillis": int(start_ns / 1e6),
                    "endTimeMillis": int(end_ns / 1e6),
                }
                
                hr_response = service.users().dataset().aggregate(
                    userId='me',
                    body=hr_body
                ).execute()
                
                for bucket in hr_response.get('bucket', []):
                    start_ms = int(bucket.get('startTimeMillis', 0))
                    end_ms = int(bucket.get('endTimeMillis', 0))
                    
                    heart_rates = []
                    for point in bucket.get('point', []):
                        for value in point.get('value', []):
                            if 'fpVal' in value:
                                heart_rates.append(value['fpVal'])
                    
                    if heart_rates:
                        avg_hr = sum(heart_rates) / len(heart_rates)
                        start_dt = datetime.utcfromtimestamp(start_ms / 1000)
                        end_dt = datetime.utcfromtimestamp(end_ms / 1000)
                        
                        HealthDataPoint.objects.update_or_create(
                            dog=dog,
                            user=user,
                            source_type='heart_rate',
                            start_time=start_dt,
                            end_time=end_dt,
                            defaults={
                                'value': avg_hr,
                                'unit': 'bpm',
                                'data_source_name': 'Google Fit (heart rate)',
                            }
                        )
                        saved_count += 1
            
            except Exception as hr_err:
                # Ignora se non ci sono dati heart rate
                pass
            
        except Exception as e:
            errors.append(f"Cane {dog.dog_name}: {str(e)}")
            skipped += 1
    
    return {"saved": saved_count, "skipped": skipped, "errors": errors}


@login_required
def health_data_history(request, dog_id, source_type=None):
    """Visualizza lo storico dati Google Health/Fit per un cane."""
    dog = get_object_or_404(DogProfile, id=dog_id, owner=request.user)
    
    data_points = HealthDataPoint.objects.filter(dog=dog)
    if source_type:
        data_points = data_points.filter(source_type=source_type)
    
    data_points = data_points.order_by('-start_time')[:100]
    
    # Prepara dati per grafico
    chart_data = {
        'labels': [dp.start_time.strftime('%d/%m') for dp in reversed(data_points)],
    }
    if source_type == 'steps' or not source_type:
        chart_data['steps'] = [dp.value for dp in reversed(data_points.filter(source_type='steps'))]
    if source_type == 'heart_rate' or not source_type:
        chart_data['heart_rate'] = [dp.value for dp in reversed(data_points.filter(source_type='heart_rate'))]
    
    return render(request, "canine_tools/health_history.html", {
        "dog": dog,
        "data_points": data_points,
        "chart_data_json": json.dumps(chart_data),
        "selected_source": source_type,
    })


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
