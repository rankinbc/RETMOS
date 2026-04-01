#!/usr/bin/env python3
"""
Text decoder for The Magic of Scheherazade.

Character encoding (CHR bank 0, pattern table 0):
  $00-$09: digits '0'-'9'
  $2C: space ' '
  $30-$49: uppercase 'A'-'Z'
  $4C: left quote
  $4D: right quote / apostrophe
  $4E: colon ':'
  $4F: period '.'
  $7B: dash '-'
  $7C: question mark '?'
  $7D: exclamation '!'
  $7E: ellipsis '...'

Text format:
  - Bit 7 ($80) on last byte marks end of word/token in dictionary mode
  - Control codes: $8C+ values that don't map to char+$80

Usage:
  python3 tools/text_decode.py <bank> <addr> <length>
  python3 tools/text_decode.py --scan <bank>           # scan bank for text strings
  python3 tools/text_decode.py --dict <bank> <addr> <count>  # decode dictionary entries

Examples:
  python3 tools/text_decode.py 1 AC06 64
  python3 tools/text_decode.py --dict 6 A160 20
  python3 tools/text_decode.py --scan 1
"""

import sys
import os

ROM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "roms", "TMOS_ORIGINAL.nes")

INES_HEADER = 16
PRG_BANK_SIZE = 16384

# Character mapping: tile index -> character
CHAR_MAP = {}
# Digits
for i in range(10):
    CHAR_MAP[i] = chr(ord('0') + i)
# Letters A-Z
for i in range(26):
    CHAR_MAP[0x30 + i] = chr(ord('A') + i)
# Punctuation / symbols
CHAR_MAP[0x29] = ' '   # blank tile (alternate space)
CHAR_MAP[0x2C] = ' '   # space (primary)
CHAR_MAP[0x4C] = "'"   # left quote
CHAR_MAP[0x4D] = "'"   # right quote / apostrophe
CHAR_MAP[0x4E] = ':'
CHAR_MAP[0x4F] = '.'
CHAR_MAP[0x7B] = '-'
CHAR_MAP[0x7C] = '?'
CHAR_MAP[0x7D] = '!'
CHAR_MAP[0x7E] = '...'
CHAR_MAP[0x28] = '>'   # right arrow


def decode_char(byte_val):
    """Decode a single byte to character. Returns (char, is_end_marker)."""
    is_end = bool(byte_val & 0x80)
    base = byte_val & 0x7F
    ch = CHAR_MAP.get(base)
    if ch is not None:
        return ch, is_end
    return None, is_end


def decode_text(data, offset, length, show_control=False):
    """Decode a text string from ROM data. Returns decoded string."""
    result = []
    for i in range(length):
        if offset + i >= len(data):
            break
        b = data[offset + i]
        ch, is_end = decode_char(b)
        if ch is not None:
            result.append(ch)
            if is_end and show_control:
                result.append('|')  # word boundary marker
        elif show_control:
            result.append(f'[${b:02X}]')
    return ''.join(result)


def decode_dictionary(data, offset, count):
    """Decode dictionary entries (words separated by bit-7 end markers)."""
    words = []
    current_word = []
    pos = offset
    while len(words) < count and pos < len(data):
        b = data[pos]
        is_end = bool(b & 0x80)
        base = b & 0x7F
        ch = CHAR_MAP.get(base)
        if ch is not None:
            current_word.append(ch)
        else:
            current_word.append(f'[${base:02X}]')
        if is_end:
            words.append((''.join(current_word), offset, pos - offset + 1))
            offset = pos + 1
            current_word = []
        pos += 1
    return words


def scan_for_text(data, bank_offset, bank_size, min_length=4):
    """Scan a bank for runs of valid text characters."""
    strings = []
    current = []
    start = 0

    for i in range(bank_size):
        b = data[bank_offset + i]
        base = b & 0x7F
        ch = CHAR_MAP.get(base)
        if ch is not None:
            if not current:
                start = i
            current.append(ch)
        else:
            if len(current) >= min_length:
                text = ''.join(current)
                # Filter out strings that are all spaces or all same char
                stripped = text.replace(' ', '')
                if len(stripped) >= min_length // 2 and len(set(stripped)) > 1:
                    addr = 0x8000 + start if bank_offset != INES_HEADER + 7 * PRG_BANK_SIZE else 0xC000 + start
                    strings.append((start, addr, text, len(current)))
            current = []

    if len(current) >= min_length:
        text = ''.join(current)
        stripped = text.replace(' ', '')
        if len(stripped) >= min_length // 2:
            addr = 0x8000 + start
            strings.append((start, addr, text, len(current)))

    return strings


def addr_to_file_offset(bank, addr):
    if bank == 7 or 0xC000 <= addr <= 0xFFFF:
        return INES_HEADER + 7 * PRG_BANK_SIZE + (addr - 0xC000)
    return INES_HEADER + bank * PRG_BANK_SIZE + (addr - 0x8000)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    with open(ROM_PATH, "rb") as f:
        rom_data = f.read()

    if args[0] == "--scan":
        bank = int(args[1])
        bank_offset = INES_HEADER + bank * PRG_BANK_SIZE
        strings = scan_for_text(rom_data, bank_offset, PRG_BANK_SIZE, min_length=5)
        print(f"Text strings in PRG bank {bank} (min 5 chars):")
        print()
        for rel_off, addr, text, length in strings:
            print(f"  ${addr:04X} [{length:3d}]: {text}")
        print(f"\nFound {len(strings)} strings")

    elif args[0] == "--dict":
        bank = int(args[1])
        addr = int(args[2], 16)
        count = int(args[3])
        file_off = addr_to_file_offset(bank, addr)
        words = decode_dictionary(rom_data, file_off, count)
        print(f"Dictionary at bank {bank} ${addr:04X} ({count} entries):")
        print()
        for i, (word, off, size) in enumerate(words):
            print(f"  [{i:3d}] {word}")

    else:
        bank = int(args[0])
        addr = int(args[1], 16)
        length = int(args[2]) if len(args) > 2 else 64
        file_off = addr_to_file_offset(bank, addr)

        print(f"Text at bank {bank} ${addr:04X} ({length} bytes):")
        print()

        # Show decoded text with control codes
        text = decode_text(rom_data, file_off, length, show_control=True)
        print(f"  {text}")
        print()

        # Also show raw hex for reference
        raw = rom_data[file_off:file_off + length]
        hex_str = ' '.join(f'{b:02X}' for b in raw)
        print(f"  Raw: {hex_str}")


if __name__ == "__main__":
    main()
