#!/usr/bin/env python3
"""Dump the bank 1 shop tables ($94ED pointer table -> $94FD shop data).

Each shop = 4 slots x 2 bytes = [code, price].
  code  = item identifier. Low nibble (code & $0F) = item index into the
          $03C0 ownership/count array (bank 1 $8A9A: "already owned?" check).
          High nibble = shop/item category ($1x,$3x = regular item, $5x = spell).
  price = gold cost (regular shops). Magic shops instead scale a base price
          from table $8AAC[code & $0F] by chapter via $8B89.

Literal item-NAME strings are not a flat code-indexed table; they are part of
each shop's text-entry screen layout. This dump shows the structural decode.
"""
import sys, os
ROM = os.path.join(os.path.dirname(__file__), "..", "roms", "TMOS_ORIGINAL.nes")
HDR = 16
with open(ROM, "rb") as f:
    DATA = f.read()

def rd(bank, addr):
    return DATA[HDR + bank * 0x4000 + (addr - 0x8000)]

def ptr(bank, addr):
    return rd(bank, addr) | (rd(bank, addr + 1) << 8)

CAT = {0x1: "item", 0x3: "item", 0x5: "spell"}

# magic-shop base price table $8AAC (until code re-use at $8AB7)
MAGIC_PRICES = [rd(1, 0x8AAC + i) for i in range(11)]

print("Shop-pointer table $94ED (8 shops, indexed by shop id $04E1)")
print("Shop data $94FD  ([code, price] x 4 slots)\n")
print("shop  ptr    slot:  code(cat/idx) price   ...")
for s in range(8):
    p = ptr(1, 0x94ED + s * 2)
    slots = []
    for i in range(4):
        code = rd(1, p + i * 2)
        price = rd(1, p + i * 2 + 1)
        cat = CAT.get(code >> 4, "?%X" % (code >> 4))
        idx = code & 0x0F
        slots.append("$%02X(%s/%d)=%d" % (code, cat, idx, price))
    print("  %d  $%04X  %s" % (s, p, "  ".join(slots)))

print("\nMagic-shop base price table $8AAC[idx] (x chapter via $8B89):")
print("  " + " ".join("%d:%d" % (i, v) for i, v in enumerate(MAGIC_PRICES)))
