from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, Sum, Count
from .models import (
    DogProfile,
    MedicalEvent,
    HealthLog,
    VeterinaryRequest,
    VeterinaryMedia,
)
from knowledge.models import DogAnalysis, LifetimeMacroAnalysis
from knowledge.views import generate_lifetime_macro_analysis
from datetime import date
import json
import os
from django.core.cache import cache
from xhtml2pdf import pisa
from django.template.loader import get_template


@login_required
def profile_list(request):
    """List all dog profiles for current user."""
    profiles = DogProfile.objects.filter(owner=request.user)
    return render(request, "dog_profile/list.html", {"profiles": profiles})


@login_required
def profile_new(request):
    """Create new dog profile."""
    if request.method == "POST":
        name = request.POST.get("name")
        dog_name = request.POST.get("dog_name")
        breed = request.POST.get("breed")
        birth_date = request.POST.get("birth_date")
        weight = request.POST.get("weight")
        gender = request.POST.get("gender")

        profile = DogProfile.objects.create(
            owner=request.user,
            name=name,
            dog_name=dog_name,
            breed=breed,
            birth_date=birth_date or None,
            weight=weight or None,
            gender=gender,
        )
        return redirect("profile_detail", profile_id=profile.id)

    return render(request, "dog_profile/form.html", {})


@login_required
def profile_detail(request, profile_id):
    """View dog profile restricted to owner."""
    profile = get_object_or_404(DogProfile, id=profile_id, owner=request.user)
    events = profile.medical_events.all().order_by("-date")[:10]
    logs = list(profile.health_logs.filter(log_type="routine").order_by("-date")[:14])
    
    chart_data = {
        "labels": [l.date.strftime("%d/%m") for l in reversed(logs)],
        "walk": [l.walk_minutes or 0 for l in reversed(logs)],
        "play": [l.play_minutes or 0 for l in reversed(logs)],
        "sleep": [float(l.sleep_hours or 0) for l in reversed(logs)],
    }

    return render(
        request,
        "dog_profile/detail.html",
        {
            "profile": profile,
            "events": events,
            "logs": logs,
            "stats": profile.get_lifetime_stats(),
            "chart_data_json": json.dumps(chart_data)
        },
    )


@login_required
def profile_add_event(request, profile_id):
    """Add medical event to profile."""
    profile = get_object_or_404(DogProfile, id=profile_id, owner=request.user)

    if request.method == "POST":
        # Usa la data fornita o quella di oggi - registrazione automatica
        event_date = request.POST.get("date")
        if not event_date:
            event_date = date.today()
        
        MedicalEvent.objects.create(
            dog=profile,
            event_type=request.POST.get("event_type"),
            title=request.POST.get("title"),
            description=request.POST.get("description", ""),
            date=event_date,
        )
        cache.delete(f"daily_coach_{profile.id}_{date.today()}")
        return redirect("profile_detail", profile_id=profile.id)

    return render(request, "dog_profile/event_form.html", {"profile": profile, "default_date": date.today()})


@login_required
def profile_add_log(request, profile_id):
    """Add routine health log (daily metrics)."""
    profile = get_object_or_404(DogProfile, id=profile_id, owner=request.user)

    if request.method == "POST":
        log_date = request.POST.get("date")
        if not log_date:
            log_date = date.today()
        
        HealthLog.objects.create(
            dog=profile,
            date=log_date,
            log_type="routine",
            sleep_hours=request.POST.get("sleep_hours") or None,
            play_minutes=request.POST.get("play_minutes") or None,
            walk_minutes=request.POST.get("walk_minutes") or None,
            food_grams=request.POST.get("food_grams") or None,
            description=request.POST.get("notes", ""),
        )
        cache.delete(f"daily_coach_{profile.id}_{date.today()}")
        return redirect("profile_detail", profile_id=profile.id)

    return render(request, "dog_profile/log_form.html", {"profile": profile, "default_date": date.today()})


@login_required
def my_dog(request):
    """Quick view for the first dog profile of the logged user."""
    profile = DogProfile.objects.filter(owner=request.user).first()
    if not profile:
        return redirect("profile_new")
    return redirect("profile_detail", profile_id=profile.id)


