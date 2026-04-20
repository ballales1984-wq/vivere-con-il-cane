#!/usr/bin/env python
"""PO to MO compiler - fixed offset calculation."""

import os
import struct
import polib


def compile_mo():
    po_file = "locale/en/LC_MESSAGES/django.po"
    mo_file = "locale/en/LC_MESSAGES/django.mo"

    po = polib.pofile(po_file)
    print(f"Parsed {len(po)} entries")

    # Extract entries that have translations - keep original order
    entries = [(e.msgid, e.msgstr) for e in po if e.msgid and e.msgstr]
    print(f"Found {len(entries)} translations")

    nstrings = len(entries)

    # Build strings with null terminator
    orig_strings = [e[0].encode("utf-8") + b"\x00" for e in entries]
    trans_strings = [e[1].encode("utf-8") + b"\x00" for e in entries]

    # Calculate total sizes for offset calculation
    orig_data_size = sum(len(s) for s in orig_strings)
    trans_data_size = sum(len(s) for s in trans_strings)

    # Calculate offsets
    header_size = 28
    index_size = nstrings * 8

    orig_index_offset = header_size
    trans_index_offset = header_size + index_size

    # Data sections start after both index tables
    orig_data_offset = header_size + index_size * 2
    trans_data_offset = orig_data_offset + orig_data_size

    print(f"Header: {header_size}, Index: {index_size}")
    print(f"Orig data: offset={orig_data_offset}, size={orig_data_size}")
    print(f"Trans data: offset={trans_data_offset}, size={trans_data_size}")

    # Build header (little-endian)
    header = struct.pack(
        "<IIIIIII",
        0x950412DE,  # Magic
        0,  # Version
        nstrings,
        orig_index_offset,
        trans_index_offset,
        0,  # Hash size
        0,  # Hash offset
    )

    # Build index tables with cumulative offsets
    orig_index = b""
    trans_index = b""

    current_orig = 0
    current_trans = 0
    for i in range(nstrings):
        orig_index += struct.pack(
            "<II", len(orig_strings[i]), orig_data_offset + current_orig
        )
        current_orig += len(orig_strings[i])

        trans_index += struct.pack(
            "<II", len(trans_strings[i]), trans_data_offset + current_trans
        )
        current_trans += len(trans_strings[i])

    # Write MO file
    with open(mo_file, "wb") as f:
        f.write(header)
        f.write(orig_index)
        f.write(trans_index)
        f.write(b"".join(orig_strings))
        f.write(b"".join(trans_strings))

    print(f"Compiled to {mo_file}")

    # Verify
    with open(mo_file, "rb") as f:
        data = f.read()

    magic = struct.unpack("<I", data[0:4])[0]
    n = struct.unpack("<I", data[8:12])[0]

    # Read first entry
    orig_offset = struct.unpack("<I", data[12:16])[0]
    l1, o1 = struct.unpack("<II", data[orig_offset : orig_offset + 8])
    first_msgid = data[o1 : o1 + l1]

    trans_offset = struct.unpack("<I", data[16:20])[0]
    l2, o2 = struct.unpack("<II", data[trans_offset : trans_offset + 8])
    first_msgstr = data[o2 : o2 + l2]

    print(f"MO: magic={hex(magic)}, nstrings={n}")
    print(f"First msgid: {first_msgid[:50]!r}")
    print(f"First msgstr: {first_msgstr[:50]!r}")


if __name__ == "__main__":
    compile_mo()
