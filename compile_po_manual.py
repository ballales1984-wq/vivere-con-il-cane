#!/usr/bin/env python
"""
PO to MO compiler with proper GNU gettext format support.
Handles multi-line strings correctly.
"""

import re
import os
import sys
import struct


def escape(s):
    """Escape special characters in a string for PO format"""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def unescape(s):
    """Unescape a PO string"""
    return s.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")


def parse_po_file(filepath):
    """Parse a PO file and return a dictionary of translations"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove header block if present
    if content.startswith('msgid ""'):
        # Find the end of header
        first_end = content.find("\n\nmsgstr ")
        if first_end != -1:
            content = content[first_end + 2 :]

    messages = {}

    # Simple parsing - match msgid/msgstr pairs
    # This handles multi-line strings
    msgid = None
    msgstr = None
    in_msgid = False
    in_msgstr = False

    for line in content.split("\n"):
        line = line.strip()

        if line.startswith('msgid "') and not line.startswith("msgstr"):
            if msgid is not None and msgstr is not None and msgid:
                messages[msgid] = msgstr

            # Extract msgid value
            s = line[7:]
            msgid = unescape(s.strip('"'))
            in_msgid = True
            in_msgstr = False
        elif line.startswith('msgstr "'):
            if msgid is not None:
                # Extract msgstr value
                s = line[8:]
                msgstr = unescape(s.strip('"'))
                in_msgid = False
                in_msgstr = True
        elif line.startswith('"') and line.endswith('"'):
            # Continuation of previous string
            s = line.strip('"')
            if in_msgid:
                msgid += unescape(s)
            elif in_msgstr:
                msgstr += unescape(s)

    # Add last entry
    if msgid and msgstr:
        messages[msgid] = msgstr

    return messages


def build_mo_file(messages, output_path):
    """Build a MO file from a messages dictionary"""
    # Get sorted keys
    keys = sorted(messages.keys())

    # Build id and str tables
    ids = b""
    strs = b""
    offsets = []

    for key in keys:
        key_bytes = key.encode("utf-8")
        value_bytes = messages[key].encode("utf-8")
        offsets.append((len(ids), len(key_bytes), len(strs), len(value_bytes)))
        ids += key_bytes + b"\0"
        strs += value_bytes + b"\0"

    # Calculate offsets
    keystart = 7 * 4  # header is 7 32-bit ints
    valstart = keystart + len(keys) * 8

    # MO file header (little-endian)
    header = struct.pack(
        "<Iiiii",
        0x950412DE,  # Magic
        0,  # Version
        len(keys),  # Number of strings
        keystart,  # Start of index table
        valstart,  # Start of translation table
    )

    # Build index tables
    id_index = b""
    str_index = b""
    current_id_offset = valstart + len(keys) * 8
    current_str_offset = current_id_offset + len(ids)

    for id_off, id_len, str_off, str_len in offsets:
        id_index += struct.pack("<ii", id_len, current_id_offset + id_off)
        str_index += struct.pack("<ii", str_len, current_str_offset + str_off)

    # Write the MO file
    with open(output_path, "wb") as f:
        f.write(header)
        f.write(id_index)
        f.write(str_index)
        f.write(ids)
        f.write(strs)


def main():
    locale_dir = os.path.join(os.path.dirname(__file__), "locale", "en", "LC_MESSAGES")
    po_file = os.path.join(locale_dir, "django.po")
    mo_file = os.path.join(locale_dir, "django.mo")

    if not os.path.exists(po_file):
        print(f"Error: {po_file} not found", file=sys.stderr)
        sys.exit(1)

    messages = parse_po_file(po_file)
    print(f"Parsed {len(messages)} messages")

    build_mo_file(messages, mo_file)
    print(f"Compiled to {mo_file}")


if __name__ == "__main__":
    main()