def get_daily_coach_tips(profile):
    """Generate dynamic daily tips using AI based on recent health logs."""
    today_str = date.today().isoformat()
    cache_key = f"daily_coach_{profile.id}_{today_str}"

    # Try cache first
    cached_tips = cache.get(cache_key)
    if cached_tips:
        return cached_tips

    logs = list(profile.health_logs.filter(log_type="routine").order_by("-date")[:7])
    if not logs:
        return [
            "Inizia a registrare il Check-in quotidiano per ricevere consigli IA personalizzati!"
        ]

    # Build history context
    history_text = f"Cane: {profile.dog_name}, Razza: {profile.breed}, Età: {profile.get_age()} anni.\n"
    history_text += "Storico ultimi giorni (Passeggiata min, Gioco min, Sonno ore):\n"
    for l in reversed(logs):
        history_text += f"- {l.date}: {l.walk_minutes or 0}m pass., {l.play_minutes or 0}m gioco, {l.sleep_hours or 0}h sonno.\n"
    
    # NEW: Add recent medical events (last 14 days)
    recent_date = date.today() - timezone.timedelta(days=14)
    medical_events = profile.medical_events.filter(date__gte=recent_date).order_by("-date")
    if medical_events.exists():
        history_text += "\nEventi Medici Recenti (IMPORTANTE):\n"
        for me in medical_events:
            history_text += f"- {me.date}: {me.title} ({me.get_event_type_display()}). Descrizione: {me.description or 'N/D'}\n"

    system_msg = "Sei un 'AI Daily Coach' per cani. Fornisci 2 consigli BREVI (max 15 parole l'uno) e molto pratici per la giornata di oggi, basati sui trend degli ultimi giorni E sugli eventuali problemi medici recenti segnalati. Sii incoraggiante."
    prompt = f'Analizza lo storico e gli eventi medici recenti e dammi 2 consigli per oggi.\n{history_text}\n\nRispondi ESATTAMENTE con un array JSON di stringhe, es: ["consiglio 1", "consiglio 2"]. Niente altro.'

    api_key = os.environ.get("GROK_API_KEY", "")
    if not api_key or len(api_key) < 20:
        return [
            "Monitora sempre il riposo di Fido dopo l'attività fisica.",
            "Una sessione di masticazione aiuta a rilassare il cane a fine giornata.",
        ]

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {
                    "type": "json_object"
                },  # We might need to ensure valid JSON, but array is fine if parsing
            },
            timeout=10,
        )
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            try:
                # Sometime LLMs wrap in Markdown
                content = content.replace("```json", "").replace("```", "").strip()
                import json

                tips = json.loads(content)
                if isinstance(tips, dict):  # if it returned {"tips": [...]}
                    tips = list(tips.values())[0]
                if isinstance(tips, list) and len(tips) > 0:
                    cache.set(cache_key, tips[:2], 60 * 60 * 24)  # Cache for 24h
                    return tips[:2]
            except Exception as e:
                import logging

                logging.warning(
                    f"JSON Parse error for Daily Coach: {e} - Content: {content}"
                )
    except Exception as e:
        import logging

        logging.warning(f"API error for Daily Coach: {e}")

    return [
        "Usa il Check-in quotidiano per tenere traccia dei progressi!",
        "Ricorda di premiare sempre i comportamenti calmi.",
    ]


@login_required
def dashboard(request):
    """Main dashboard - private view for owner's dogs."""
    profiles = list(
        DogProfile.objects.filter(owner=request.user).annotate(
            events_count=Count("medical_events")
        )
    )

    chart_data = []
    for profile in profiles:
        profile.recent_analyses = list(profile.analyses.all()[:5])

        # Last 6 health logs for mini-chart
        logs = list(profile.health_logs.order_by("-date")[:6])
        # Check if daily routine logged today
        today = date.today()
        profile.logged_today = profile.health_logs.filter(
            date=today, log_type="routine"
        ).exists()

        # Get AI Coach tips
        profile.daily_tips = get_daily_coach_tips(profile)

        if logs:
            profile.has_chart = True
            chart_data.append(
                {
                    "id": str(profile.id),
                    "labels": [str(l.date) for l in reversed(logs)],
                    "walk": [l.walk_minutes or 0 for l in reversed(logs)],
                    "play": [l.play_minutes or 0 for l in reversed(logs)],
                    "sleep": [float(l.sleep_hours or 0) for l in reversed(logs)],
                }
            )
        else:
            profile.has_chart = False

    return render(
        request,
        "dog_profile/dashboard.html",
        {"profiles": profiles, "chart_data_json": chart_data},
    )


