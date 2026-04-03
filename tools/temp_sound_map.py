#!/usr/bin/env python3
"""Map sound IDs to channels and categories using the $800E priority table."""

import os

ROM_PATH = os.path.join(os.path.dirname(__file__), '..', 'roms', 'TMOS_ORIGINAL.nes')
HEADER = 16
BANK0_OFFSET = HEADER

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

# Priority table at bank 0 $800E (144 entries, IDs 0-$8F)
PRIO_TABLE = BANK0_OFFSET + 0x000E  # file offset

CHANNEL_NAMES = {
    0: "Pulse1 SFX ($F8)",
    1: "Song ($F9)",
    2: "Noise ($FA)",
    3: "SFX overlay ($FB)"
}

CHANNEL_SHORT = {0: "SFX", 1: "SONG", 2: "NOISE", 3: "OVERLAY"}

print("=" * 80)
print("Sound ID -> Channel/Priority Routing (bank 0 $800E table)")
print("=" * 80)

# Collect by channel
by_channel = {0: [], 1: [], 2: [], 3: []}
silent = []

for sid in range(0x90):
    byte = rom[PRIO_TABLE + sid]
    priority = byte & 0x3F
    channel = (byte >> 6) & 0x03

    if priority == 0:
        silent.append(sid)
    else:
        by_channel[channel].append((sid, priority, byte))

print(f"\nSilent/unused IDs ({len(silent)}): ", end="")
# Group consecutive ranges
ranges = []
start = None
prev = None
for s in silent:
    if start is None:
        start = prev = s
    elif s == prev + 1:
        prev = s
    else:
        ranges.append((start, prev))
        start = prev = s
if start is not None:
    ranges.append((start, prev))
print(", ".join(f"${s:02X}-${e:02X}" if s != e else f"${s:02X}" for s, e in ranges))

for ch in range(4):
    entries = by_channel[ch]
    if not entries:
        continue
    print(f"\n--- Channel {ch}: {CHANNEL_NAMES[ch]} ({len(entries)} IDs) ---")
    for sid, pri, raw in entries:
        print(f"  ${sid:02X} ({sid:3d})  pri={pri:2d}  raw=${raw:02X}")

# Now print a condensed mapping for the IDs we found in call sites
print("\n" + "=" * 80)
print("Sound ID Context Map (cross-referenced with call sites)")
print("=" * 80)

# Known context from code analysis
context = {
    0x01: "overworld music start",
    0x02: "entity SFX (type 5 knock)",
    0x03: "UI/transition SFX",
    0x04: "chapter SFX",
    0x05: "overworld/area music",
    0x07: "entity collision SFX",
    0x0A: "entity/battle SFX",
    0x0B: "RPG party command SFX",
    0x0C: "RPG party command SFX",
    0x0D: "RPG/scene SFX",
    0x0E: "RPG battle SFX",
    0x0F: "entity hurt SFX",
    0x10: "tile/screen SFX",
    0x11: "entity AI SFX",
    0x13: "screen scroll start",
    0x15: "RPG battle start fanfare",
    0x17: "RPG battle victory fanfare",
    0x18: "screen scroll complete",
    0x19: "chapter event SFX",
    0x1A: "enter area / warp SFX",
    0x1B: "ambient/area SFX",
    0x1C: "hit/attack connect",
    0x1D: "death/kill SFX",
    0x1E: "menu/dialogue SFX",
    0x1F: "ambient SFX",
    0x20: "ambient SFX",
    0x21: "entity despawn SFX",
    0x22: "enemy contact damage",
    0x23: "boss/special SFX",
    0x25: "UI confirm SFX",
    0x26: "warp/spell SFX",
    0x27: "item get SFX",
    0x28: "equip/use SFX",
    0x29: "level up SFX",
    0x2B: "NPC interact SFX",
    0x2D: "boss phase SFX",
    0x2E: "boss attack SFX",
    0x2F: "entity projectile SFX",
    0x30: "entity event SFX",
    0x31: "area/zone music",
    0x32: "battle result SFX",
    0x33: "RPG spell cast",
    0x34: "RPG battle result fanfare",
    0x39: "dialogue/UI music",
    0x3A: "player attack swing",
    0x3B: "treasure open SFX",
    0x3C: "key item get",
    0x3D: "shop/menu music",
    0x3E: "continue/password music",
    0x3F: "tempo change (special)",
    0x42: "title/intro SFX",
    0x43: "title/intro SFX",
    0x44: "title/intro SFX",
    0x45: "chapter intro music",
    0x46: "chapter screen music",
    0x49: "ending/credits SFX",
    0x4A: "scene SFX",
    0x4C: "game over SFX",
    0x4F: "chapter title jingle",
    0x5F: "dungeon/cave music",
    0x60: "town music",
    0x61: "screen load SFX",
    0x62: "RPG battle init",
    0x63: "credits/ending music",
    0x64: "credits phase music",
    0x65: "victory/clear music",
    0x66: "game clear music",
    0x67: "object interact SFX",
    0x68: "story event music",
    0x6E: "RPG battle music (boss?)",
    0x71: "RPG magic cast",
    0x73: "RPG special fanfare",
    0x75: "area transition music",
    0x77: "RPG battle music (standard)",
    0x79: "RPG victory music",
    0x7A: "music driver SFX",
    0x7B: "dungeon event music",
    0x7D: "text scroll SFX",
    0x7E: "entity spawn jingle",
    0x7F: "RPG boss battle music",
    0x80: "music init",
    0x83: "HP restore SFX",
    0x84: "magic cast SFX",
}

for sid in sorted(set(list(range(0x90)))):
    byte = rom[PRIO_TABLE + sid]
    priority = byte & 0x3F
    channel = (byte >> 6) & 0x03
    if priority == 0:
        continue
    ch_label = CHANNEL_SHORT[channel]
    ctx = context.get(sid, "")
    print(f"  ${sid:02X}  {ch_label:7s}  pri={pri:2d}  {ctx}")
