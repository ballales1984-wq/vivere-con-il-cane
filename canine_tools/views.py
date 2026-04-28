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


@login_required
def heart_recorder(request):
    """Pagina principale per registrare i battiti cardiaci."""
    dogs = []
    recordings = []
    dogs = DogProfile.objects.filter(owner=request.user)
    recordings = HeartSoundRecording.objects.filter(owner=request.user).order_by("-created_at")[:10]
    return render(request, "canine_tools/heart_recorder.html", {"dogs": dogs, "recordings": recordings})


@login_required
def heart_recording_detail(request, recording_id):
    """Dettaglio di una registrazione cardiaca con analisi completa."""
    recording = get_object_or_404(HeartSoundRecording, id=recording_id, owner=request.user)
    
    # Ricalcola analisi completa (envelope, S1/S2, HRV) per grafico e metriche avanzate
    import tempfile
    import os
    from django.core.files.storage import default_storage
    
    # Scarica file audio in temp per analisi (funziona con qualsiasi storage backend)
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
        with recording.audio_file.open('rb') as src:
            tmp_file.write(src.read())
        tmp_path = tmp_file.name
    
    try:
        analysis = analyze_heart_sound(tmp_path, subject_type=recording.get_subject_type())
    finally:
        os.unlink(tmp_path)  # cleanup
    
    # Interpretazione BPM in base al soggetto (cane vs umano) e taglia
    subject_type = recording.get_subject_type()
    normal_range = recording.get_normal_bpm_range()
    is_normal = normal_range[0] <= analysis['bpm'] <= normal_range[1] if analysis['bpm'] > 0 else None
    
    interpretation = {
        'subject_type': subject_type,
        'normal_range': normal_range,
        'normal_range_display': recording.get_normal_bpm_range_display(),
        'is_normal': is_normal,
        'bpm': analysis['bpm'],
    }
    
    return render(request, "canine_tools/heart_recording_detail.html", {
        "recording": recording,
        "analysis": analysis,
        "analysis_json": json.dumps(analysis),
        "interpretation": interpretation,
    })


@login_required
def heart_recording_export_csv(request, recording_id):
    """Esporta i risultati dell'analisi in CSV."""
    recording = get_object_or_404(HeartSoundRecording, id=recording_id, owner=request.user)
    
    import tempfile
    import os
    import csv
    from django.http import HttpResponse
    
    # Ricalcola analisi per dati completi
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
        with recording.audio_file.open('rb') as src:
            tmp_file.write(src.read())
        tmp_path = tmp_file.name
    
    try:
        analysis = analyze_heart_sound(tmp_path, subject_type=recording.get_subject_type())
    finally:
        os.unlink(tmp_path)
    
    # Prepara response CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="heart_recording_{recording_id}_{recording.created_at.strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response, delimiter=';')
    # Intestazioni
    writer.writerow(['# Analisi fonocardiografica - Vivere con il Cane'])
    writer.writerow(['# Cane', recording.dog.dog_name if recording.dog else 'N/A'])
    writer.writerow(['# Data', recording.created_at.strftime('%Y-%m-%d %H:%M')])
    writer.writerow(['# Durata (s)', analysis['duration']])
    writer.writerow(['# BPM', analysis['bpm']])
    writer.writerow(['# Battiti totali', analysis['beat_count']])
    writer.writerow(['# Confidenza', f"{analysis['confidence']*100:.1f}%"])
    if analysis.get('hrv'):
        h = analysis['hrv']
        writer.writerow(['# HRV - SDNN (s)', h['sdnn_sec']])
        writer.writerow(['# HRV - RMSSD (s)', h['rmssd_sec']])
        writer.writerow(['# HRV - pNN50 (%)', h['pnn50_percent']])
    writer.writerow([])
    
    # Dati per ogni battito
    writer.writerow(['N.', 'Tempo (s)', 'Ampiezza', 'Intervallo dal precedente (s)', 'Intervallo (ms)'])
    
    peak_times = analysis['peak_times']
    amplitudes = analysis['amplitudes']
    
    for i in range(len(peak_times)):
        t = peak_times[i]
        a = amplitudes[i]
        if i == 0:
            interval_s = ''
            interval_ms = ''
        else:
            interval_s = round(peak_times[i] - peak_times[i-1], 4)
            interval_ms = round(interval_s * 1000, 1) if interval_s != '' else ''
        writer.writerow([i+1, f"{t:.4f}", f"{a:.4f}", f"{interval_s}" if interval_s != '' else '', f"{interval_ms}" if interval_ms != '' else ''])
    
    return response




