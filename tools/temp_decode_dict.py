#!/usr/bin/env python3
"""Decode all 16 dictionary groups from bank 2 $99B7-$9C37."""

import struct, sys, os

ROM_PATH = os.path.join(os.path.dirname(__file__), '..', 'roms', 'TMOS_ORIGINAL.nes')
HEADER = 16
BANK2_OFFSET = HEADER + 2 * 0x4000  # bank 2 starts at file offset 0x08010

# Character encoding map
CHAR_MAP = {}
for i in range(10):
    CHAR_MAP[i] = str(i)
CHAR_MAP[0x2C] = ' '
for i in range(26):
    CHAR_MAP[0x30 + i] = chr(ord('A') + i)
# Known special glyphs beyond Z
CHAR_MAP[0x4A] = '.'   # tentative
CHAR_MAP[0x4B] = ','   # tentative
CHAR_MAP[0x4C] = '!'   # tentative
CHAR_MAP[0x4D] = '?'   # tentative
CHAR_MAP[0x4E] = "'"   # tentative
CHAR_MAP[0x4F] = '-'   # tentative (appears between words like "R-ARMOR")

def cpu_to_file(addr):
    """Convert bank 2 CPU address to file offset."""
    return BANK2_OFFSET + (addr - 0x8000)

def decode_char(b):
    """Decode a single byte (with bit 7 stripped) to a character."""
    c = b & 0x7F
    return CHAR_MAP.get(c, f'[{c:02X}]')

def decode_dict_group(rom, base_ptr, group_idx):
    """Decode all words in a dictionary group, return list of strings."""
    words = []
    pos = base_ptr
    current_word = []

    while True:
        b = rom[cpu_to_file(pos)]
        ch = decode_char(b)
        current_word.append(ch)

        if b & 0x80:  # bit 7 set = end of word
            words.append(''.join(current_word))
            current_word = []
            pos += 1
            # Check if we've reached the next group's start
            # (we'll handle boundaries externally)
        else:
            pos += 1

    return words

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

# Read the 16 dictionary group pointers from $99B7
ptr_table_offset = cpu_to_file(0x99B7)
group_ptrs = []
for i in range(16):
    lo = rom[ptr_table_offset + i*2]
    hi = rom[ptr_table_offset + i*2 + 1]
    group_ptrs.append(lo | (hi << 8))

# Determine boundaries: each group ends where the next one starts
# Last group ends at $9C37 (just before text entry table at $9C3A)
boundaries = group_ptrs[1:] + [0x9C37]

print("=" * 60)
print("The Magic of Scheherazade - Dictionary Word List")
print("Bank 2 $99B7: 16 dictionary groups")
print("=" * 60)

total_words = 0
for g in range(16):
    start = group_ptrs[g]
    end = boundaries[g]
    size = end - start

    if size <= 0 or size > 500:
        print(f"\nGroup {g:2d} (${start:04X}): [empty or invalid, size={size}]")
        continue

    # Decode words
    words = []
    pos = start
    current_word = []

    while pos < end:
        b = rom[cpu_to_file(pos)]
        ch = decode_char(b)
        current_word.append(ch)

        if b & 0x80:
            words.append(''.join(current_word))
            current_word = []
        pos += 1

    # Handle any trailing partial word
    if current_word:
        words.append(''.join(current_word) + '...')

    total_words += len(words)
    print(f"\nGroup {g:2d} (${start:04X}, {size}B, {len(words)} words):")
    for w, word in enumerate(words):
        print(f"  [{g:X}{w:X}] {word}")

print(f"\n{'=' * 60}")
print(f"Total: {total_words} words across 16 groups")
print(f"{'=' * 60}")
print(f"\nNote: Characters marked [XX] are unmapped tile IDs.")
print(f"Glyphs $4A-$4F tentatively mapped as . , ! ? ' -")
