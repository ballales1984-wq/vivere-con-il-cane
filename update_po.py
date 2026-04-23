#!/usr/bin/env python
"""Aggiorna i file .po con tutte le stringhe mancanti dai template."""

import re
from pathlib import Path
import polib

templates_dir = Path("templates")
all_strings = set()

for tpl in templates_dir.rglob("*.html"):
    try:
        content = tpl.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {tpl}: {e}")
        continue

    # {% trans "text" %}
    for m in re.finditer(r'{%\s*trans\s+"([^"]+)"', content):
        all_strings.add(m.group(1))

    # {% blocktrans %}text{% endblocktrans %}
    for m in re.finditer(
        r"{%\s*blocktrans\s*%}(.*?){%\s*endblocktrans\s*%}", content, re.DOTALL
    ):
        txt = m.group(1).strip()
        if txt:
            all_strings.add(txt)

print(f"Found {len(all_strings)} unique msgids")

# Update Italian PO (should already have most)
po_it = polib.pofile("locale/it/LC_MESSAGES/django.po")
existing_it = {e.msgid for e in po_it}
missing_it = all_strings - existing_it
print(f"\nItalian: missing {len(missing_it)} entries")
for msgid in sorted(missing_it):
    entry = polib.POEntry(
        msgid=msgid, msgstr=msgid
    )  # source=Italian, translation = same
    po_it.append(entry)
po_it.save("locale/it/LC_MESSAGES/django.po")
print(f"Updated Italian PO with {len(missing_it)} new entries")

# Update English PO (needs translations)
po_en = polib.pofile("locale/en/LC_MESSAGES/django.po")
existing_en = {e.msgid for e in po_en}
missing_en = all_strings - existing_en
print(f"\nEnglish: missing {len(missing_en)} entries")
for msgid in sorted(missing_en):
    entry = polib.POEntry(msgid=msgid, msgstr="")  # empty translation to be filled
    po_en.append(entry)
po_en.save("locale/en/LC_MESSAGES/django.po")
print(f"Updated English PO with {len(missing_en)} new entries")
