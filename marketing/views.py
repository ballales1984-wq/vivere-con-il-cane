from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import NewsletterSubscriber
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def landing_page(request):
    """Landing page marketing WordPress."""
    return render(request, "marketing/landing_page.html")


def subscribe_newsletter(request):
    """Handles newsletter subscription via HTMX."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        # Validation
        if not email:
            return HttpResponse(
                '<p style="color: #ef4444; font-size: 0.9rem; margin-top: 10px;">Inserisci un indirizzo email.</p>'
            )

        try:
            validate_email(email)
        except ValidationError:
            return HttpResponse(
                '<p style="color: #ef4444; font-size: 0.9rem; margin-top: 10px;">Email non valida.</p>'
            )

        if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            return HttpResponse(
                '<p style="color: #10b981; font-size: 0.9rem; margin-top: 10px;">Sei già iscritto! Grazie comunque.</p>'
            )

        # Get or create (in case previously unsubscribed)
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={"is_active": True}
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()

        # Send confirmation email
        try:
            subject = "Benvenuto nella newsletter di Vivere con il Cane!"
            unsubscribe_url = request.build_absolute_uri(
                f"/unsubscribe/{subscriber.unsubscribe_token}/"
            )
            html_message = render_to_string(
                "marketing/email_welcome.html",
                {
                    "email": email,
                    "subscriber": subscriber,
                    "unsubscribe_url": unsubscribe_url,
                },
            )
            plain_message = strip_tags(html_message)
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=None,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            # Mark welcome as sent for follow-up sequence
            subscriber.welcome_sent = True
            from django.utils import timezone
            subscriber.last_email_at = timezone.now()
            subscriber.save()
        except Exception as e:
            print(f"Error sending welcome email to {email}: {e}")

        return render(request, "marketing/success.html", {"email": email})

    return HttpResponse("Metodo non permesso", status=405)


def unsubscribe_newsletter(request, token):
    """Unsubscribe from newsletter via token."""
    subscriber = get_object_or_404(NewsletterSubscriber, unsubscribe_token=token)
    subscriber.is_active = False
    subscriber.save()
    return render(
        request, "marketing/unsubscribe_success.html", {"email": subscriber.email}
    )