@login_required
def heart_analyze_ai(request, recording_id):
    """Analizza una registrazione cardiaca con LLM (Groq/OpenAI)."""
    import tempfile, os, requests
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    
    recording = get_object_or_404(HeartSoundRecording, id=recording_id, owner=request.user)
    tmp_path = None
    
    try:
        # Salva audio in file temporaneo
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
            with recording.audio_file.open('rb') as src:
                tmp_file.write(src.read())
            tmp_path = tmp_file.name
        
        # Analisi audio
        subject_type = recording.get_subject_type()
        analysis = analyze_heart_sound(tmp_path, subject_type=subject_type)
        
        # Prepara prompt LLM
        subject_name = recording.dog.dog_name if recording.dog else "l'utente"
        subject_weight = f"{recording.dog.weight} kg" if recording.dog and recording.dog.weight else "N/A"
        context_display = recording.get_recording_context_display() if recording.recording_context else "N/A"
        
        # Rapporto S1/S2 safe (evita divisione per zero)
        s1_s2_ratio = "N/A"
        if analysis.get('s1_s2') and analysis['s1_s2']['s2_avg_amplitude'] > 0:
            s1_s2_ratio = f"{analysis['s1_s2']['s1_avg_amplitude'] / analysis['s1_s2']['s2_avg_amplitude']:.2f}"
        
        prompt = f"""Sei un veterinario specializzato in cardiologia animale. Analizza questi dati di fonocardiografia.

**Dati:**
- Soggetto: {subject_name} ({'cane' if subject_type=='dog' else 'umano'})
- Peso: {subject_weight}
- Contesto: {context_display}
- Durata: {analysis['duration']} s
- BPM: {analysis['bpm']}
- Battiti (S1): {analysis['beat_count']}
- Confidenza: {analysis['confidence']:.2f}

**HRV:**"""
        if analysis.get('hrv'):
            h = analysis['hrv']
            prompt += f" SDNN={h['sdnn_sec']}s, RMSSD={h['rmssd_sec']}s, pNN50={h['pnn50_percent']}%"
        else:
            prompt += " Non disponibile."
        
        prompt += f"""
**S1/S2:** S1={analysis['s1_s2']['s1_count'] if analysis.get('s1_s2') else 'N/A'}, S2={analysis['s1_s2']['s2_count'] if analysis.get('s1_s2') else 'N/A'}, Rapporto={s1_s2_ratio}

Fornisci 4 punti:
1. Stato attuale (normale/stressato/patologico)
2. Confronto BPM con range normale ({subject_weight if subject_type=='dog' else '60-100 BPM'})
3. Significato HRV e S1/S2
4. Consigli pratici

Max 150 parole, italiano chiaro."""
        
        # Chiama LLM
        grok_key = os.environ.get("GROK_API_KEY", "")
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        analysis_text = None
        
        if grok_key and len(grok_key) > 20:
            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {grok_key}"},
                    json={"model": "llama-3.3-70b-versatile", "messages": [
                        {"role": "system", "content": "Sei un veterinario cardio esperto. Rispondi in italiano, conciso, max 150 parole."},
                        {"role": "user", "content": prompt}
                    ], "temperature": 0.7, "max_tokens": 400},
                    timeout=25,
                )
                if resp.status_code == 200:
                    analysis_text = resp.json()["choices"][0]["message"]["content"]
            except Exception:
                pass
        
        if not analysis_text and openai_key and len(openai_key) > 20:
            try:
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {openai_key}"},
                    json={"model": "gpt-4o-mini", "messages": [
                        {"role": "system", "content": "Sei un veterinario cardio esperto. Rispondi in italiano, conciso, max 150 parole."},
                        {"role": "user", "content": prompt}
                    ], "temperature": 0.7, "max_tokens": 400},
                    timeout=25,
                )
                if resp.status_code == 200:
                    analysis_text = resp.json()["choices"][0]["message"]["content"]
            except Exception:
                pass
        
        if not analysis_text:
            analysis_text = "⚠️ Servizio IA non disponibile. Verifica le chiavi API nel file .env."
        
        return JsonResponse({
            "success": True,
            "recording_id": recording.id,
            "analysis_text": analysis_text,
            "subject": subject_name,
            "bpm": analysis['bpm'],
        })
        
    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


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
    context = request.POST.get("recording_context", "")
    subject_type = request.POST.get("subject_type", "dog")  # dog o human

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
        analysis = analyze_heart_sound(temp_path, context, subject_type=subject_type)
        
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
            recording_context=context,
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


