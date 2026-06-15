#!/usr/bin/env python3
"""Parse bank 0 display screen-data: index table at $BBA1 + layout streams at $B3A0-$BAFF.

Consumer (bank 0 $B097-$B109):
  X = screen_param * 2
  data_lo = $A0 + byte[$BBA2 + X]
  data_hi = ($B3 + (byte[$BBA1 + X] & 7)) + carry
  => stream address. Stream is a tile/text layout bytecode read by $B0D9 loop:
     $2F = end of stream, $2E = row advance, $30-$7F = tile/char (stored),
     $2C = stored char (space), $00-$2B = PPU-write command (+$E0 -> $B331),
     $80-$8A = special (JSR $B241), $8B-$FF = stored raw tile.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

ROM = os.path.join(os.path.dirname(__file__), "..", "roms", "TMOS_ORIGINAL.nes")
HDR = 16
BANK0 = HDR  # bank 0 file offset of $8000

def b0(addr):
    """byte at bank 0 CPU addr ($8000-$BFFF)."""
    return DATA[BANK0 + (addr - 0x8000)]

with open(ROM, "rb") as f:
    DATA = f.read()

# tile -> char map (from REVERSE.md text encoding)
def tile_char(v):
    if 0x00 <= v <= 0x09: return chr(ord('0') + v)
    if 0x30 <= v <= 0x49: return chr(ord('A') + (v - 0x30))
    if v == 0x2C: return ' '
    if v == 0x4F: return '-'
    return None

def decode_stream(addr, maxlen=512):
    """Return (rows, raw_bytes, end_addr)."""
    rows = []
    cur = []
    raw = []
    a = addr
    for _ in range(maxlen):
        b = b0(a); a += 1; raw.append(b)
        if b == 0x2F:        # end
            break
        if b == 0x2E:        # row advance
            rows.append(cur); cur = []
            continue
        if b < 0x2C:         # PPU-write command byte
            cur.append("<%02X>" % b)
            continue
        if b >= 0x80:
            cur.append("[%02X]" % b)
            continue
        c = tile_char(b)
        cur.append(c if c else "{%02X}" % b)
    if cur: rows.append(cur)
    return rows, raw, a

def parse_index(n=32):
    """Index entries: (page_flags_byte @ $BBA1+2i, lo_byte @ $BBA2+2i)."""
    out = []
    for i in range(n):
        x = i * 2
        flags = b0(0xBBA1 + x)
        lo = b0(0xBBA2 + x)
        page_off = flags & 0x07
        b1f1_idx = (flags >> 3) & 0x03
        hi_flags = flags >> 5
        data_lo = (0xA0 + lo)
        carry = data_lo >> 8
        data_lo &= 0xFF
        data_hi = 0xB3 + page_off + carry
        addr = (data_hi << 8) | data_lo
        out.append((i, flags, lo, page_off, b1f1_idx, hi_flags, addr))
    return out

print("=== Index table $BBA1 (32 entries x 2B) ===")
print("idx flags lo  page b1f1 hi  -> addr   in-range  text")
entries = parse_index(32)
for (i, flags, lo, page_off, b1f1, hi, addr) in entries:
    inrange = "yes" if 0xB3A0 <= addr <= 0xBAFF else "OUT"
    text = ""
    if 0xB3A0 <= addr <= 0xBAFF:
        rows, raw, end = decode_stream(addr)
        flat = " / ".join("".join(r) for r in rows)
        text = flat[:60]
    print("%2d  $%02X  $%02X  %d    %d    %d   $%04X  %-7s %s" %
          (i, flags, lo, page_off, b1f1, hi, addr, inrange, text))
