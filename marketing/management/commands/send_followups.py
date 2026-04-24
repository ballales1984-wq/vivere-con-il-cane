from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from marketing.models import NewsletterSubscriber
from datetime import timedelta


class Command(BaseCommand):
    help = "Send automated onboarding follow-up emails to newsletter subscribers"

    def handle(self, *args, **options):
        now = timezone.now()
        
        # 1. Welcome Emails (immediate after subscription if not sent)
        to_welcome = NewsletterSubscriber.objects.filter(is_active=True, welcome_sent=False)
        for sub in to_welcome:
            self.send_onboarding_email(sub, step=0)
            sub.welcome_sent = True
            sub.last_email_at = now
            sub.save()
            self.stdout.write(f"Sent Welcome email to {sub.email}")

        # 2. Follow-up 1 (after 2 days)
        f1_subscribers = NewsletterSubscriber.objects.filter(
            is_active=True, 
            welcome_sent=True, 
            followup_step=0,
            last_email_at__lte=now - timedelta(days=2)
        )
        for sub in f1_subscribers:
            self.send_onboarding_email(sub, step=1)
            sub.followup_step = 1
            sub.last_email_at = now
            sub.save()
            self.stdout.write(f"Sent Follow-up #1 to {sub.email}")

        # 3. Follow-up 2 (after 5 days from last email)
        f2_subscribers = NewsletterSubscriber.objects.filter(
            is_active=True, 
            followup_step=1,
            last_email_at__lte=now - timedelta(days=3) # 2+3 = 5 days total
        )
        for sub in f2_subscribers:
            self.send_onboarding_email(sub, step=2)
            sub.followup_step = 2
            sub.last_email_at = now
            sub.save()
            self.stdout.write(f"Sent Follow-up #2 to {sub.email}")

    def send_onboarding_email(self, subscriber, step):
        subjects = [
            "Benvenuto in Vivere con il Cane! 🐕",
            "Come usare al meglio l'IA per il tuo cane 🧠",
            "Monitora la salute del tuo compagno 📊",
        ]
        
        templates = [
            "marketing/emails/welcome.html",
            "marketing/emails/followup_1.html",
            "marketing/emails/followup_2.html",
        ]
        
        subject = subjects[step]
        template = templates[step]
        
        # In a real app, we would render a template
        # html_message = render_to_string(template, {'subscriber': subscriber})
        
        # Simplified for now (console output in dev)
        message = f"Ciao! Questo è lo step {step} della nostra guida onboarding per {subscriber.email}."
        
        send_mail(
            subject,
            message,
            "newsletter@vivereconilcane.com",
            [subscriber.email],
            fail_silently=True,
        )