def analyze_heart_sound(filepath, context='', subject_type='dog'):
    """
    Analisi avanzata di fonocardiografia digitale.
    Pipeline: filtro 20-150 Hz -> envelope Hilbert -> normalizzazione -> find_peaks.
    Estrae: tempi battiti, ampiezze, distinzione S1/S2, HRV, pulizia outlier.
    Restituisce: duration, bpm, beat_count, confidence, peak_times, amplitudes,
                 s1_s2_classification, hrv_metrics, envelope_data (per grafico).
    """
    try:
        import numpy as np
        import librosa
        from scipy.signal import butter, filtfilt, hilbert, find_peaks, savgol_filter

        # --- 1. CARICAMENTO ---
        ext = os.path.splitext(filepath)[1].lower()
        
        # Per file WebM/OGG/MP3 etc: usa pydub (richiede ffmpeg)
        if ext in ('.webm', '.ogg', '.mp3', '.m4a', '.flac', '.wma', '.aac'):
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(filepath)
                # Converti a mono
                if audio.channels == 2:
                    audio = audio.set_channels(1)
                # Converti a 16-bit per consistenza (se non lo è)
                if audio.sample_width != 2:
                    audio = audio.set_sample_width(2)
                # Ottieni array di campioni
                samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
                # Normalizza a [-1, 1] per 16-bit
                samples = samples / 32768.0
                y = samples
                sr = audio.frame_rate
            except ImportError:
                raise ImportError("pydub non installato. pip install pydub (e installa ffmpeg nel sistema)")
            except Exception as e:
                # Se pydub fallisce, prova con librosa come fallback (ma probabilmente fallirà)
                import librosa
                y, sr = librosa.load(filepath, sr=None, mono=True, dtype=np.float32)
        else:
            # WAV o altri formati supportati da librosa/soundfile
            import librosa
            y, sr = librosa.load(filepath, sr=None, mono=True, dtype=np.float32)
        
        duration = len(y) / sr

        # Normalizza
        y = y / (np.max(np.abs(y)) + 1e-9)

        # --- 2. FILTRO PASSA-BANDA 20-150 Hz Butterworth 4° ordine ---
        def bandpass_filter(signal, fs, low=20, high=150, order=4):
            nyq = fs / 2
            b, a = butter(order, [low/nyq, high/nyq], btype='band')
            return filtfilt(b, a, signal)

        y_filt = bandpass_filter(y, sr)
        # Safe guard: sostituisci NaN/inf con segnale originale normalizzato
        if np.any(np.isnan(y_filt)) or np.any(np.isinf(y_filt)):
            y_filt = y

        # --- 3. ENVELOPE Hilbert + Smoothing Savitzky-Golay ---
        analytic = hilbert(y_filt)
        envelope = np.abs(analytic)

        # Smoothing: window length dipende da ampiezza envelope
        max_window = 101
        # Determina window_len: deve essere dispari e < len(envelope)
        win_len = min(max_window, len(envelope) - 1 if len(envelope) % 2 == 0 else len(envelope))
        if win_len > 3:
            env_max_val = np.max(envelope)
            if env_max_val < 0.05:
                win_len = min(31, win_len)
            # Assicura che window sia dispari
            if win_len % 2 == 0:
                win_len = max(3, win_len - 1)
            envelope_smooth = savgol_filter(envelope, win_len, 3)
        else:
            envelope_smooth = envelope

        envelope_smooth = np.nan_to_num(envelope_smooth, nan=0.0, posinf=0.0, neginf=0.0)

        # --- 4. NORMALIZZAZIONE envelope a [0, 1] ---
        env_min, env_max = np.min(envelope_smooth), np.max(envelope_smooth)
        env_range = env_max - env_min
        if env_range < 1e-6:
            # Fallback: normalizza segnale assoluto filtrato
            abs_sig = np.abs(y_filt)
            max_abs = np.max(abs_sig)
            if max_abs < 1e-6:
                env_norm = np.zeros_like(envelope_smooth)
            else:
                env_norm = abs_sig / (max_abs + 1e-9)
        else:
            env_norm = (envelope_smooth - env_min) / (env_range + 1e-9)

        # Safe guard: sostituisci NaN/inf con 0
        env_norm = np.nan_to_num(env_norm, nan=0.0, posinf=0.0, neginf=0.0)
        # Clamp a [0, 1] per sicurezza
        env_norm = np.clip(env_norm, 0.0, 1.0)

        # --- 5. RILEVAMENTO PICCHI - Robustezza e sensibilità ---
        # Fase 1: detection permissiva iniziale per candidati
        # Soglia bassa basata su percentile (60) + offset minimo
        threshold_low = max(np.percentile(env_norm, 60), 0.04)
        threshold_low = min(threshold_low, 0.5)
        
        # Distanza minima corta (100 ms) per non perdere S1/S2 ravvicinati
        min_distance_initial = int(0.10 * sr)
        
        peaks_initial, _ = find_peaks(env_norm, distance=min_distance_initial, height=threshold_low, prominence=0.0005)
        
        # Fase 2: stima BPM per threshold adattivo (min_distance rimane corta)
        if len(peaks_initial) >= 3:
            peak_times_initial = peaks_initial / sr
            intervals_initial = np.diff(peak_times_initial)
            median_interval = np.median(intervals_initial)
            # Filtra intervalli anomali per stima più pulita
            valid_mask = (intervals_initial >= 0.5 * median_interval) & (intervals_initial <= 1.5 * median_interval)
            if np.any(valid_mask):
                median_interval = np.median(intervals_initial[valid_mask])
            estimated_bpm = int(60.0 / median_interval) if median_interval > 0 else 0
            # Non adattiamo min_distance in base a BPM — teniamo 100-150ms per rilevare sia S1 che S2
            # Se BPM è alto (intervallo piccolo), min_distance 100ms va bene; se BPM basso, va bene lo stesso
            min_distance = int(0.12 * sr)  # 120 ms fixed — sufficiente a separare rumore, lascia passare S1+S2
        else:
            min_distance = int(0.12 * sr)
        
        # Fase 3: threshold principale — robusto ma sensibile
        if len(peaks_initial) >= 5:
            initial_amplitudes = env_norm[peaks_initial]
            median_amp = np.median(initial_amplitudes)
            mad = np.median(np.abs(initial_amplitudes - median_amp))
            # Usa 1.2×MAD per essere più sensibile (avevamo 1.5)
            threshold_main = median_amp + 1.2 * mad
            # Limiti: floor 0.06 (per picchi deboli), ceiling 0.75
            threshold_main = np.clip(threshold_main, 0.06, 0.75)
        else:
            # Pochi candidati: usa percentile diretto
            threshold_main = max(np.percentile(env_norm, 65), 0.05)
            threshold_main = min(threshold_main, 0.70)
        
        # Fase 4: prominence adattiva ma bassa
        peak_to_peak_var = np.std(env_norm[peaks_initial]) if len(peaks_initial) >= 3 else 0.02
        prom = max(0.0005, 0.03 * threshold_main + 0.2 * peak_to_peak_var)
        prom = min(prom, threshold_main * 0.4)
        
        # Rilevazione principale
        peaks, properties = find_peaks(env_norm, distance=min_distance, height=threshold_main, prominence=prom)
        
        # Fase 5: fallback gerarchico se pochi picchi
        if len(peaks) < 2 and len(peaks_initial) >= 2:
            fallback_levels = [
                (0.9, 0.002),
                (0.75, 0.001),
                (0.55, 0.0005),
                (0.4, 0.0002),
            ]
            for mult, p in fallback_levels:
                lower_thresh = threshold_main * mult
                if lower_thresh < 0.03:
                    lower_thresh = 0.03
                peaks, properties = find_peaks(env_norm, distance=min_distance, height=lower_thresh, prominence=p)
                if len(peaks) >= 2:
                    break
        
        # Fallback finale: threshold molto bassa, distance ridotta
        if len(peaks) < 2:
            peaks, properties = find_peaks(env_norm, distance=int(0.08 * sr), height=0.02, prominence=0.0002)
        
        # Fase 5: fallback gerarchico se pochi picchi
        if len(peaks) < 2 and len(peaks_initial) >= 2:
            # Threshold più bassa ma non permissiva all'estremo
            fallback_levels = [
                (0.85, 0.003),   # 85% della threshold originale, prominence minima
                (0.7, 0.002),
                (0.5, 0.001),
                (0.35, 0.0005),
            ]
            for mult, p in fallback_levels:
                lower_thresh = threshold_main * mult
                if lower_thresh < 0.06:
                    lower_thresh = 0.06
                peaks, properties = find_peaks(
                    env_norm,
                    distance=min_distance,
                    height=lower_thresh,
                    prominence=p
                )
                if len(peaks) >= 2:
                    break
        
        # --- 5. RILEVAMENTO PICCHI - Parametri ottimizzati per sensibilità ---
        # Fase 1: detection permissiva iniziale
        threshold_low = max(np.percentile(env_norm, 55), 0.03)  # più permissivo
        threshold_low = min(threshold_low, 0.45)
        
        min_distance_initial = int(0.08 * sr)  # 80 ms per non perdere S1/S2 ravvicinati
        peaks_initial, _ = find_peaks(env_norm, distance=min_distance_initial, height=threshold_low, prominence=0.0002)
        
        # Min distance per detection principale: 80 ms (basso, per permettere sia S1 che S2)
        min_distance = int(0.08 * sr)
        
        # Threshold principale: mediana + 1.0 MAD (più sensibile), floor 0.04
        if len(peaks_initial) >= 5:
            initial_amplitudes = env_norm[peaks_initial]
            median_amp = np.median(initial_amplitudes)
            mad = np.median(np.abs(initial_amplitudes - median_amp))
            threshold_main = median_amp + 1.0 * mad
            threshold_main = np.clip(threshold_main, 0.04, 0.70)
        else:
            threshold_main = max(np.percentile(env_norm, 60), 0.03)
            threshold_main = min(threshold_main, 0.60)
        
        # Prominence molto bassa
        peak_to_peak_var = np.std(env_norm[peaks_initial]) if len(peaks_initial) >= 3 else 0.015
        prom = max(0.0002, 0.02 * threshold_main + 0.1 * peak_to_peak_var)
        prom = min(prom, threshold_main * 0.3)
        
        peaks, properties = find_peaks(env_norm, distance=min_distance, height=threshold_main, prominence=prom)
        
        # Fallback gerarchico
        if len(peaks) < 2 and len(peaks_initial) >= 2:
            fallback_levels = [
                (0.95, 0.0015),
                (0.8, 0.001),
                (0.6, 0.0005),
                (0.4, 0.0002),
            ]
            for mult, p in fallback_levels:
                lower_thresh = threshold_main * mult
                if lower_thresh < 0.02:
                    lower_thresh = 0.02
                peaks, properties = find_peaks(env_norm, distance=min_distance, height=lower_thresh, prominence=p)
                if len(peaks) >= 2:
                    break
        
        if len(peaks) < 2:
            peaks, properties = find_peaks(env_norm, distance=int(0.06 * sr), height=0.015, prominence=0.0001)

        # Calcola tempi e ampiezze dei picchi (prima della pulizia artefatti)
        peak_times = (peaks / sr).tolist()
        amplitudes = env_norm[peaks].tolist()
        beat_count = len(peaks)

        # --- RIMOZIONE ARTEFATTI INIZIALI ---
        # Se il primo picco è troppo vicino all'inizio (<0.35s) e il secondo intervallo è normale (>0.5s),
        # probabilmente è un transitorio/rumore: rimuovilo
        if len(peaks) >= 3:
            first_time = peak_times[0]
            second_interval = peak_times[1] - peak_times[0]
            if first_time < 0.35 and second_interval > 0.5:
                peaks = peaks[1:]
                peak_times = peak_times[1:]
                amplitudes = amplitudes[1:]
                beat_count = len(peaks)

        # --- 6. VALIDAZIONE FISIOLOGICA (post-detection) ---
        # Controlla se i BPM stimati sono in range fisiologico
        # Nota: qui misuriamo BPM basato su tutti i picchi (S1+S2), quindi atteso ~2× BPM reale se entrambi rilevati
        physiological_bpm_estimate = 0
        if beat_count >= 2:
            times_arr = np.array(peak_times)
            intervals = np.diff(times_arr)
            avg_interval = np.mean(intervals)
            candidate_bpm = int(60.0 / avg_interval) if avg_interval > 0 else 0
            
            # Se candidate_bpm > 300, è probabilmente rumore o artefatti (troppo alto per qualsiasi soggetto)
            # Se 200-300, potrebbe essere S1+S2 separati di un BPM reale 100-150 (accettabile)
            # Se < 30, potrebbe essere artefatti a bassa frequenza
            if candidate_bpm > 350:
                # Probabile falso positivo da rumore ad alta frequenza
                #Applica threshold più severa e riduci numero di picchi
                high_freq_mask = amplitudes >= np.percentile(amplitudes, 60)
                peaks = peaks[high_freq_mask]
                peak_times = (peaks / sr).tolist()
                amplitudes = env_norm[peaks].tolist()
                beat_count = len(peaks)
            elif candidate_bpm < 25 and beat_count > 5:
                # BPM troppo basso → probabilmente artefatti lenti o baseline wander
                # Mantieni solo picchi con ampiezza sopra soglia relativa
                amp_threshold = 0.15 * np.max(amplitudes)
                keep_mask = np.array(amplitudes) >= amp_threshold
                peaks = peaks[keep_mask]
                peak_times = (peaks / sr).tolist()
                amplitudes = env_norm[peaks].tolist()
                beat_count = len(peaks)

        # --- 6. PULIZIA OUTLIER ROBUSTA (conservativa) ---
        # Solo se abbiamo un numero sufficiente di picchi (>=7) per evitare over-cleaning
        if len(peaks) >= 7:
            peak_times_arr = peaks / sr
            intervals = np.diff(peak_times_arr)
            
            # PASS 1: Rimuovi solo outlier evidenti di ampiezza (usando MAD, ma più permissiva)
            amplitudes_arr = env_norm[peaks]
            median_amp = np.median(amplitudes_arr)
            mad_amp = np.median(np.abs(amplitudes_arr - median_amp))
            # Soglia: entro 3.5 MAD (invece di 3) per essere più conservativi
            amp_lower = median_amp - 3.5 * (mad_amp + 1e-9)
            amp_upper = median_amp + 3.5 * (mad_amp + 1e-9)
            amp_mask = (amplitudes_arr >= amp_lower) & (amplitudes_arr <= amp_upper)
            peaks_filtered = peaks[amp_mask]
            
            # Se abbiamo rimosso troppi picchi (>20%), annulla la pulizia
            if len(peaks_filtered) < 0.8 * len(peaks):
                peaks_filtered = peaks
            
            peaks = peaks_filtered
            
            # PASS 2: Pulizia intervalli — solo se rimangono >=7 picchi
            if len(peaks) >= 7:
                peak_times_arr = peaks / sr
                intervals = np.diff(peak_times_arr)
                median_int = np.median(intervals)
                mad_int = np.median(np.abs(intervals - median_int))
                
                # Soglia più permissiva: 3×MAD (invece di 2.5×)
                if mad_int < 0.01:
                    int_lower = 0.5 * median_int
                    int_upper = 1.5 * median_int
                else:
                    int_lower = median_int - 3.0 * mad_int
                    int_upper = median_int + 3.0 * mad_int
                
                # Assicura limiti ragionevoli
                int_lower = max(int_lower, 0.5 * median_int)
                int_upper = min(int_upper, 1.5 * median_int)
                
                if len(intervals) >= 3:
                    valid_mask_intervals = (intervals >= int_lower) & (intervals <= int_upper)
                    keep = np.ones(len(peaks), dtype=bool)
                    if len(valid_mask_intervals) > 0:
                        keep[0] = valid_mask_intervals[0]
                    if len(valid_mask_intervals) >= 2:
                        keep[1:-1] = valid_mask_intervals[:-1] & valid_mask_intervals[1:]
                    if len(valid_mask_intervals) > 0:
                        keep[-1] = valid_mask_intervals[-1]
                    
                    # Controlla quanti picchi verrebbero rimossi
                    if np.sum(keep) >= 0.8 * len(peaks):
                        peaks = peaks[keep]
                    # altrimenti mantieni tutti
            
            # Ri-calcola dopo pulizia
            peak_times = (peaks / sr).tolist()
            amplitudes = env_norm[peaks].tolist()
            beat_count = len(peaks)

        # --- 7. ANALISI BPM E CLASSIFICAZIONE ---
        s1_s2_classification = None
        hrv_metrics = None
        bpm = 0
        confidence = 0.0
        
        # Per grafico: di default mostriamo tutti i picchi rilevati
        # Se classifichiamo S1/S2, mostriamo solo S1 per coerenza con beat_count
        display_peak_times = peak_times
        display_amplitudes = amplitudes
        
        if beat_count >= 2:
            times_arr = np.array(peak_times)
            amps_arr = np.array(amplitudes)
            intervals_all = np.diff(times_arr)
            
            # Se è un umano e il BPM calcolato direttamente è troppo basso (<45),
            # potrebbe essere che l'algoritmo ha perso metà dei picchi.
            # In tal caso, usa i picchi diretti.
            candidate_bpm_direct = int(60.0 / np.mean(intervals_all)) if np.mean(intervals_all) > 0 else 0
            
            # Rileva presenza di componenti S1 e S2
            if len(intervals_all) >= 3:
                short_ratio = np.mean(intervals_all < 0.2)
                has_dual_components = short_ratio >= 0.2
            else:
                has_dual_components = False
            
            # Per umani: se i BPM diretti sono molto bassi (<50), forziamo la modalità senza accoppiamento
            if subject_type == 'human' and candidate_bpm_direct > 0 and candidate_bpm_direct < 50:
                has_dual_components = False
            
            if has_dual_components and subject_type != 'human':
                # Accorpa picchi consecutivi come S1/S2
                n_pairs = beat_count // 2
                if n_pairs >= 1:
                    s1_times_list = []
                    s1_amps_list = []
                    s2_times_list = []
                    s2_amps_list = []

                    for i in range(n_pairs):
                        idx1 = i * 2
                        idx2 = i * 2 + 1
                        a1 = amps_arr[idx1]
                        a2 = amps_arr[idx2]
                        t1 = times_arr[idx1]
                        t2 = times_arr[idx2]
                        if a1 >= a2:
                            s1_times_list.append(t1)
                            s1_amps_list.append(a1)
                            s2_times_list.append(t2)
                            s2_amps_list.append(a2)
                        else:
                            s1_times_list.append(t2)
                            s1_amps_list.append(a2)
                            s2_times_list.append(t1)
                            s2_amps_list.append(a1)
                    
                    s1_times_arr = np.array(s1_times_list)
                    s1_amps_arr = np.array(s1_amps_list)
                    s2_times_arr = np.array(s2_times_list)
                    s2_amps_arr = np.array(s2_amps_list)
                    
                    # BPM da S1 (per umani: intervallo tra S1)
                    # Per cani: S1-S1 = 1 battito, ma se accoppiamo S1/S2,
                    # l'intervallo S1-S1 già rappresenta i battiti corretti
                    if len(s1_times_arr) >= 2:
                        s1_intervals = np.diff(s1_times_arr)
                        avg_s1_int = np.mean(s1_intervals)
                        bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
                        # Per umani (sempre accoppiati), i BPM da S1 sono corretti
                        # Per cani, S1-S1 = battito completo, già OK
                        if len(s1_intervals) > 1:
                            std_s1 = np.std(s1_intervals)
                            cv = std_s1 / (avg_s1_int + 1e-9)
                            reg_score = max(0.0, 1.0 - cv)
                            n_score = min(1.0, len(s1_times_arr) / 20.0)
                            confidence = round(0.5 + 0.3 * reg_score + 0.2 * n_score, 2)
                        else:
                            confidence = 0.5
                    else:
                        confidence = 0.0
                    
                    # HRV (>=3 S1)
                    if len(s1_times_arr) >= 3:
                        sdnn = float(np.std(s1_intervals))
                        diff_sq = np.square(np.diff(s1_intervals))
                        rmssd = float(np.sqrt(np.mean(diff_sq))) if len(diff_sq) > 0 else 0.0
                        diff_ms = np.diff(s1_intervals) * 1000.0
                        pnn50 = float(np.mean(np.abs(diff_ms) > 50.0) * 100.0)
                        hrv_metrics = {
                            "sdnn_sec": round(sdnn, 4),
                            "rmssd_sec": round(rmssd, 4),
                            "pnn50_percent": round(pnn50, 2),
                            "mean_hr_sec": round(float(np.mean(s1_intervals)), 4),
                        }
                    
                    s1_s2_classification = {
                        "s1_count": int(len(s1_times_arr)),
                        "s2_count": int(len(s2_times_arr)),
                        "s1_avg_amplitude": float(np.mean(s1_amps_arr)) if len(s1_amps_arr) > 0 else 0.0,
                        "s2_avg_amplitude": float(np.mean(s2_amps_arr)) if len(s2_amps_arr) > 0 else 0.0,
                    }
                    
                    # Per grafico: mostra solo S1 (coerenza con beat_count)
                    display_peak_times = s1_times_list
                    display_amplitudes = s1_amps_list
                    
                    # beat_count = numero di cicli S1
                    beat_count = len(s1_times_arr)
                else:
                    bpm = int(60.0 / np.mean(intervals_all)) if np.mean(intervals_all) > 0 else 0
                    confidence = 0.5
            else:
                # Tutti i picchi sono S1 (o singola componente)
                s1_times_arr = times_arr
                intervals_s1 = intervals_all
                avg_s1_int = np.mean(intervals_s1)
                bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
                if len(intervals_s1) > 1:
                    std_s1 = np.std(intervals_s1)
                    cv = std_s1 / (avg_s1_int + 1e-9)
                    reg_score = max(0.0, 1.0 - cv)
                    n_score = min(1.0, len(s1_times_arr) / 20.0)
                    confidence = round(0.5 + 0.3 * reg_score + 0.2 * n_score, 2)
                else:
                    confidence = 0.5
                if len(intervals_s1) >= 2:
                    sdnn = float(np.std(intervals_s1))
                    diff_sq = np.square(np.diff(intervals_s1))
                    rmssd = float(np.sqrt(np.mean(diff_sq))) if len(diff_sq) > 0 else 0.0
                    diff_ms = np.diff(intervals_s1) * 1000.0
                    pnn50 = float(np.mean(np.abs(diff_ms) > 50.0) * 100.0)
                    hrv_metrics = {
                        "sdnn_sec": round(sdnn, 4),
                        "rmssd_sec": round(rmssd, 4),
                        "pnn50_percent": round(pnn50, 2),
                        "mean_hr_sec": round(float(np.mean(intervals_s1)), 4),
                    }
                # display_peak_times rimane tutti i picchi (che sono tutti S1)
                # beat_count rimane len(peaks)
        else:
            bpm = 0
            confidence = 0.0
            # display_peak_times rimane vuoto se nessun picco
        
        if beat_count >= 2:
            times_arr = np.array(peak_times)
            amps_arr = np.array(amplitudes)
            intervals_all = np.diff(times_arr)
            
            # Rileva presenza di componenti S1 e S2: cerca mix di intervalli brevi (<0.2s) e lunghi
            # In un segnale cardiaco, S1-S2 distano 0.08-0.20s, mentre S1-S1 (o S2-S2) >0.3s
            if len(intervals_all) >= 3:
                short_ratio = np.mean(intervals_all < 0.2)
                has_dual_components = short_ratio >= 0.2  # almeno 20% intervalli brevi
            else:
                has_dual_components = False
            
            if has_dual_components:
                # Componente duale: accorpa picchi consecutivi come S1/S2
                n_pairs = beat_count // 2
                if n_pairs >= 1:
                    s1_times = []
                    s1_amps = []
                    s2_times = []
                    s2_amps = []
                    
                    for i in range(n_pairs):
                        idx1 = i * 2
                        idx2 = i * 2 + 1
                        a1 = amps_arr[idx1]
                        a2 = amps_arr[idx2]
                        t1 = times_arr[idx1]
                        t2 = times_arr[idx2]
                        
                        if a1 >= a2:
                            s1_times.append(t1)
                            s1_amps.append(a1)
                            s2_times.append(t2)
                            s2_amps.append(a2)
                        else:
                            s1_times.append(t2)
                            s1_amps.append(a2)
                            s2_times.append(t1)
                            s2_amps.append(a1)
                    
                    s1_times = np.array(s1_times)
                    s1_amps = np.array(s1_amps)
                    s2_times = np.array(s2_times)
                    s2_amps = np.array(s2_amps)
                    
                    # BPM da intervalli S1
                    if len(s1_times) >= 2:
                        s1_intervals = np.diff(s1_times)
                        avg_s1_int = np.mean(s1_intervals)
                        bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
                        
                        # Confidence: regolarità intervalli + numero cicli
                        if len(s1_intervals) > 1:
                            std_s1 = np.std(s1_intervals)
                            cv = std_s1 / (avg_s1_int + 1e-9)
                            reg_score = max(0.0, 1.0 - cv)
                            n_score = min(1.0, len(s1_times) / 20.0)
                            confidence = round(0.5 + 0.3 * reg_score + 0.2 * n_score, 2)
                        else:
                            confidence = 0.5
                    else:
                        confidence = 0.0
                    
                    # HRV (solo se >= 3 cicli S1 → >=2 intervalli)
                    if len(s1_times) >= 3:
                        sdnn = float(np.std(s1_intervals))
                        diff_sq = np.square(np.diff(s1_intervals))
                        rmssd = float(np.sqrt(np.mean(diff_sq))) if len(diff_sq) > 0 else 0.0
                        diff_ms = np.diff(s1_intervals) * 1000.0
                        pnn50 = float(np.mean(np.abs(diff_ms) > 50.0) * 100.0)
                        hrv_metrics = {
                            "sdnn_sec": round(sdnn, 4),
                            "rmssd_sec": round(rmssd, 4),
                            "pnn50_percent": round(pnn50, 2),
                            "mean_hr_sec": round(float(np.mean(s1_intervals)), 4),
                        }
                    
                    s1_s2_classification = {
                        "s1_count": int(len(s1_times)),
                        "s2_count": int(len(s2_times)),
                        "s1_avg_amplitude": float(np.mean(s1_amps)) if len(s1_amps) > 0 else 0.0,
                        "s2_avg_amplitude": float(np.mean(s2_amps)) if len(s2_amps) > 0 else 0.0,
                    }
                    
                    # beat_count = numero di cicli S1 (coppie complete)
                    beat_count = len(s1_times)
                else:
                    # Non ci sono coppie complete (improbabile con beat_count>=2), usa tutti i picchi
                    bpm = int(60.0 / np.mean(intervals_all)) if np.mean(intervals_all) > 0 else 0
                    confidence = 0.5
                    # beat_count rimane il numero totale di picchi
            else:
                # Componente singola: tutti i picchi considerati S1
                s1_times = times_arr
                intervals_s1 = intervals_all
                avg_s1_int = np.mean(intervals_s1)
                bpm = int(60.0 / avg_s1_int) if avg_s1_int > 0 else 0
                
                if len(intervals_s1) >= 1:
                    std_s1 = np.std(intervals_s1)
                    cv = std_s1 / (avg_s1_int + 1e-9)
                    reg_score = max(0.0, 1.0 - cv)
                    n_score = min(1.0, len(s1_times) / 20.0)
                    confidence = round(0.5 + 0.3 * reg_score + 0.2 * n_score, 2)
                else:
                    confidence = 0.5
                
                if len(intervals_s1) >= 2:
                    sdnn = float(np.std(intervals_s1))
                    diff_sq = np.square(np.diff(intervals_s1))
                    rmssd = float(np.sqrt(np.mean(diff_sq))) if len(diff_sq) > 0 else 0.0
                    diff_ms = np.diff(intervals_s1) * 1000.0
                    pnn50 = float(np.mean(np.abs(diff_ms) > 50.0) * 100.0)
                    hrv_metrics = {
                        "sdnn_sec": round(sdnn, 4),
                        "rmssd_sec": round(rmssd, 4),
                        "pnn50_percent": round(pnn50, 2),
                        "mean_hr_sec": round(float(np.mean(intervals_s1)), 4),
                    }
                # s1_s2_classification rimane None
                # beat_count rimane il numero totale di picchi (tutti S1)
        else:
            bpm = 0
            confidence = 0.0
            # beat_count already set to len(peaks)

        # --- 10. ENVELOPE DATA per grafico (max 2000 punti) ---
        t_env = np.arange(len(env_norm)) / sr
        step = max(1, len(env_norm) // 2000)
        envelope_data = {
            "times": t_env[::step].tolist(),
            "values": env_norm[::step].tolist(),
        }

        # --- 11. RETURN ---
        return {
            "duration": round(duration, 2),
            "bpm": bpm,
            "beat_count": beat_count,
            "confidence": confidence,
            "peak_times": display_peak_times,
            "amplitudes": display_amplitudes,
            "sample_rate": sr,
            "s1_s2": s1_s2_classification,
            "hrv": hrv_metrics,
            "envelope": envelope_data,
            "filter_low": 20,
            "filter_high": 150,
        }


    except ImportError:
        # Fallback: analisi molto semplice senza scipy/librosa
        import wave
        import struct

        with wave.open(filepath, 'rb') as wav:
            sr = wav.getframerate()
            n_frames = wav.getnframes()
            data = wav.readframes(n_frames)
            fmt = f"{n_frames}h"
            try:
                samples = list(struct.unpack(fmt, data))
            except struct.error:
                samples = [0] * n_frames

            duration = n_frames / sr
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
                "amplitudes": [1.0]*len(peaks),
                "sample_rate": sr,
                "s1_s2": None,
                "hrv": None,
                "envelope": None,
            }
