from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.cache import cache
from .models import Problem, Solution, BreedInsight, DogAnalysis, VeterinaryDocument, LifetimeMacroAnalysis
from dog_profile.models import DogProfile
from blog.models import BlogPost
import requests
import os
from xhtml2pdf import pisa
from django.template.loader import get_template


def problem_list(request):
    """List all problems."""
    problems = Problem.objects.all()
    return render(request, "knowledge/problem_list.html", {"problems": problems})


def problem_detail(request, slug):
    """Show problem with causes and solutions and related articles."""
    problem = get_object_or_404(Problem, slug=slug)

    # Find related articles based on problem keywords
    keywords = problem.slug.split("-")
    # Filter out common short words
    keywords = [k for k in keywords if len(k) > 2]

    from django.db.models import Q

    query = Q()
    for kw in keywords:
        query |= Q(slug__icontains=kw) | Q(title__icontains=kw)

    related_articles = (
        BlogPost.objects.filter(query, published=True)
        .exclude(content="")
        .distinct()[:3]
    )

    return render(
        request,
        "knowledge/problem_detail.html",
        {
            "problem": problem,
            "causes": problem.causes.all(),
            "solutions": problem.solutions.all(),
            "related_articles": related_articles,
        },
    )


def breed_list(request):
    """List all breed insights."""
    breeds = BreedInsight.objects.all()
    return render(request, "knowledge/breed_list.html", {"breeds": breeds})


def breed_detail(request, slug):
    """Show breed details with related problems."""
    breed = get_object_or_404(BreedInsight, slug=slug)

    # Find related problems based on breed common_problems keywords
    related_problems = []
    common = breed.common_problems.lower() if breed.common_problems else ""

    if "abbaio" in common or "ansia" in common:
        related_problems.extend(Problem.objects.filter(slug="abbaia-troppo"))
    if "tir" in common or "guinzaglio" in common:
        related_problems.extend(Problem.objects.filter(slug="tira-guinzaglio"))
    if "separazione" in common or "ansia" in common:
        related_problems.extend(Problem.objects.filter(slug="ansia-separazione"))
    if "distruzione" in common or "noia" in common:
        related_problems.extend(Problem.objects.filter(slug="distrugge-casa"))
    if "eccitazione" in common:
        related_problems.extend(Problem.objects.filter(slug="eccitazione-eccessiva"))

    # Remove duplicates and limit to 4
    related_problems = list(dict.fromkeys(related_problems))[:4]

    return render(
        request,
        "knowledge/breed_detail.html",
        {"breed": breed, "related_problems": related_problems},
    )


def analyze_problem(request):
    """AI-powered problem analysis with IP-based rate limiting."""
    if request.method == "POST":
        # --- Rate Limiting ---
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "unknown"))
        ip = ip.split(",")[0].strip()
        rate_key = f"analyze_rate:{ip}"
        rate_limit = getattr(settings, "ANALYZE_RATE_LIMIT", 10)
        rate_window = getattr(settings, "ANALYZE_RATE_WINDOW", 3600)
        current_count = cache.get(rate_key, 0)
        if current_count >= rate_limit:
            dogs = DogProfile.objects.filter(owner=request.user) if request.user.is_authenticated else []
            problems = Problem.objects.all()
            return render(
                request,
                "knowledge/analyze_form.html",
                {
                    "dogs": dogs,
                    "problems": problems,
                    "error": "Hai raggiunto il limite di analisi orarie. Riprova tra poco.",
                },
            )
        cache.set(rate_key, current_count + 1, rate_window)
        # --- End Rate Limiting ---

        dog_id = request.POST.get("dog_id")
        problem_id = request.POST.get("problem_id")
        description = request.POST.get("description", "").strip()

        if not description:
            dogs = DogProfile.objects.all()
            problems = Problem.objects.all()
            return render(
                request,
                "knowledge/analyze_form.html",
                {
                    "dogs": dogs,
                    "problems": problems,
                    "error": "Descrivi il problema del tuo cane.",
                },
            )

        dog = None
        problem = None

        if dog_id:
            dog = DogProfile.objects.filter(id=dog_id).first()
        if problem_id:
            problem = Problem.objects.filter(id=problem_id).first()

        # Auto-detect problem from description if not selected
        if not problem and description:
            problem = auto_detect_problem(description)

        # Get breed insights if available
        breed_info = None
        if dog and dog.breed:
            breed_info = BreedInsight.objects.filter(breed__icontains=dog.breed).first()

        # Check language preference
        lang = request.COOKIES.get("app_lang", "it")

        # Generate AI response
        ai_response = generate_ai_response(problem, description, dog, breed_info, lang)

        # Find suggested articles based on description and detected problem
        suggested_articles = get_related_articles(description, problem)

        # Save analysis only if dog is available
        analysis = None
        if dog:
            analysis = DogAnalysis.objects.create(
                dog=dog,
                problem=problem,
                user_description=description,
                ai_response=ai_response,
            )

        return render(
            request,
            "knowledge/analysis_result.html",
            {
                "analysis": analysis,
                "dog": dog,
                "ai_response": ai_response,
                "problem": problem,
                "description": description,
                "suggested_articles": suggested_articles,
            },
        )

    # GET - show form, pre-fill description from homepage if provided
    dogs = DogProfile.objects.all()
    problems = Problem.objects.all()
    prefill = request.GET.get("q", "")
    return render(
        request,
        "knowledge/analyze_form.html",
        {
            "dogs": dogs,
            "problems": problems,
            "prefill": prefill,
        },
    )


