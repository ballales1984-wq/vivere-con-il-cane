from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import Problem, Solution, BreedInsight, DogAnalysis
from dog_profile.models import DogProfile
from blog.models import BlogPost
import requests
import os


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
    
    related_articles = BlogPost.objects.filter(query, published=True).exclude(content="").distinct()[:3]

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
    """AI-powered problem analysis."""
    if request.method == "POST":
        dog_id = request.POST.get("dog_id")
        problem_id = request.POST.get("problem_id")
        description = request.POST.get("description", "").strip()

        if not description:
            # Redirect back to form if no description
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

        # Generate AI response
        ai_response = generate_ai_response(problem, description, dog, breed_info)

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
    }

    for keyword, slug in keyword_map.items():
        if keyword in text_lower:
            problem = Problem.objects.filter(slug=slug).first()
            if problem:
                return problem
    return None


def generate_ai_response(problem, description, dog, breed_info):
    """Generate AI response using Grok or OpenAI."""

    grok_key = os.environ.get("GROK_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    # Build context
    context = f"Problema descritto: {description}\n"

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
                            "content": "Sei un esperto di cani gentile e pratico.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                pass
        except Exception as err:
            pass

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
                        {"role": "system", "content": "Esperto di cani."},
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
    return f"""Basandomi sulle informazioni fornite:

1. **Causa più probabile**: Senza ulteriori dettagli, i problemi comportamentali sono spesso legati a mancanza di esercizio, routine inconsistente o bisogno di attenzione.

2. **Soluzioni suggerite**:
   - Stabilisci una routine quotidiana coerente
   - Aumenta l'esercizio fisico e mentale
   - Premia i comportamenti desiderati

3. **Consiglio**: Osserva il cane in diverse situazioni per identificare i trigger specifici.

4. **Quando rivolgerti a un professionista**: Se il problema persiste oltre 2-3 settimane nonostante gli allenamenti, consulta un educatore cinofilo o un Veterinario comportamentalista."""


def update_analysis_result(request, analysis_id):
    """Update the result of an analysis after user tries solution."""
    if request.method == "POST":
        analysis = get_object_or_404(DogAnalysis, id=analysis_id)
        analysis.result = request.POST.get("result", "pending")
        analysis.save()
        return redirect("dashboard")
    return JsonResponse({"error": "POST required"}, status=405)
