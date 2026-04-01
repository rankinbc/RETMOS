#!/usr/bin/env python3
"""Find all JSR $E8C8 calls and extract the A value (LDA #imm) that precedes them."""

ROM_PATH = "roms/TMOS_ORIGINAL.nes"
HEADER = 16
BANK_SIZE = 0x4000

with open(ROM_PATH, "rb") as f:
    rom = f.read()

prg = rom[HEADER:HEADER + 8 * BANK_SIZE]

# Search for JSR $E8C8 = 20 C8 E8
pattern = bytes([0x20, 0xC8, 0xE8])

print(f"{'Bank':>4s} {'Addr':>6s} {'A val':>6s}  {'CHR0':>5s} {'CHR1':>5s}  Context")
print("-" * 70)

# CHR bank table at $ED43 in bank 7
chr_tbl_off = 7 * BANK_SIZE + (0xED43 - 0xC000)

for offset in range(len(prg)):
    if prg[offset:offset+3] == pattern:
        bank = offset // BANK_SIZE
        addr = (offset % BANK_SIZE) + (0xC000 if bank == 7 else 0x8000)

        # Check what's before this: LDA #imm = A9 XX
        a_val = None
        source = "?"
        if offset >= 2 and prg[offset-2] == 0xA9:
            a_val = prg[offset-1]
            source = f"LDA #${a_val:02X}"
        elif offset >= 3 and prg[offset-3] == 0xA5:
            zp = prg[offset-2]
            source = f"LDA ${zp:02X} (zp)"
        elif offset >= 4 and prg[offset-4:offset-1] == bytes([0xAD]):
            lo = prg[offset-3]
            hi = prg[offset-2]
            source = f"LDA ${hi:02X}{lo:02X} (abs)"
        # Check for LDA $B8; AND #$3F pattern
        if offset >= 5:
            if prg[offset-5:offset-3] == bytes([0xA5, 0xB8]) and prg[offset-3:offset-1] == bytes([0x29, 0x3F]):
                source = "LDA $B8; AND #$3F (DataPointer)"
                a_val = None  # dynamic

        # Also check for AD XX XX (LDA abs)
        if offset >= 3 and prg[offset-3] == 0xAD:
            lo = prg[offset-2]
            hi = prg[offset-1]
            source = f"LDA ${hi:02X}{lo:02X} (abs)"

        chr0_str = "?"
        chr1_str = "?"
        if a_val is not None and a_val < 32:
            tbl_idx = a_val * 2
            chr0 = prg[chr_tbl_off + tbl_idx]
            chr1 = prg[chr_tbl_off + tbl_idx + 1]
            chr0_str = f"${chr0:02X}"
            chr1_str = f"${chr1:02X}"

        print(f"  {bank:>2d} ${addr:04X}   {source:>20s}  {chr0_str:>5s} {chr1_str:>5s}")