def auto_detect_problem(text):
    """Auto-detect problem from user description text."""
    text_lower = text.lower()
    keyword_map = {
        # Existing problems
        "abbaia": "abbaia-troppo",
        "abbaio": "abbaia-troppo",
        "tira": "tira-guinzaglio",
        "guinzaglio": "tira-guinzaglio",
        "ansia": "ansia-separazione",
        "separazione": "ansia-separazione",
        "solo": "ansia-separazione",
        "morde": "cane-morde",
        "morso": "cane-morde",
        "mordere": "cane-morde",
        "mangia": "non-mangia",
        "appetito": "non-mangia",
        "cibo": "non-mangia",
        "paura": "paura-rumori",
        "temporale": "paura-rumori",
        "tuono": "paura-rumori",
        "petardi": "paura-rumori",
        "salta": "salta-addosso",
        "addosso": "salta-addosso",
        "richiamo": "non-richiamo",
        "viene": "non-richiamo",
        "distrugge": "distrugge-casa",
        "mastica": "distrugge-casa",
        "eccitato": "eccitazione-eccessiva",
        "eccitazione": "eccitazione-eccessiva",
        # New problems
        "reattivo": "reattivita-guinzaglio",
        "reattivita": "reattivita-guinzaglio",
        "ringhia": "reattivita-guinzaglio",
        "aggressivo": "reattivita-guinzaglio",
        "sassi": "mangia-tutto-terra",
        "terra": "mangia-tutto-terra",
        "raccoglie": "mangia-tutto-terra",
        "inghiotte": "mangia-tutto-terra",
        "pica": "mangia-tutto-terra",
        "estraneo": "paura-estranei",
        "persone": "paura-estranei",
        "estranei": "paura-estranei",
        "feci": "mangia-feci",
        "coprofagia": "mangia-feci",
        "scava": "scava-giardino",
        "buche": "scava-giardino",
        "giardino": "scava-giardino",
        "veterinario": "paura-veterinario",
        "clinica": "paura-veterinario",
        "visita": "paura-veterinario",
        "auto": "mal-auto",
        "macchina": "mal-auto",
        "vomita": "mal-auto",
        "viaggi": "mal-auto",
        "lecca": "lecca-zampe-ossessivo",
        "zampe": "lecca-zampe-ossessivo",
        "prurito": "lecca-zampe-ossessivo",
        "distrae": "scarsa-attenzione",
        "distrazione": "scarsa-attenzione",
        "concentrazione": "scarsa-attenzione",
        "attenzione": "scarsa-attenzione",
    }

    for keyword, slug in keyword_map.items():
        if keyword in text_lower:
            problem = Problem.objects.filter(slug=slug).first()
            if problem:
                return problem
    return None