@login_required
def log_daily_routine(request, profile_id):
    """Handle daily habit check-in submission from dashboard."""
    if request.method == "POST":
        profile = get_object_or_404(DogProfile, id=profile_id, owner=request.user)
        walk_minutes = request.POST.get("walk_minutes")
        sleep_hours = request.POST.get("sleep_hours")
        play_minutes = request.POST.get("play_minutes")
        food_grams = request.POST.get("food_grams")

        # Safe conversion with defaults
        try:
            walk_minutes = int(walk_minutes) if walk_minutes else None
        except (ValueError, TypeError):
            walk_minutes = None

        try:
            sleep_hours = float(sleep_hours) if sleep_hours else None
        except (ValueError, TypeError):
            sleep_hours = None

        try:
            play_minutes = int(play_minutes) if play_minutes else None
        except (ValueError, TypeError):
            play_minutes = None

        try:
            food_grams = int(food_grams) if food_grams else None
        except (ValueError, TypeError):
            food_grams = None

        # Create health log for today
        HealthLog.objects.create(
            dog=profile,
            date=date.today(),
            log_type="routine",
            walk_minutes=walk_minutes,
            sleep_hours=sleep_hours,
            play_minutes=play_minutes,
            food_grams=food_grams,
            description="Check-in giornaliero (tramite Dashboard)",
        )
        return redirect("dashboard")
    return redirect("dashboard")


@login_required
def lifetime_analytics(request, profile_id):
    """Visualizza il Centro Salute (Wellness Hub) e gestisce la Macro-Analisi IA."""
    profile = get_object_or_404(DogProfile, id=profile_id, owner=request.user)

    if request.method == "POST":
        # Genera nuovo report IA
        generate_lifetime_macro_analysis(profile)
        return redirect("lifetime_analytics", profile_id=profile.id)

    stats = profile.get_lifetime_stats()
    latest_macro = profile.macro_analyses.first()

    return render(
        request,
        "dog_profile/analytics.html",
        {"profile": profile, "stats": stats, "latest_macro": latest_macro},
    )


@login_required
def profile_dossier(request, profile_id):
    """Generates a complete clinical history dossier for the owner."""
    profile = get_object_or_404(DogProfile, id=profile_id, owner=request.user)

    events = list(profile.medical_events.all())
    analyses = list(profile.analyses.all())

    for e in events:
        e.sort_date = e.date
        e.item_type = "event"
    for a in analyses:
        e_date = getattr(a, "created_at", None)
        a.sort_date = e_date.date() if e_date else date.today()
        a.item_type = "analysis"

    timeline = events + analyses
    timeline.sort(key=lambda x: x.sort_date, reverse=True)

    whatsapp_text = f"🐾 *Dossier Medico: {profile.dog_name}* 🐾\n"
    whatsapp_text += f"Razza: {profile.breed or 'N/A'} | Età: {profile.get_age()} anni | Peso: {profile.weight or 'N/A'} kg\n\n"

    for item in timeline:
        if item.item_type == "event":
            whatsapp_text += (
                f"📅 {item.sort_date.strftime('%d/%m/%Y')} - [Evento] {item.title}\n"
            )
            if item.description:
                whatsapp_text += f"   Dettagli: {item.description}\n"
        elif item.item_type == "analysis":
            problem_title = (
                item.problem.title
                if hasattr(item, "problem") and item.problem
                else "Analisi Generale"
            )
            whatsapp_text += f"📅 {item.sort_date.strftime('%d/%m/%Y')} - [Analisi IA] {problem_title}\n"
            whatsapp_text += f"   Sintomi: {item.user_description}\n"
            if (
                hasattr(item, "get_result_display")
                and item.result
                and item.result != "pending"
            ):
                whatsapp_text += f"   Esito: {item.get_result_display()}\n"

    whatsapp_text += "\n*Generato via Vivere con il Cane*"

    import urllib.parse

    whatsapp_url = "https://wa.me/?text=" + urllib.parse.quote(whatsapp_text)

    return render(
        request,
        "dog_profile/dossier.html",
        {
            "profile": profile,
            "timeline": timeline,
            "whatsapp_text": whatsapp_text,
            "whatsapp_url": whatsapp_url,
        },
    )


@login_required
def export_dossier_pdf(request, profile_id):
    """Generates a professional clinical PDF dossier."""
    profile = get_object_or_404(DogProfile, id=profile_id, owner=request.user)
    events = list(profile.medical_events.all())
    analyses = list(profile.analyses.all())

    for e in events:
        e.sort_date = e.date
        e.item_type = "event"
    for a in analyses:
        e_date = getattr(a, "created_at", None)
        a.sort_date = e_date.date() if e_date else date.today()
        a.item_type = "analysis"

    timeline = events + analyses
    timeline.sort(key=lambda x: x.sort_date, reverse=True)

    template_path = "dog_profile/dossier_pdf.html"
    context = {"profile": profile, "timeline": timeline, "today": date.today()}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Dossier_{profile.dog_name}_{date.today()}.pdf"'
    )

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response


