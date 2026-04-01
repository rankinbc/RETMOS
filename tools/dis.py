#!/usr/bin/env python3
"""
NES banked ROM disassembler.
Auto-loads labels.csv for annotation.

Usage:
  python3 tools/dis.py <bank> <addr> [nbytes]

  bank  - PRG ROM bank number (0-7), or 'c'/'fixed' for the fixed bank 7
  addr  - CPU address in hex (e.g. E19B or 0xE19B)
  nbytes - number of bytes to disassemble (default 64)

Examples:
  python3 tools/dis.py 7 E19B 48       # RESET vector, 48 bytes
  python3 tools/dis.py 0 8000 32       # Start of bank 0
  python3 tools/dis.py fixed E3C9 64   # NMI handler in fixed bank
"""

import sys
import os
import csv

# ROM layout
INES_HEADER_SIZE = 16
PRG_BANK_SIZE = 16384  # 16KB
PRG_BANKS = 8
CHR_BANK_SIZE = 8192   # 8KB

ROM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "roms", "TMOS_ORIGINAL.nes")
LABELS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "labels.csv")

# Import instruction set
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from instruction_set import OPCODES, format_operand, get_target_addr, decode_instruction


def load_labels():
    """Load labels.csv -> dict of (bank_or_star, addr_int) -> (name, comment)"""
    labels = {}
    if not os.path.exists(LABELS_PATH):
        return labels
    with open(LABELS_PATH, "r") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            bank_str, addr_str, name = row[0].strip(), row[1].strip(), row[2].strip()
            comment = row[3].strip() if len(row) > 3 else ""
            try:
                addr = int(addr_str, 16)
            except ValueError:
                continue
            labels[(bank_str, addr)] = (name, comment)
    return labels


def lookup_label(labels, bank, addr):
    """Look up a label by bank+addr, also checks wildcard bank '*'."""
    bank_str = str(bank)
    result = labels.get((bank_str, addr))
    if result:
        return result
    result = labels.get(("*", addr))
    if result:
        return result
    # Also try matching any bank for addresses in the fixed bank range
    if 0xC000 <= addr <= 0xFFFF:
        result = labels.get(("7", addr))
        if result:
            return result
    return None


def addr_to_file_offset(bank, addr):
    """Convert bank + CPU address to file offset in the ROM."""
    if bank == 7 or (0xC000 <= addr <= 0xFFFF):
        # Fixed bank at $C000-$FFFF
        actual_bank = 7
        offset_in_bank = addr - 0xC000
    else:
        # Switchable bank at $8000-$BFFF
        actual_bank = bank
        offset_in_bank = addr - 0x8000

    if offset_in_bank < 0 or offset_in_bank >= PRG_BANK_SIZE:
        return None

    return INES_HEADER_SIZE + (actual_bank * PRG_BANK_SIZE) + offset_in_bank


def disassemble(rom_data, bank, start_addr, nbytes, labels):
    """Disassemble nbytes starting at bank:start_addr."""
    file_offset = addr_to_file_offset(bank, start_addr)
    if file_offset is None:
        print(f"ERROR: Cannot map bank {bank} addr ${start_addr:04X} to file offset")
        return

    data = rom_data[file_offset:file_offset + nbytes]
    if not data:
        print(f"ERROR: No data at file offset 0x{file_offset:05X}")
        return

    pc = start_addr
    i = 0

    while i < len(data):
        addr = pc

        # Check for label at this address
        label_info = lookup_label(labels, bank, addr)
        if label_info:
            name, comment = label_info
            if name:
                label_comment = f"  ; {comment}" if comment else ""
                print(f"\n{name}:{label_comment}")

        # Decode instruction
        result = decode_instruction(data, i)
        if result is None:
            # Unknown opcode - show as .db
            byte_val = data[i]
            print(f"  ${addr:04X}:  {byte_val:02X}          .db ${byte_val:02X}")
            i += 1
            pc += 1
            continue

        mnemonic, mode, nbytes_instr, operand_bytes = result

        # Build hex bytes string
        raw_bytes = data[i:i + nbytes_instr]
        hex_str = " ".join(f"{b:02X}" for b in raw_bytes)

        # Format operand with label substitution
        operand_str = format_operand(mode, operand_bytes, addr)
        target = get_target_addr(mode, operand_bytes, addr)

        # Label annotation
        annotation = ""
        if target is not None and target >= 0x100:  # Skip ZP for annotations
            target_label = lookup_label(labels, bank, target)
            if target_label and target_label[0]:
                annotation = f"  ; -> {target_label[0]}"
                if target_label[1]:
                    annotation += f" ({target_label[1]})"

        # Format output
        hex_padded = f"{hex_str:<10s}"
        if operand_str:
            instr_str = f"{mnemonic} {operand_str}"
        else:
            instr_str = mnemonic

        print(f"  ${addr:04X}:  {hex_padded} {instr_str}{annotation}")

        i += nbytes_instr
        pc += nbytes_instr


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    bank_arg = sys.argv[1]
    addr_arg = sys.argv[2]
    nbytes = int(sys.argv[3], 0) if len(sys.argv) > 3 else 64

    # Parse bank
    if bank_arg.lower() in ("c", "fixed", "f"):
        bank = 7
    else:
        bank = int(bank_arg)

    # Parse address
    addr = int(addr_arg, 16)

    # Auto-fix: if addr is in $C000-$FFFF range, use bank 7
    if 0xC000 <= addr <= 0xFFFF:
        bank = 7

    # Load ROM
    with open(ROM_PATH, "rb") as f:
        rom_data = f.read()

    labels = load_labels()

    file_off = addr_to_file_offset(bank, addr)
    print(f"; Bank {bank} ${addr:04X} (file offset 0x{file_off:05X}), {nbytes} bytes")
    print(f"; ---")
    disassemble(rom_data, bank, addr, nbytes, labels)


if __name__ == "__main__":
    main()