def get_related_articles(text, problem=None):
    """Find related blog posts based on problem keywords or description."""
    from django.db.models import Q

    keywords = []
    if problem:
        # Use problem slug keywords
        keywords.extend(problem.slug.split("-"))
    
    # Extract some long words from description as potential keywords
    desc_words = [w.lower() for w in text.split() if len(w) > 4]
    keywords.extend(desc_words[:3])  # Take a few

    # Filter keywords (exclude common ones)
    keywords = [k for k in set(keywords) if len(k) > 3]

    if not keywords:
        return BlogPost.objects.filter(published=True).order_by("-created_at")[:2]

    query = Q()
    for kw in keywords:
        query |= Q(title__icontains=kw) | Q(slug__icontains=kw) | Q(content__icontains=kw)

    return (
        BlogPost.objects.filter(query, published=True)
        .distinct()
        .order_by("-importance", "-created_at")[:2]
    )


import urllib.parse


def query_external_vet_db(description, breed=None):
    """
    Interroga il database pubblico OpenFDA (Veterinary Adverse Events)
    cercando corrispondenze con i sintomi descritti per ottenere contesto medico aggiuntivo.
    """
    try:
        # Extract keywords for better search
        symptoms_map = {
            "vomito": "vomiting", "diarrea": "diarrhea", "zoppica": "lameness",
            "prurito": "itching", "tosse": "cough", "febbre": "fever",
            "letargia": "lethargy", "sangue": "blood", "pelo": "alopecia"
        }
        
        search_term = None
        for it_kw, en_kw in symptoms_map.items():
            if it_kw in description.lower():
                search_term = en_kw
                break
        
        if not search_term:
            # Fallback to the first long word used as is (OpenFDA is primarily English)
            words = [w for w in description.split() if len(w) > 5]
            if not words: return ""
            search_term = words[0]

        # Build the query for dogs
        query = 'animal.species:"Dog"'
        if breed:
            # Pulisci il nome della razza
            safe_breed = breed.split()[0]
            query += f' AND animal.breed.breed_name:"{safe_breed}"'

        # Add the symptom
        query += f' AND (reaction.reaction_pt:"{search_term}" OR health_assessment_prior_to_exposure.condition:"{search_term}")'

        url = f"https://api.fda.gov/animalandveterinary/event.json?search={urllib.parse.quote(query)}&limit=2"

        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                ext_context = (
                    "\n[DATI OPEN-FDA: REAZIONI AVVERSE E CASI CLINICI SIMILI]\n"
                )
                for idx, result in enumerate(data["results"]):
                    animal = result.get("animal", {})
                    drugs = result.get("drug", [])
                    reactions = result.get("reaction", [])

                    drug_names = [
                        d.get("active_ingredients", [{"name": "Sconosciuto"}])[0].get(
                            "name", "Sconosciuto"
                        )
                        for d in drugs
                    ]
                    reaction_names = [r.get("reaction_pt", "") for r in reactions]

                    ext_context += f"- Caso #{idx + 1}: Cane ({animal.get('breed', {}).get('breed_name', 'Meticcio')}), "
                    ext_context += f"Farmaci assunti: {', '.join(drug_names)}. "
                    ext_context += (
                        f"Reazioni documentate: {', '.join(reaction_names)}.\n"
                    )
                ext_context += "[/DATI OPEN-FDA]\n\n"
                return ext_context
    except Exception as e:
        import logging

        logging.warning(f"Errore ricerca OpenFDA: {e}")
        return ""
    return ""


