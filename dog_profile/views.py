from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import DogProfile, HealthEvent, DailyLog
from knowledge.models import DogAnalysis
from datetime import date


def profile_list(request):
    """List all dog profiles."""
    profiles = DogProfile.objects.all()
    return render(request, "dog_profile/list.html", {"profiles": profiles})


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
            name=name,
            dog_name=dog_name,
            breed=breed,
            birth_date=birth_date or None,
            weight=weight or None,
            gender=gender,
        )
        return redirect("profile_detail", profile_id=profile.id)

    return render(request, "dog_profile/form.html", {})


def profile_detail(request, profile_id):
    """View dog profile with events and daily logs."""
    profile = get_object_or_404(DogProfile, id=profile_id)
    events = profile.events.all()[:10]
    logs = profile.daily_logs.all()[:7]

    return render(
        request,
        "dog_profile/detail.html",
        {
            "profile": profile,
            "events": events,
            "logs": logs,
        },
    )


def profile_add_event(request, profile_id):
    """Add health event to profile."""
    profile = get_object_or_404(DogProfile, id=profile_id)

    if request.method == "POST":
        HealthEvent.objects.create(
            dog=profile,
            event_type=request.POST.get("event_type"),
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            date=request.POST.get("date") or date.today(),
        )
        return redirect("profile_detail", profile_id=profile.id)

    return render(request, "dog_profile/event_form.html", {"profile": profile})


def profile_add_log(request, profile_id):
    """Add daily log to profile."""
    profile = get_object_or_404(DogProfile, id=profile_id)

    if request.method == "POST":
        DailyLog.objects.create(
            dog=profile,
            date=request.POST.get("date") or date.today(),
            sleep_hours=request.POST.get("sleep_hours") or 0,
            play_minutes=request.POST.get("play_minutes") or 0,
            walk_minutes=request.POST.get("walk_minutes") or 0,
            food_grams=request.POST.get("food_grams") or 0,
        )
        return redirect("profile_detail", profile_id=profile.id)

    return render(request, "dog_profile/log_form.html", {"profile": profile})


def my_dog(request):
    """Quick view for the first dog profile."""
    profile = DogProfile.objects.first()
    if not profile:
        return redirect("profile_new")
    return redirect("profile_detail", profile_id=profile.id)


def dashboard(request):
    """Main dashboard - unified view for all dog's data."""
    profiles = list(DogProfile.objects.all())

    # Attach analyses to each profile
    for profile in profiles:
        profile.recent_analyses = list(profile.analyses.all()[:5])

    return render(request, "dog_profile/dashboard.html", {"profiles": profiles})
