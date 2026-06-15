#!/usr/bin/env python3
"""Decode the item/magic-menu name strings (bank 1 $B4BA ptr table -> tile strings).

$B3D3 renders menu text: A*2 -> $B4BA ptr -> copy null-terminated tile string to
nametable buffer. Tile encoding: $30-$49=A-Z, $00-$09=digits, $2C=space, $4F='-'.
"""
import os
ROM = os.path.join(os.path.dirname(__file__), "..", "roms", "TMOS_ORIGINAL.nes")
HDR = 16
with open(ROM, "rb") as f:
    DATA = f.read()

def rd(bank, addr):
    return DATA[HDR + bank * 0x4000 + (addr - 0x8000)]

def tchar(v):
    if 0x00 <= v <= 0x09: return chr(ord('0') + v)
    if 0x30 <= v <= 0x49: return chr(ord('A') + (v - 0x30))
    if v == 0x2C: return ' '
    if v == 0x4F: return '-'
    if v == 0x2E: return '.'
    return "{%02X}" % v

def decode_str(bank, addr, maxlen=64):
    s = ""
    for i in range(maxlen):
        b = rd(bank, addr + i)
        if b == 0x00:
            break
        s += tchar(b)
    return s

print("Menu name pointer table $B4BA (bank 1) + decoded strings:\n")
for i in range(10):
    pa = 0xB4BA + i * 2
    p = rd(1, pa) | (rd(1, pa + 1) << 8)
    if not (0x8000 <= p <= 0xBFFF):
        print("  [%d] $%04X -> $%04X (out of range, table end)" % (i, pa, p))
        break
    print("  [%d] $%04X -> $%04X : \"%s\"" % (i, pa, p, decode_str(1, p)))