def generate_ai_response(problem, description, dog, breed_info, lang="it"):
    """Generate AI response using Grok or OpenAI, in the specified language."""

    grok_key = os.environ.get("GROK_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    # Retrieve internal veterinary knowledge base for context
    vet_docs = VeterinaryDocument.objects.filter(is_active=True)
    vet_context = ""
    if vet_docs.exists():
        # A simple keyword match or just include all if small (simplified RAG)
        desc_lower = description.lower()
        matched_docs = []
        for doc in vet_docs:
            if any(k.strip().lower() in desc_lower for k in doc.keywords.split(",")):
                matched_docs.append(doc)

        if matched_docs:
            vet_context = "\n[DATABASE VETERINARIO INTERNO]\n"
            for doc in matched_docs:
                vet_context += f"Documento: {doc.title}\n{doc.content}\n"
            vet_context += "[/DATABASE VETERINARIO INTERNO]\n\n"

    # Build context
    context = f"Problema descritto: {description}\n"
    if vet_context:
        context = vet_context + context

    # 3. Interroga database esterno OpenFDA per ampliare contesto clinico
    breed_name = dog.breed if dog and dog.breed else None
    fda_context = query_external_vet_db(description, breed_name)
    if fda_context:
        context += fda_context

    if dog:
        context += f"Cane: {dog.dog_name}"
        if dog.breed:
            context += f", razza: {dog.breed}"
        if dog.birth_date:
            context += f", età: {dog.get_age()} anni"
        if dog.weight:
            context += f", peso: {dog.weight} kg"
        context += "\n"

    if breed_info:
        context += f"Razza {dog.breed} - caratteristiche: {breed_info.traits}\n"
        context += f"Problemi comuni: {breed_info.common_problems}\n"

    # Add recent medical events if dog is available
    if dog:
        recent_events = dog.medical_events.order_by("-date")[:7]
        if recent_events:
            context += "\nEventi medici recenti:\n"
            for event in recent_events:
                context += f"- {event.date.strftime('%d/%m/%Y')}: {event.title} ({event.get_event_type_display()})\n"

    # Add previous analyses context if dog is available
    if dog:
        previous_analyses = DogAnalysis.objects.filter(dog=dog).order_by("-created_at")[
            :3
        ]
        if previous_analyses:
            context += "\nStorico analisi precedenti per questo cane:\n"
            for i, prev in enumerate(previous_analyses, 1):
                context += f"{i}. {prev.created_at.strftime('%d/%m/%Y')}: {prev.user_description[:80]}..."
                if prev.result and prev.result != "pending":
                    context += f" - Esito: {prev.result}\n"
                else:
                    context += "\n"

    if problem:
        context += f"Problema noto: {problem.title}\n"
        causes = [c.description for c in problem.causes.all()]
        if causes:
            context += f"Possibili cause: {', '.join(causes)}\n"
        solutions = [(s.title, s.description) for s in problem.solutions.all()[:3]]
        if solutions:
            context += "Soluzioni:\n"
            for title, desc in solutions:
                context += f"- {title}: {desc[:100]}...\n"

    system_msg = "Sei un esperto di cani gentile e pratico."
    if lang == "en":
        prompt = f"""You are an expert in canine behavior and wellness. Analyze this problem and provide a practical and personalized response based on the context.

{context}

Provide:
1. most likely cause
2. 2-3 practical solutions
3. a specific tip for this dog
4. when to consult a veterinarian

Answer in English clearly and practically."""
        system_msg = "You are a kind and practical dog expert."
    else:
        prompt = f"""Sei un esperto di comportamento e benessere canino. Analizza questo problema e fornisci una risposta pratica e personalizzata.

{context}

Fornisci:
1. causa più probabile
2. 2-3 soluzioni pratiche
3. un consiglio specifico per questo cane
4. quando consultare un veterinario

Rispondi in italiano in modo chiaro e pratico."""

    # Try Groq (Grok via Groq)
    if grok_key and len(grok_key) > 20:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {grok_key}",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": system_msg,
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                import logging

                logging.warning(
                    f"[AI] Groq API error {response.status_code}: {response.text[:200]}"
                )
        except Exception as err:
            import logging

            logging.warning(f"[AI] Groq exception: {err}")

    # Fallback to OpenAI
    if openai_key and len(openai_key) > 20:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_key}",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except:
            pass

    # No API key - return generic response
    if lang == "en":
        return f"""Based on the information provided:

1. **Most likely cause**: Without further details, behavioral problems are often linked to lack of exercise, inconsistent routine, or a need for attention.

2. **Suggested solutions**:
   - Establish a consistent daily routine
   - Increase physical and mental exercise
   - Reward desired behaviors

3. **Tip**: Observe the dog in different situations to identify specific triggers.

4. **When to see a professional**: If the problem persists beyond 2-3 weeks despite training, consult a dog trainer or a veterinary behaviorist."""
    else:
        return f"""Basandomi sulle informazioni fornite:

1. **Causa più probabile**: Senza ulteriori dettagli, i problemi comportamentali sono spesso legati a mancanza di esercizio, routine inconsistente o bisogno di attenzione.

2. **Soluzioni suggerite**:
   - Stabilisci una routine quotidiana coerente
   - Aumenta l'esercizio fisico e mentale
   - Premia i comportamenti desiderati

3. **Consiglio**: Osserva il cane in diverse situazioni per identificare i trigger specifici.

4. **Quando rivolgerti a un professionista**: Se il problema persiste oltre 2-3 settimane nonostante gli allenamenti, consulta un educatore cinofilo o un Veterinario comportamentalista."""


