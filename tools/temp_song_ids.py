#!/usr/bin/env python3
"""Extract all queue_sound ($E992) call sites and their sound IDs."""

import os

ROM_PATH = os.path.join(os.path.dirname(__file__), '..', 'roms', 'TMOS_ORIGINAL.nes')
HEADER = 16
BANK_SIZE = 0x4000

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

# Search for JSR $E992 pattern: 20 92 E9
pattern = bytes([0x20, 0x92, 0xE9])
calls = {}  # sound_id -> [(bank, addr, context)]
indirect = []  # calls where A isn't from immediate LDA

for offset in range(HEADER, len(rom) - 2):
    if rom[offset:offset+3] == pattern:
        bank = (offset - HEADER) // BANK_SIZE
        addr = 0x8000 + ((offset - HEADER) % BANK_SIZE)

        # Look back for LDA #imm (A9 xx) within 4 bytes
        sound_id = None
        source = "unknown"

        for lookback in range(2, 8):
            if offset - lookback >= HEADER:
                if rom[offset - lookback] == 0xA9:  # LDA #imm
                    sound_id = rom[offset - lookback + 1]
                    # Check nothing between LDA and JSR modifies A
                    between = rom[offset - lookback + 2:offset]
                    # Simple check: if the bytes between are just the JSR itself, it's clean
                    if lookback == 2:
                        source = "immediate"
                        break
                    # Check for common safe instructions between
                    safe = True
                    i = 0
                    while i < len(between):
                        b = between[i]
                        if b in (0x48, 0x08):  # PHA, PHP - might be OK but A still valid
                            i += 1
                        elif b in (0x85, 0x86, 0x84):  # STA/STX/STY zp
                            i += 2
                        elif b in (0x8D, 0x8E, 0x8C):  # STA/STX/STY abs
                            i += 3
                        elif b == 0xA9:  # Another LDA #imm - take the CLOSEST one
                            sound_id = between[i+1]
                            safe = True
                            i += 2
                        elif b == 0xA5:  # LDA zp - A is now from ZP, not imm
                            sound_id = None
                            source = f"LDA ${between[i+1]:02X}"
                            safe = False
                            break
                        elif b == 0xAD:  # LDA abs
                            sound_id = None
                            if i+2 < len(between):
                                abs_addr = between[i+1] | (between[i+2] << 8)
                                source = f"LDA ${abs_addr:04X}"
                            safe = False
                            break
                        elif b in (0xBD, 0xB9, 0xB1, 0xB5):  # LDA indexed
                            sound_id = None
                            source = "indexed"
                            safe = False
                            break
                        elif b == 0x68:  # PLA
                            sound_id = None
                            source = "PLA"
                            safe = False
                            break
                        elif b == 0x46:  # LSR zp
                            i += 2
                        elif b == 0x4A:  # LSR A - modifies A
                            sound_id = None
                            source = "shifted"
                            safe = False
                            break
                        else:
                            # Unknown instruction, be conservative
                            i += 1
                    if safe and sound_id is not None:
                        source = "immediate"
                        break

        if sound_id is not None and source == "immediate":
            if sound_id not in calls:
                calls[sound_id] = []
            calls[sound_id].append((bank, addr))
        else:
            indirect.append((bank, addr, source))

# Print results sorted by sound ID
print("=" * 70)
print("Sound ID Usage Map - The Magic of Scheherazade")
print("=" * 70)

# Group by category
print("\n--- SPECIAL VALUES ---")
for sid in sorted(calls.keys()):
    if sid in (0x00, 0xFF):
        sites = calls[sid]
        banks = {}
        for b, a in sites:
            banks.setdefault(b, []).append(a)
        bank_str = ", ".join(f"B{b}({len(addrs)})" for b, addrs in sorted(banks.items()))
        label = "$FF=silence" if sid == 0xFF else "$00=no-op"
        print(f"  ${sid:02X}: {label} -- {len(sites)} sites [{bank_str}]")

print("\n--- SOUND EFFECTS (SFX) ---")
for sid in sorted(calls.keys()):
    if sid == 0x00 or sid == 0xFF:
        continue
    sites = calls[sid]
    banks = {}
    for b, a in sites:
        banks.setdefault(b, []).append(a)
    bank_str = ", ".join(f"B{b}({len(addrs)})" for b, addrs in sorted(banks.items()))
    print(f"  ${sid:02X} ({sid:3d}): {len(sites):2d} sites [{bank_str}]")

print(f"\n--- INDIRECT/DYNAMIC ({len(indirect)} sites) ---")
for b, a, src in sorted(indirect):
    print(f"  Bank {b} ${a:04X}: A from {src}")

# Summary
all_ids = sorted(calls.keys())
print(f"\n{'=' * 70}")
print(f"Total: {sum(len(v) for v in calls.values())} static + {len(indirect)} dynamic = {sum(len(v) for v in calls.values()) + len(indirect)} call sites")
print(f"Unique sound IDs: {len(all_ids)} ({min(all_ids):02X}-{max(all_ids):02X})")
print(f"{'=' * 70}")
