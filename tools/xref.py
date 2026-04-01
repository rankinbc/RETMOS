#!/usr/bin/env python3
"""
Cross-reference finder for NES ROM.
Finds all references (calls, jumps, loads, stores) to a given address.
Bank-aware: cross-bank byte matches are filtered when bank specified.

Usage:
  python3 tools/xref.py <addr> [bank] [options]

  addr   - target CPU address in hex (e.g. E19B)
  bank   - optional: restrict to references FROM this bank only
  --code - only scan known code regions (faster)
  -r START END - restrict scan to file byte range
  -c N   - show N bytes of context/disasm at each reference

Examples:
  python3 tools/xref.py E19B           # All refs to RESET vector
  python3 tools/xref.py E3C9 7         # Refs to NMI from bank 7 only
  python3 tools/xref.py 8000 0 -c 8    # Refs to bank 0 $8000 with context
"""

import sys
import os

ROM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "roms", "TMOS_ORIGINAL.nes")
LABELS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "labels.csv")

INES_HEADER_SIZE = 16
PRG_BANK_SIZE = 16384
PRG_BANKS = 8

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instruction_set import OPCODES, decode_instruction, format_operand, get_target_addr


def file_offset_to_bank_addr(offset):
    """Convert file offset to (bank, cpu_addr)."""
    if offset < INES_HEADER_SIZE:
        return None
    prg_offset = offset - INES_HEADER_SIZE
    if prg_offset >= PRG_BANKS * PRG_BANK_SIZE:
        return None  # CHR region
    bank = prg_offset // PRG_BANK_SIZE
    offset_in_bank = prg_offset % PRG_BANK_SIZE
    if bank == 7:
        cpu_addr = 0xC000 + offset_in_bank
    else:
        cpu_addr = 0x8000 + offset_in_bank
    return (bank, cpu_addr)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    target_addr = int(args[0], 16)
    bank_filter = None
    code_only = False
    range_start = None
    range_end = None
    context = 0

    i = 1
    while i < len(args):
        if args[i] == "--code":
            code_only = True
        elif args[i] == "-r":
            range_start = int(args[i + 1], 0)
            range_end = int(args[i + 2], 0)
            i += 2
        elif args[i] == "-c":
            context = int(args[i + 1])
            i += 1
        else:
            try:
                bank_filter = int(args[i])
            except ValueError:
                pass
        i += 1

    # Load ROM
    with open(ROM_PATH, "rb") as f:
        rom_data = f.read()

    # Target as little-endian bytes (for absolute addressing matches)
    target_lo = target_addr & 0xFF
    target_hi = (target_addr >> 8) & 0xFF

    # Search range
    prg_end = INES_HEADER_SIZE + PRG_BANKS * PRG_BANK_SIZE
    if range_start is not None:
        scan_start = range_start
        scan_end = range_end
    else:
        scan_start = INES_HEADER_SIZE
        scan_end = prg_end  # Only scan PRG ROM

    # Collect labels for annotation
    import csv
    labels = {}
    if os.path.exists(LABELS_PATH):
        with open(LABELS_PATH, "r") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    try:
                        a = int(row[1].strip(), 16)
                        labels[a] = row[2].strip()
                    except ValueError:
                        pass

    target_name = labels.get(target_addr, f"${target_addr:04X}")
    print(f"Cross-references to {target_name} (${target_addr:04X}):")
    print()

    results = []

    # Scan instruction-by-instruction through each bank
    for bank in range(PRG_BANKS):
        if bank_filter is not None and bank != bank_filter:
            continue

        bank_file_start = INES_HEADER_SIZE + bank * PRG_BANK_SIZE
        bank_file_end = bank_file_start + PRG_BANK_SIZE

        if bank_file_start >= scan_end or bank_file_end <= scan_start:
            continue

        actual_start = max(bank_file_start, scan_start)
        actual_end = min(bank_file_end, scan_end)

        offset = actual_start
        while offset < actual_end:
            result = decode_instruction(rom_data, offset)
            if result is None:
                offset += 1
                continue

            mnemonic, mode, nbytes, operand_bytes = result
            ba = file_offset_to_bank_addr(offset)
            if ba is None:
                offset += 1
                continue

            src_bank, src_addr = ba
            target = get_target_addr(mode, operand_bytes, src_addr)

            if target == target_addr:
                raw = rom_data[offset:offset + nbytes]
                hex_str = " ".join(f"{b:02X}" for b in raw)
                operand_str = format_operand(mode, operand_bytes, src_addr)
                instr = f"{mnemonic} {operand_str}" if operand_str else mnemonic

                ref_type = "call" if mnemonic == "JSR" else \
                           "jump" if mnemonic in ("JMP", "BPL", "BMI", "BVC", "BVS",
                                                   "BCC", "BCS", "BNE", "BEQ") else \
                           "load" if mnemonic in ("LDA", "LDX", "LDY") else \
                           "store" if mnemonic in ("STA", "STX", "STY") else \
                           "read" if mnemonic in ("BIT", "CMP", "CPX", "CPY",
                                                   "ORA", "AND", "EOR", "ADC", "SBC") else \
                           "rmw" if mnemonic in ("INC", "DEC", "ASL", "LSR",
                                                  "ROL", "ROR") else "ref"

                src_label = labels.get(src_addr, "")
                label_str = f" ({src_label})" if src_label else ""

                results.append((src_bank, src_addr, ref_type, instr, hex_str, label_str))

            offset += nbytes

    # Also do a raw byte scan for the little-endian address bytes
    # (catches data references like pointer tables)
    if target_addr >= 0x100:  # Only for 16-bit addresses
        pos = scan_start
        while pos < scan_end - 1:
            if rom_data[pos] == target_lo and rom_data[pos + 1] == target_hi:
                ba = file_offset_to_bank_addr(pos)
                if ba:
                    src_bank, src_addr = ba
                    if bank_filter is not None and src_bank != bank_filter:
                        pos += 1
                        continue
                    # Check if this was already found as an instruction operand
                    already = any(r[0] == src_bank and (r[1] <= src_addr <= r[1] + 2)
                                  for r in results)
                    if not already:
                        hex_str = f"{rom_data[pos]:02X} {rom_data[pos+1]:02X}"
                        results.append((src_bank, src_addr, "data", f".dw ${target_addr:04X}",
                                        hex_str, ""))
            pos += 1

    # Sort by bank, address
    results.sort(key=lambda r: (r[0], r[1]))

    if not results:
        print("  (no references found)")
    else:
        for src_bank, src_addr, ref_type, instr, hex_str, label_str in results:
            print(f"  Bank {src_bank} ${src_addr:04X}: [{ref_type:5s}] {hex_str:<10s} {instr}{label_str}")

            # Disassemble context if requested
            if context > 0:
                file_off = INES_HEADER_SIZE + src_bank * PRG_BANK_SIZE + (src_addr - (0xC000 if src_bank == 7 else 0x8000))
                ctx_start = max(INES_HEADER_SIZE, file_off - context)
                ctx_data = rom_data[ctx_start:file_off + context]
                ctx_hex = " ".join(f"{b:02X}" for b in ctx_data)
                print(f"           context: {ctx_hex}")

    print(f"\nTotal: {len(results)} references")


if __name__ == "__main__":
    main()
