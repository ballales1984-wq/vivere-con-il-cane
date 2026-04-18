from django.shortcuts import render
from django.http import HttpResponse
from .models import NewsletterSubscriber
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def subscribe_newsletter(request):
    """Handles newsletter subscription via HTMX."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        
        # Validation
        if not email:
            return HttpResponse('<p style="color: #ef4444; font-size: 0.9rem; margin-top: 10px;">Inserisci un indirizzo email.</p>')
        
        try:
            validate_email(email)
        except ValidationError:
            return HttpResponse('<p style="color: #ef4444; font-size: 0.9rem; margin-top: 10px;">Email non valida.</p>')
            
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return HttpResponse('<p style="color: #10b981; font-size: 0.9rem; margin-top: 10px;">Sei già iscritto! Grazie comunque.</p>')
            
        # Create subscriber
        NewsletterSubscriber.objects.create(email=email)
        
        # Return success message (this replaces the form in HTMX)
        return render(request, "marketing/success.html", {"email": email})
        
    return HttpResponse("Metodo non permesso", status=405)
