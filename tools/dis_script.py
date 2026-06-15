#!/usr/bin/env python3
"""Disassemble bank 2 Script VM bytecode (the dialogue/shop/password/event VM).

VM: main loop bank 2 $AA1D, opcode jump table $AC9D (14 opcodes), script ptr $CE/$CF.
Operand bytes consumed after each opcode (from the $ACBD LDX #n in each handler):

  0  BLOCK     terminator/exec-block (reads 2-byte ptr, $0000 = end of script)
  1  SOUND     id                      -> queue_sound
  2  CHR       mode                    -> $38
  3  JUMP      addr16                  -> $CE/$CF (goto)
  4  CALL      addr16                  exec sub-block, continue
  5  STORE     addr8, val8             write val to resolved game-state addr
  6  TEXTBOX   ppu_lo, ppu_hi, flags   render text window
  7  TEXTINIT  param                   text_data_init
  8  LOADTEXT  addr16                  load text entry, set script ptr
  9  IF        addr8,cmp8,fl,gtL,gtH,eqL,eqH  compare+3-way branch (+writeback)
  10 WINDOW    type, param             set window type
  11 NUMINPUT  a, b, c                 numeric (buy-quantity) input
  12 PWDCHK    addr16                  password secret check
  13 RET       (none)                  return (restore $CE/$CF)

Operand byte 0 of STORE/IF encodes an address: bits 7-5 index base table $ACF8,
bits 4-0 = offset.  Bases: $00A0 $0300 $0320 $0080 $0480 $03E0.
"""
import sys, os
ROM = os.path.join(os.path.dirname(__file__), "..", "roms", "TMOS_ORIGINAL.nes")
HDR = 16
with open(ROM, "rb") as f:
    DATA = f.read()

def rd(bank, addr):
    return DATA[HDR + bank * 0x4000 + (addr - 0x8000)]

ADDR_BASE = [0x00A0, 0x0300, 0x0320, 0x0080, 0x0480, 0x03E0, 0x0000, 0x0000]

def resolve(op0):
    base = ADDR_BASE[(op0 >> 5) & 7]
    return base + (op0 & 0x1F)

# opcode name + fixed operand byte count after opcode
OPS = {
    0:("BLOCK",2), 1:("SOUND",1), 2:("CHR",1), 3:("JUMP",2), 4:("CALL",2),
    5:("STORE",2), 6:("TEXTBOX",3), 7:("TEXTINIT",1), 8:("LOADTEXT",2),
    9:("IF",7), 10:("WINDOW",2), 11:("NUMINPUT",3), 12:("PWDCHK",2), 13:("RET",0),
}

def diss(bank, start, maxops=60):
    a = start
    out = []
    for _ in range(maxops):
        opc = rd(bank, a)
        if opc not in OPS:
            out.append("  $%04X: .db $%02X  ??? (not an opcode; likely end/data)" % (a, opc))
            break
        name, n = OPS[opc]
        ops = [rd(bank, a + 1 + i) for i in range(n)]
        a2 = a + 1 + n
        txt = "  $%04X: %-9s" % (a, name)
        if name in ("JUMP", "CALL", "LOADTEXT", "PWDCHK", "BLOCK"):
            tgt = ops[0] | (ops[1] << 8)
            txt += "$%04X" % tgt
        elif name == "STORE":
            txt += "[$%04X] = $%02X" % (resolve(ops[0]), ops[1])
        elif name == "IF":
            var = resolve(ops[0]); cmp = ops[1]; fl = ops[2]
            gt = ops[3] | (ops[4] << 8); eq = ops[5] | (ops[6] << 8)
            txt += "[$%04X] vs $%02X  fl=$%02X  >->$%04X  =->$%04X" % (var, cmp, fl, gt, eq)
        elif name in ("SOUND","CHR","TEXTINIT"):
            txt += "$%02X" % ops[0]
        elif ops:
            txt += " ".join("$%02X" % o for o in ops)
        out.append(txt)
        if name in ("JUMP", "RET"):     # unconditional control flow ends linear trace
            break
        a = a2
    return "\n".join(out)

if __name__ == "__main__":
    bank = int(sys.argv[1])
    addr = int(sys.argv[2], 16)
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    print("; Script VM disasm: bank %d $%04X" % (bank, addr))
    print(diss(bank, addr, mx))
