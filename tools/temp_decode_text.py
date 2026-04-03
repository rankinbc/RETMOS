#!/usr/bin/env python3
"""Decode consecutive bit7-terminated text strings from bank 4 of TMOS ROM."""

ROM_PATH = "/mnt/c/Users/Brian.Rankin/claude-workspace/projects/RETMOS/roms/TMOS_ORIGINAL.nes"
BANK4_BASE = 0x10010

# Character map
CHAR_MAP = {}
for i in range(10):
    CHAR_MAP[i] = chr(ord('0') + i)
CHAR_MAP[0x2C] = ' '
CHAR_MAP[0x29] = ' '
for i in range(26):
    CHAR_MAP[0x30 + i] = chr(ord('A') + i)
CHAR_MAP[0x4C] = '\''
CHAR_MAP[0x4D] = '\''
CHAR_MAP[0x4E] = ':'
CHAR_MAP[0x4F] = '.'
CHAR_MAP[0x7B] = '-'
CHAR_MAP[0x7C] = '?'
CHAR_MAP[0x7D] = '!'
CHAR_MAP[0x7E] = '...'


def decode_char(byte_val):
    if byte_val in CHAR_MAP:
        return CHAR_MAP[byte_val]
    return f'[${byte_val:02X}]'


def main():
    with open(ROM_PATH, 'rb') as f:
        rom_data = f.read()

    # Scan consecutive strings starting at $BD34 through end of bank ($BFFF)
    start_addr = 0xBD34
    end_addr = 0xBFFF
    pos = BANK4_BASE + (start_addr - 0x8000)
    count = 0

    while True:
        cpu_addr = 0x8000 + (pos - BANK4_BASE)
        if cpu_addr >= end_addr:
            break

        # Decode one string
        result = []
        string_start = pos
        valid = True
        while True:
            if pos - BANK4_BASE + 0x8000 >= end_addr + 1:
                valid = False
                break
            byte_val = rom_data[pos]
            is_last = (byte_val & 0x80) != 0
            char_val = byte_val & 0x7F
            ch = decode_char(char_val)
            result.append(ch)
            pos += 1
            if is_last:
                break
            # Safety: strings shouldn't be longer than 32 chars
            if len(result) > 32:
                valid = False
                break

        if not valid:
            break

        text = ''.join(result)
        addr = 0x8000 + (string_start - BANK4_BASE)
        print(f'  [{count:3d}] ${addr:04X}: {text}')
        count += 1

    print(f'\nTotal: {count} strings from ${start_addr:04X} to ${0x8000 + (pos - BANK4_BASE) - 1:04X}')


if __name__ == '__main__':
    main()