@login_required
def vet_request_start(request, dog_id):
    """Start a new veterinary request. analysis_id can be passed via GET."""
    dog = get_object_or_404(DogProfile, id=dog_id, owner=request.user)
    analysis = None
    problem_description = ""

    # Optional analysis_id from query string
    analysis_id = request.GET.get("analysis_id")
    if analysis_id:
        analysis = get_object_or_404(DogAnalysis, id=analysis_id, dog=dog)
        problem_description = analysis.user_description

    if request.method == "POST":
        # Create the request
        vet_request = VeterinaryRequest.objects.create(
            dog=dog,
            analysis=analysis,
            problem_description=request.POST.get(
                "problem_description", problem_description
            ),
            status="draft",
        )

        # Generate AI summary
        vet_request.ai_summary = generate_vet_summary(vet_request)
        vet_request.save()
        return redirect("vet_request_upload", dog_id=dog.id, request_id=vet_request.id)

    return render(
        request,
        "dog_profile/vet_request_start.html",
        {
            "dog": dog,
            "analysis": analysis,
            "problem_description": problem_description,
        },
    )


@login_required
def vet_request_upload(request, dog_id, request_id):
    """Step 2: Guided media collection based on AI-detected problem type."""
    vet_request = get_object_or_404(
        VeterinaryRequest, id=request_id, dog__owner=request.user, dog__id=dog_id
    )

    if request.method == "POST":
        # Handle media uploads
        for file in request.FILES.getlist("photos"):
            VeterinaryMedia.objects.create(
                request=vet_request,
                media_type="photo",
                file=file,
                caption=request.POST.get("photo_caption", ""),
                upload_order=VeterinaryMedia.objects.filter(
                    request=vet_request
                ).count(),
            )

        for file in request.FILES.getlist("videos"):
            VeterinaryMedia.objects.create(
                request=vet_request,
                media_type="video",
                file=file,
                caption=request.POST.get("video_caption", ""),
                upload_order=VeterinaryMedia.objects.filter(
                    request=vet_request
                ).count(),
            )

        vet_request.status = "ready"
        vet_request.save()
        return redirect("vet_request_review", dog_id=dog_id, request_id=vet_request.id)

    # AI suggests media types needed based on problem
    suggested_media = get_suggested_media_for_problem(
        vet_request.problem_description,
        vet_request.analysis.problem if vet_request.analysis else None,
    )

    return render(
        request,
        "dog_profile/vet_request_upload.html",
        {
            "vet_request": vet_request,
            "suggested_media": suggested_media,
            "existing_media": vet_request.media_files.all().order_by("upload_order"),
        },
    )


@login_required
def vet_request_review(request, dog_id, request_id):
    """Step 3: Review complete package before sending."""
    vet_request = get_object_or_404(
        VeterinaryRequest, id=request_id, dog__owner=request.user, dog__id=dog_id
    )

    if request.method == "POST":
        vet_request.sent_at = timezone.now()
        vet_request.status = "sent"
        vet_request.save()
        return redirect("vet_request_detail", dog_id=dog_id, request_id=vet_request.id)

    # Generate WhatsApp message or email body
    vet_request.vet_contact_info = generate_vet_contact_info(vet_request)

    return render(
        request,
        "dog_profile/vet_request_review.html",
        {
            "vet_request": vet_request,
        },
    )


@login_required
def vet_request_detail(request, dog_id, request_id):
    """View sent request details and vet contact options."""
    vet_request = get_object_or_404(
        VeterinaryRequest, id=request_id, dog__owner=request.user, dog__id=dog_id
    )
    return render(
        request,
        "dog_profile/vet_request_detail.html",
        {
            "vet_request": vet_request,
            "whatsapp_url": generate_whatsapp_url(vet_request),
        },
    )


@login_required
def vet_request_list(request):
    """List all veterinary requests for the user's dogs."""
    requests = VeterinaryRequest.objects.filter(dog__owner=request.user).order_by(
        "-created_at"
    )
    return render(
        request,
        "dog_profile/vet_request_list.html",
        {
            "requests": requests,
        },
    )


# Helper functions
def generate_vet_summary(vet_request):
    """Generate concise AI summary for veterinarian."""
    dog = vet_request.dog
    analysis = vet_request.analysis
    problem_desc = vet_request.problem_description

    summary = f"RIASSUNTO CLINICO - {dog.dog_name}\n"
    summary += f"Razza: {dog.breed or 'N/A'} | Età: {dog.get_age()} anni | Peso: {dog.weight or 'N/A'} kg\n"
    summary += f"Problema: {problem_desc[:200]}\n\n"

    if analysis and analysis.ai_response:
        summary += "ANALISI AI:\n"
        summary += analysis.ai_response[:500] + "...\n"

    # Add recent relevant medical events
    recent_events = dog.medical_events.order_by("-date")[:3]
    if recent_events:
        summary += "\nEVENTI MEDICI RECENTI:\n"
        for event in recent_events:
            summary += f"- {event.date.strftime('%d/%m/%Y')}: {event.title}\n"

    return summary


