#!/usr/bin/env python3
"""Extract all $0300+ game state addresses from chapter warp data and cross-reference."""

import os

ROM_PATH = os.path.join(os.path.dirname(__file__), '..', 'roms', 'TMOS_ORIGINAL.nes')
HEADER = 16

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

# Bank 6 file offset for $BB1F
BANK6_OFF = HEADER + 6 * 0x4000  # 0x18010
WARP_START = BANK6_OFF + (0xBB1F - 0x8000)

# Read warp records (7 bytes each, terminated by $FF)
addresses = {}  # addr -> [ch0, ch1, ch2, ch3, ch4]
pos = WARP_START
while True:
    b0 = rom[pos]
    if b0 == 0xFF:
        break
    b1 = rom[pos+1]
    addr = b0 | (b1 << 8)
    vals = [rom[pos+2+i] for i in range(5)]
    addresses[addr] = vals
    pos += 7

print("=" * 80)
print("Game State Variable Map ($0300+ from chapter warp data)")
print(f"{len(addresses)} addresses set by warp system")
print("=" * 80)

# Known labels from our RE work
known = {
    0x0084: "screen_position",
    0x0087: "world_flags",
    0x0089: "chapter_number",
    0x0300: "bread_count",
    0x0301: "mashroob_count",
    0x0302: "armor_level",
}

# Password command mapping
pwd_addrs = {
    0x0300: "$10 (base stat 0, max 9)",
    0x0301: "$11 (base stat 1, max 9)",
    0x0306: "$33 (ext stat 3, max 10)",
    0x0307: "$34 (ext stat 4, max 10)",
    0x030D: "$58 (special 8, max 1)",
    0x030F: "$50 (special 0)",
    0x0310: "$51 (special 1, max 5)",
    0x0311: "$52 (special 2, max 15)",
    0x0312: "$53 (special 3)",
}

# Group by address range
zp_addrs = {a: v for a, v in sorted(addresses.items()) if a < 0x0100}
ram_addrs = {a: v for a, v in sorted(addresses.items()) if 0x0300 <= a < 0x0400}
other_addrs = {a: v for a, v in sorted(addresses.items()) if a >= 0x0100 and a < 0x0300 or a >= 0x0400}

if zp_addrs:
    print("\n--- Zero Page ---")
    for addr, vals in sorted(zp_addrs.items()):
        label = known.get(addr, "")
        print(f"  ${addr:04X}: ch0={vals[0]:3d} ch1={vals[1]:3d} ch2={vals[2]:3d} ch3={vals[3]:3d} ch4={vals[4]:3d}  {label}")

if ram_addrs:
    print(f"\n--- $0300-$03FF ({len(ram_addrs)} addresses) ---")
    for addr, vals in sorted(ram_addrs.items()):
        label = known.get(addr, "")
        pwd = pwd_addrs.get(addr, "")
        # Analyze value pattern
        if all(v == vals[0] for v in vals):
            pattern = f"constant={vals[0]}"
        elif vals == sorted(vals):
            pattern = "increasing"
        elif all(v <= 1 for v in vals):
            pattern = "boolean"
        else:
            pattern = ""
        extra = f"  {label}" if label else ""
        extra += f"  pwd:{pwd}" if pwd else ""
        extra += f"  [{pattern}]" if pattern else ""
        print(f"  ${addr:04X}: {vals[0]:3d} {vals[1]:3d} {vals[2]:3d} {vals[3]:3d} {vals[4]:3d}{extra}")

if other_addrs:
    print(f"\n--- Other ({len(other_addrs)} addresses) ---")
    for addr, vals in sorted(other_addrs.items()):
        print(f"  ${addr:04X}: {vals[0]:3d} {vals[1]:3d} {vals[2]:3d} {vals[3]:3d} {vals[4]:3d}")
