#!/usr/bin/env python3
"""Decode CHR bank 22-24 dialogue text data."""

import os

ROM_PATH = os.path.join(os.path.dirname(__file__), '..', 'roms', 'TMOS_ORIGINAL.nes')
HEADER = 16
PRG_SIZE = 128 * 1024
CHR_BASE = HEADER + PRG_SIZE

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

# Character map
def decode_char(b):
    raw = b & 0x7F
    if raw == 0x2C: return ' '
    if 0x30 <= raw <= 0x49: return chr(ord('A') + raw - 0x30)
    if 0x00 <= raw <= 0x09: return str(raw)
    if raw == 0x4A: return '.'
    if raw == 0x4B: return ','
    if raw == 0x4C: return "'"
    if raw == 0x4D: return '?'
    if raw == 0x4E: return "'"
    if raw == 0x4F: return '-'
    return None

# Control codes
CTRL = {
    0x7A: '\n',
    0x7B: '\n---\n',   # section break?
    0x7C: '?',          # question mark
    0x7D: '!',          # exclamation
    0x7E: '\n\n',       # paragraph/new box
    0x7F: '\n[END]\n',  # end of text block
    0x52: '{HERO}',     # player name
    0xFE: '',           # delimiter (skip)
    0xFA: '',           # appears after newlines (skip)
}

def decode_dialogue(data, max_bytes=4096):
    result = []
    i = 0
    while i < min(len(data), max_bytes):
        b = data[i]

        # Control codes
        if b in CTRL:
            result.append(CTRL[b])
            i += 1
            continue

        # Regular character
        ch = decode_char(b)
        if ch:
            result.append(ch)
            i += 1
            continue

        # Special codes $50-$6F (inline references)
        if 0x50 <= b <= 0x6F:
            result.append(f'[${b:02X}]')
            i += 1
            continue

        # $70-$79 codes
        if 0x70 <= b <= 0x79:
            result.append(f'[${b:02X}]')
            i += 1
            continue

        # Values $10-$2B - might be formatting/indices
        if 0x0A <= b <= 0x2B:
            result.append(f'[${b:02X}]')
            i += 1
            continue

        # Dictionary references ($80+)
        if b >= 0x80:
            group = (b >> 4) & 0x07
            word = b & 0x0F
            result.append(f'{{D{group}:{word}}}')
            i += 1
            continue

        result.append(f'[${b:02X}]')
        i += 1

    return ''.join(result)

# Decode CHR banks 22-24
for bank_num in [22, 23, 24]:
    bank_offset = CHR_BASE + bank_num * 0x1000
    data = rom[bank_offset:bank_offset + 0x1000]

    print(f"{'=' * 70}")
    print(f"CHR Bank {bank_num} (file offset 0x{bank_offset:05X})")
    print(f"{'=' * 70}")

    text = decode_dialogue(data)

    # Split into entries by [END] markers
    entries = text.split('[END]')
    for idx, entry in enumerate(entries):
        entry = entry.strip()
        if not entry:
            continue
        print(f"\n--- Entry {idx} ---")
        print(entry)

    print()
