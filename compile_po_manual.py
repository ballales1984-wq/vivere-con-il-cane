import struct
import array
import os

def compile_po_to_mo(po_path, mo_path):
    """Simple PO to MO compiler in pure Python"""
    messages = {}
    with open(po_path, 'r', encoding='utf-8') as f:
        msgid = None
        for line in f:
            line = line.strip()
            if line.startswith('msgid "'):
                msgid = line[7:-1]
            elif line.startswith('msgstr "') and msgid is not None:
                msgstr = line[8:-1]
                if msgid and msgstr:
                    messages[msgid] = msgstr
                msgid = None

    keys = sorted(messages.keys())
    offsets = []
    ids = b''
    strs = b''

    for k in keys:
        v = messages[k].encode('utf-8')
        k = k.encode('utf-8')
        offsets.append((len(ids), len(k), len(strs), len(v)))
        ids += k + b'\0'
        strs += v + b'\0'

    # MO file format header
    # Magic number, version, msg count, offset of msgids, offset of msgstrs, hash size, hash offset
    keystart = 7 * 4
    valstart = keystart + len(keys) * 8
    
    header = struct.pack('<Iiiiiii',
                         0x950412de, # Magic
                         0,          # Version
                         len(keys),  # Msg count
                         keystart,   # Offset of msgids
                         valstart,   # Offset of msgstrs
                         0, 0)       # Hash (not needed)

    id_table = []
    str_table = []
    
    current_id_offset = valstart + len(keys) * 8
    current_str_offset = current_id_offset + len(ids)

    for id_off, id_len, str_off, str_len in offsets:
        id_table.append(struct.pack('<ii', id_len, current_id_offset + id_off))
        str_table.append(struct.pack('<ii', str_len, current_str_offset + str_off))

    with open(mo_path, 'wb') as f:
        f.write(header)
        for t in id_table: f.write(t)
        for t in str_table: f.write(t)
        f.write(ids)
        f.write(strs)

if __name__ == "__main__":
    po_file = r'locale\en\LC_MESSAGES\django.po'
    mo_file = r'locale\en\LC_MESSAGES\django.mo'
    if os.path.exists(po_file):
        compile_po_to_mo(po_file, mo_file)
        print(f"Compiled {po_file} to {mo_file}")
    else:
        print(f"Error: {po_file} not found")
