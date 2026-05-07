from celery import shared_task
from django.core.management import call_command


@shared_task
def send_followup_emails():
    """Celery task che invoca il management command send_followups."""
    call_command("send_followups")
