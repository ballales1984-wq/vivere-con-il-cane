from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import math


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
    tools = [
        {
            "name": "Calcolatore Cibo",
            "url": "food_calculator",
            "icon": "🍖",
            "desc": "Calcola le porzioni giornaliere",
        },
        {
            "name": "Età Umana",
            "url": "age_calculator",
            "icon": "🎂",
            "desc": "Conosci l'età del cane in anni umani",
        },
        {
            "name": "Quiz Linguaggio",
            "url": "dog_quiz",
            "icon": "🧠",
            "desc": "Testa la tua conoscenza",
        },
    ]
    return render(request, "canine_tools/index.html", {"tools": tools})


def privacy_policy(request):
    return render(request, "canine_tools/privacy_policy.html")


def terms_of_service(request):
    return render(request, "canine_tools/terms_of_service.html")


def cookie_policy(request):
    return render(request, "canine_tools/cookie_policy.html")
