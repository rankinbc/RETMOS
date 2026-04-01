#!/usr/bin/env python3
"""Scan all WorldScreen records and extract unique DataPointer ($B8) values."""

import sys

ROM_PATH = "roms/TMOS_ORIGINAL.nes"

# Chapter data locations (file offsets, from REVERSE.md)
CHAPTERS = [
    (1, 0x039695, 131),
    (2, 0x039EC5, 137),
    (3, 0x03A755, 153),
    (4, 0x03B0E5, 164),
    (5, 0x03BB25, 154),
]

RECORD_SIZE = 16

with open(ROM_PATH, "rb") as f:
    rom = f.read()

# Collect all DataPointer values
dp_values = {}  # dp_value -> list of (chapter, screen_idx)
chr_indices = {}  # $38 value -> list of (chapter, screen_idx, dp_raw)

for ch_num, offset, count in CHAPTERS:
    for i in range(count):
        rec_offset = offset + i * RECORD_SIZE
        if rec_offset + RECORD_SIZE > len(rom):
            break
        rec = rom[rec_offset:rec_offset + RECORD_SIZE]
        dp = rec[8]  # DataPointer is byte 8
        chr_idx = dp & 0x3F  # bits 0-5 = $38

        if dp not in dp_values:
            dp_values[dp] = []
        dp_values[dp].append((ch_num, i))

        if chr_idx not in chr_indices:
            chr_indices[chr_idx] = []
        chr_indices[chr_idx].append((ch_num, i, dp))

print("=== DataPointer ($B8) raw values ===")
print(f"{'DP':>4s} {'$38':>4s} {'Bit7':>5s} {'Bit6':>5s} {'Count':>6s}  Chapters")
for dp in sorted(dp_values.keys()):
    chr_idx = dp & 0x3F
    bit7 = (dp >> 7) & 1
    bit6 = (dp >> 6) & 1
    chapters = set(ch for ch, _ in dp_values[dp])
    ch_str = ",".join(str(c) for c in sorted(chapters))
    print(f"${dp:02X}   ${chr_idx:02X}     {bit7}       {bit6}     {len(dp_values[dp]):>4d}   Ch {ch_str}")

print()
print("=== Unique $38 (CHR bank index) values ===")
print(f"{'$38':>4s} {'Count':>6s}  CHR0  CHR1  Chapters")

# Read CHR bank table
chr_table_offset = 0x1ED53  # $ED43 in file
for idx in sorted(chr_indices.keys()):
    count = len(chr_indices[idx])
    chapters = set(ch for ch, _, _ in chr_indices[idx])
    ch_str = ",".join(str(c) for c in sorted(chapters))
    tbl_off = chr_table_offset + idx * 2
    if tbl_off + 1 < len(rom):
        chr0 = rom[tbl_off]
        chr1 = rom[tbl_off + 1]
        print(f"${idx:02X}   {count:>4d}    ${chr0:02X}    ${chr1:02X}   Ch {ch_str}")
    else:
        print(f"${idx:02X}   {count:>4d}    ??    ??   Ch {ch_str}")

# Also check what ParentWorld values correlate with each $38
print()
print("=== $38 by ParentWorld (game area type) ===")
for ch_num, offset, count in CHAPTERS:
    for i in range(count):
        rec_offset = offset + i * RECORD_SIZE
        rec = rom[rec_offset:rec_offset + RECORD_SIZE]
        parent = rec[0]  # ParentWorld
        dp = rec[8]
        chr_idx = dp & 0x3F

# Re-collect with parent world
parent_chr = {}  # (parent, chr_idx) -> count
for ch_num, offset, count in CHAPTERS:
    for i in range(count):
        rec_offset = offset + i * RECORD_SIZE
        rec = rom[rec_offset:rec_offset + RECORD_SIZE]
        parent = rec[0]
        dp = rec[8]
        chr_idx = dp & 0x3F
        key = (parent, chr_idx)
        parent_chr[key] = parent_chr.get(key, 0) + 1

print(f"{'Parent':>7s} {'$38':>4s} {'Count':>6s}")
for (parent, idx) in sorted(parent_chr.keys()):
    print(f"  ${parent:02X}    ${idx:02X}   {parent_chr[(parent, idx)]:>4d}")
