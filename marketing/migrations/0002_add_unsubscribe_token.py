# -*- coding: utf-8 -*-
import uuid
from django.db import migrations, models


def add_unsubscribe_tokens(apps, schema_editor):
    NewsletterSubscriber = apps.get_model("marketing", "NewsletterSubscriber")
    for subscriber in NewsletterSubscriber.objects.all():
        if not subscriber.unsubscribe_token:
            subscriber.unsubscribe_token = uuid.uuid4()
            subscriber.save(update_fields=["unsubscribe_token"])


class Migration(migrations.Migration):
    dependencies = [
        ("marketing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="newslettersubscriber",
            name="unsubscribe_token",
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.RunPython(
            add_unsubscribe_tokens, reverse_code=migrations.RunPython.noop
        ),
    ]
