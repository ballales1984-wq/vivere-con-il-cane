# -*- coding: utf-8 -*-
from django.db import migrations


def copy_to_en(apps, schema_editor):
    Problem = apps.get_model("knowledge", "Problem")
    Cause = apps.get_model("knowledge", "Cause")
    Solution = apps.get_model("knowledge", "Solution")

    # Copy Problem fields
    for p in Problem.objects.all():
        updated = False
        if not p.title_en:
            p.title_en = p.title
            updated = True
        if not p.description_en:
            p.description_en = p.description
            updated = True
        if updated:
            p.save(update_fields=["title_en", "description_en"])

    # Copy Cause fields
    for c in Cause.objects.all():
        updated = False
        if not c.description_en:
            c.description_en = c.description
            updated = True
        if not c.notes_en:
            c.notes_en = c.notes
            updated = True
        if updated:
            c.save(update_fields=["description_en", "notes_en"])

    # Copy Solution fields
    for s in Solution.objects.all():
        updated = False
        if not s.title_en:
            s.title_en = s.title
            updated = True
        if not s.description_en:
            s.description_en = s.description
            updated = True
        if not s.time_needed_en:
            s.time_needed_en = s.time_needed
            updated = True
        if not s.warnings_en:
            s.warnings_en = s.warnings
            updated = True
        if updated:
            s.save(
                update_fields=[
                    "title_en",
                    "description_en",
                    "time_needed_en",
                    "warnings_en",
                ]
            )


class Migration(migrations.Migration):
    dependencies = [
        ("knowledge", "0003_cause_description_en_cause_notes_en_and_more"),
    ]
    operations = [
        migrations.RunPython(copy_to_en, reverse_code=migrations.RunPython.noop),
    ]
