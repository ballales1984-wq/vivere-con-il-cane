#!/usr/bin/env python
"""Extract translatable strings from Django templates."""

import re
from pathlib import Path

templates_dir = Path("templates")
strings = set()

for tpl in templates_dir.rglob("*.html"):
    try:
        content = tpl.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {tpl}: {e}")
        continue

    # {% trans "text" %}
    for m in re.finditer(r"{%\s*trans\s+\"([^\"]+)\"", content):
        strings.add(m.group(1))

    # {% blocktrans %}text{% endblocktrans %}
    for m in re.finditer(
        r"{%\s*blocktrans\s*%}(.*?){%\s*endblocktrans\s*%}", content, re.DOTALL
    ):
        txt = m.group(1).strip()
        if txt:
            # Handle variable interpolation like {{ dog.dog_name }}
            txt = re.sub(r"{{[^}]+}}", "", txt)
            txt = txt.strip()
            if txt:
                strings.add(txt)

print(f"Found {len(strings)} unique translatable strings:\n")
for s in sorted(strings):
    print(f"  {s!r}")