def analysis_history(request, dog_id):
    """Show previous analyses for a specific dog."""
    dog = get_object_or_404(DogProfile, id=dog_id)
    analyses = DogAnalysis.objects.filter(dog=dog).order_by("-created_at")
    return render(
        request, "knowledge/analysis_history.html", {"dog": dog, "analyses": analyses}
    )


def update_analysis_result(request, analysis_id):
    """Update the result of an analysis after user tries solution."""
    if request.method == "POST":
        analysis = get_object_or_404(DogAnalysis, id=analysis_id)
        analysis.result = request.POST.get("result", "pending")
        analysis.save()
        return redirect("dashboard")
    return JsonResponse({"error": "POST required"}, status=405)


def download_analysis_pdf(request, analysis_id):
    """Generates a PDF report for a specific AI analysis."""
    analysis = get_object_or_404(DogAnalysis, id=analysis_id)
    
    # Ensure the user has permission to download this analysis
    if analysis.dog and request.user.is_authenticated and analysis.dog.owner != request.user:
        return HttpResponse("Non sei autorizzato a scaricare questo referto.", status=403)
        
    template_path = "knowledge/analysis_pdf.html"
    from datetime import date
    context = {"analysis": analysis, "dog": analysis.dog, "today": date.today()}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type="application/pdf")
    filename = f"Referto_IA_{analysis.dog.dog_name if analysis.dog else 'Generico'}_{analysis.created_at.date()}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Si è verificato un errore durante la generazione del PDF <pre>" + html + "</pre>")
    return response


def generate_lifetime_macro_analysis(profile):
    """
    Super-Prompt AI: Prende il 'Digital Twin' del cane (storico vita, medie)
    e genera un referto macrostrutturato permanente.
    """
    import json
    import markdown
    
    stats = profile.get_lifetime_stats()
    
    # Costruzione del "Context Snapshot"
    context_data = {
        "dog_name": profile.dog_name,
        "breed": profile.breed,
        "age": profile.get_age(),
        "weight": str(profile.weight) if profile.weight else "N/D",
        "stats": stats,
        "medical_events": list(profile.medical_events.values('date', 'event_type', 'title', 'description')[:15]) # ultimi 15 eventi
    }
    
    system_msg = """Sei un Esperto Veterinario Analista e Comportamentalista.
Il tuo compito è leggere i dati aggregati di TUTTA LA VITA di questo cane e generare un Report Macro (Check-up Totale).
Devi restituire SOLO codice HTML puro (senza markdown ```html), formattato elegantemente, diviso esattamente in queste 4 sezioni:
<h2>1. Valutazione Stile di Vita</h2> (Analizza sonno, passeggiate, gioco basandoti sulle medie)
<h2>2. Correlazioni Clinico-Comportamentali</h2> (Trova schemi tra eventi medici e problemi)
<h2>3. Segnali d'Allarme (Red Flags)</h2> (Anomalie o carenze rispetto agli standard di razza)
<h2>4. Protocollo Benessere Prossimi 3 Mesi</h2> (Azioni a lungo termine)"""

    prompt = f"Analizza questo Gemello Digitale (Dati di Vita):\n{json.dumps(context_data, indent=2, default=str)}"

    api_key = os.environ.get("GROK_API_KEY", "")
    html_report = "<p>Impossibile contattare l'Intelligenza Artificiale al momento.</p>"
    
    if api_key and len(api_key) > 20:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt}
                    ],
                },
                timeout=45, # This is a long generation
            )
            if response.status_code == 200:
                html_report = response.json()["choices"][0]["message"]["content"]
                html_report = html_report.replace("```html", "").replace("```", "").strip()
            else:
                html_report += f"<p>Errore API: {response.status_code}</p>"
        except Exception as e:
            html_report += f"<p>Eccezione: {str(e)}</p>"
            
    # Save the permanent macro analysis
    macro = LifetimeMacroAnalysis.objects.create(
        dog=profile,
        context_snapshot=context_data,
        ai_report_html=html_report
    )
    return macro


def learning_hub(request):
    """Visualizza l'Hub Didattico con risorse accademiche e scientifiche."""
    return render(request, "knowledge/learning_hub.html")
