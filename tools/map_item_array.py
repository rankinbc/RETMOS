#!/usr/bin/env python3
"""Map the $03C0 item/spell ownership array via chapter-warp init data.

Chapter warp data: bank 6 $BB1F, 7-byte records [addr_lo, addr_hi, ch0..ch4],
$FF sentinel. Records targeting $03C0-$03DF show each slot's per-chapter init,
revealing the array layout (2 bytes per item index = code low-nibble).
"""
import os
ROM = os.path.join(os.path.dirname(__file__), "..", "roms", "TMOS_ORIGINAL.nes")
HDR = 16
with open(ROM, "rb") as f:
    DATA = f.read()

def rd(bank, addr):
    return DATA[HDR + bank * 0x4000 + (addr - 0x8000)]

a = 0xBB1F
print("All chapter-warp records (bank 6 $BB1F), full $03xx state init:")
print("addr     ch0 ch1 ch2 ch3 ch4")
arr = {}
while True:
    lo = rd(6, a); hi = rd(6, a + 1)
    if lo == 0xFF:
        break
    addr = lo | (hi << 8)
    chvals = [rd(6, a + 2 + j) for j in range(5)]
    if 0x0300 <= addr <= 0x03DF:
        tag = ""
        if 0x03C0 <= addr <= 0x03DF:
            tag = "  <- item-array idx %d" % ((addr - 0x03C0) // 2) + (".hi" if (addr - 0x03C0) % 2 else ".lo")
        print("$%04X    %s%s" % (addr, " ".join("%3d" % v for v in chvals), tag))
    a += 7