def get_suggested_media_for_problem(description, problem):
    """AI pre-filter: determine what media would be most useful."""
    desc_lower = description.lower()
    suggestions = []

    # Behavior problems
    if any(word in desc_lower for word in ["abbaia", "abbaio", "latra", "rumore"]):
        suggestions.append(
            {
                "type": "video",
                "label": "Video dell'abbaio (quando succede)",
                "help": "Registra un breve video (10-30 secondi) quando il cane abbaia, per mostrare il contesto.",
            }
        )

    if any(word in desc_lower for word in ["zoppica", "zampa", "gamba", "cammina"]):
        suggestions.append(
            {
                "type": "photo",
                "label": "Foto della zampa/zonna interessata",
                "help": "Scatta una foto chiara della zona sospetta, possibilmente da vicino.",
            }
        )
        suggestions.append(
            {
                "type": "video",
                "label": "Video del movimento",
                "help": "Registra il cane che cammina o corre per mostrare la zoppicatura.",
            }
        )

    if any(
        word in desc_lower
        for word in ["pelle", "forfora", "prurito", "gratta", "rossore"]
    ):
        suggestions.append(
            {
                "type": "photo",
                "label": "Foto della zona cutanea",
                "help": "Scatta una foto della pelle interessata, possibilmente ben illuminata.",
            }
        )
        suggestions.append(
            {
                "type": "video",
                "label": "Video del cane che si gratta",
                "help": "Registra il comportamento di grattamento.",
            }
        )

    if any(
        word in desc_lower for word in ["occhio", "occhi", "lacrima", "rossore occhi"]
    ):
        suggestions.append(
            {
                "type": "photo",
                "label": "Foto dell'occhio/o interessati",
                "help": "Scatta una foto frontale degli occhi per valutare arrossamento o secrezioni.",
            }
        )

    if any(word in desc_lower for word in ["morde", "morso", "aggressivo", "mordere"]):
        suggestions.append(
            {
                "type": "video",
                "label": "Video del comportamento",
                "help": "Registra il cane in una situazione che scatena il comportamento per mostrare i segnali pre-morso.",
            }
        )

    # Default suggestions
    if not suggestions:
        suggestions = [
            {
                "type": "photo",
                "label": "Foto generale del cane",
                "help": "Una foto del cane nella condizione normale.",
            },
            {
                "type": "photo",
                "label": "Foto della zona specifica",
                "help": "Se il problema è localizzato, scatta una foto dettagliata.",
            },
        ]

    return suggestions


def generate_vet_contact_info(vet_request):
    """Prepare contact info for vet (phone/email)."""
    info = {
        "dog_name": vet_request.dog.dog_name,
        "owner_name": vet_request.dog.owner.get_full_name()
        if vet_request.dog.owner
        else "Proprietario",
        "problem_summary": vet_request.problem_description[:100],
    }
    if vet_request.vet_name:
        info["vet_name"] = vet_request.vet_name
    if vet_request.vet_email:
        info["vet_email"] = vet_request.vet_email
    if vet_request.vet_phone:
        info["vet_phone"] = vet_request.vet_phone
    return info


def generate_whatsapp_url(vet_request):
    """Generate WhatsApp URL with structured message."""
    dog = vet_request.dog
    message = f"🐕 *Richiesta Consulto Veterinario*\n\n"
    message += f"*Cane:* {dog.dog_name}\n"
    message += f"*Razza:* {dog.breed or 'N/A'} | *Età:* {dog.get_age()} anni | *Peso:* {dog.weight or 'N/A'} kg\n"
    message += f"\n*Problema:* {vet_request.problem_description}\n\n"

    message += "*RIASSUNTO AI:*\n"
    message += vet_request.ai_summary[:500] + "...\n\n"

    message += (
        f"*Media allegati:* {vet_request.media_files.count()} file fotografici/video\n"
    )
    message += "*Storico eventi recenti inclusi nel pacchetto digitale.*\n\n"
    message += "Il proprietario ha caricato un caso clinico strutturato nell'app 'Vivere con il Cane'. Richiede consulto."

    import urllib.parse

    return "https://wa.me/?text=" + urllib.parse.quote(message)
