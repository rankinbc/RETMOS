#!/usr/bin/env python3
"""Scan all bank 2 VM scripts for shop signatures (NUMINPUT, gold/item STOREs)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import dis_script as D

# entry pointers live in bank 1 type sub-tables $9046..$908F
def ptr(bank, addr):
    return D.rd(bank, addr) | (D.rd(bank, addr + 1) << 8)

entries = [ptr(1, 0x9046 + 2 * i) for i in range(37)]

def walk(bank, start, maxops=80):
    """Linear walk collecting opcodes + interesting operands until RET/JUMP/bad."""
    a = start; ops_seen = []; notable = []
    seen = set()
    for _ in range(maxops):
        if a in seen: break
        seen.add(a)
        opc = D.rd(bank, a)
        if opc not in D.OPS: break
        name, n = D.OPS[opc]
        operands = [D.rd(bank, a + 1 + i) for i in range(n)]
        ops_seen.append(name)
        if name == "NUMINPUT":
            notable.append("NUMINPUT@$%04X" % a)
        if name in ("STORE", "IF"):
            tgt = D.resolve(operands[0])
            if tgt in (0x0306, 0x0307, 0x0308, 0x0309, 0x030A, 0x030F, 0x0310,
                       0x0311, 0x0312) or 0x03E0 <= tgt <= 0x03E4:
                notable.append("%s[$%04X]@$%04X" % (name, tgt, a))
        if name in ("JUMP", "RET"): break
        a = a + 1 + n
    return ops_seen, notable

print("entry   opcodes(uniq)                          notable")
for e in entries:
    ops, notable = walk(2, e)
    uniq = []
    for o in ops:
        if o not in uniq: uniq.append(o)
    flag = " <<<" if ("NUMINPUT" in ops or notable) else ""
    print("$%04X  %-40s %s%s" % (e, ",".join(uniq)[:40], " ".join(notable), flag))
