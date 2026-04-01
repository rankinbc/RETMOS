#!/usr/bin/env python3
"""
Byte pattern search in NES ROM.

Usage:
  python3 tools/search_bytes.py <hex_pattern> [--context N] [--disasm [N]]

  hex_pattern - hex bytes, spaces optional (e.g. "4C9BE1" or "4C 9B E1")
  --context N - show N bytes of context around each match (default 0)
  --disasm [N] - disassemble N bytes at each match location (default 16)
  --prg        - search only PRG ROM (skip header and CHR)
  --chr        - search only CHR ROM
  --bank B     - restrict search to PRG bank B

Examples:
  python3 tools/search_bytes.py "4C 9B E1"           # Find JMP $E19B
  python3 tools/search_bytes.py "20 C9 E3" --disasm  # Find JSR NMI with disasm
  python3 tools/search_bytes.py "A9 00" --bank 7     # LDA #$00 in bank 7 only
"""

import sys
import os
import csv

ROM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "roms", "TMOS_ORIGINAL.nes")
LABELS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "labels.csv")

INES_HEADER_SIZE = 16
PRG_BANK_SIZE = 16384
PRG_BANKS = 8
CHR_BANK_SIZE = 8192
CHR_BANKS = 16

PRG_START = INES_HEADER_SIZE
PRG_END = PRG_START + PRG_BANKS * PRG_BANK_SIZE
CHR_START = PRG_END
CHR_END = CHR_START + CHR_BANKS * CHR_BANK_SIZE


def file_offset_to_bank_addr(offset):
    """Convert file offset to (bank, cpu_addr) or (region, offset) for non-PRG."""
    if offset < INES_HEADER_SIZE:
        return ("header", offset)
    elif offset < PRG_END:
        prg_offset = offset - INES_HEADER_SIZE
        bank = prg_offset // PRG_BANK_SIZE
        offset_in_bank = prg_offset % PRG_BANK_SIZE
        if bank == 7:
            cpu_addr = 0xC000 + offset_in_bank
        else:
            cpu_addr = 0x8000 + offset_in_bank
        return (bank, cpu_addr)
    elif offset < CHR_END:
        chr_offset = offset - CHR_START
        chr_bank = chr_offset // CHR_BANK_SIZE
        return (f"CHR{chr_bank}", chr_offset % CHR_BANK_SIZE)
    else:
        return ("???", offset)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    # Parse arguments
    hex_pattern = ""
    context_bytes = 0
    disasm_bytes = 0
    prg_only = False
    chr_only = False
    bank_filter = None
    i = 0
    while i < len(args):
        if args[i] == "--context":
            i += 1
            context_bytes = int(args[i])
        elif args[i] == "--disasm":
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                i += 1
                disasm_bytes = int(args[i])
            else:
                disasm_bytes = 16
        elif args[i] == "--prg":
            prg_only = True
        elif args[i] == "--chr":
            chr_only = True
        elif args[i] == "--bank":
            i += 1
            bank_filter = int(args[i])
        else:
            hex_pattern += args[i].replace(" ", "")
        i += 1

    # Parse hex pattern
    if len(hex_pattern) % 2 != 0:
        print(f"ERROR: Odd number of hex digits: {hex_pattern}")
        sys.exit(1)
    pattern = bytes.fromhex(hex_pattern)
    if not pattern:
        print("ERROR: Empty pattern")
        sys.exit(1)

    # Load ROM
    with open(ROM_PATH, "rb") as f:
        rom_data = f.read()

    # Determine search range
    if prg_only:
        search_start, search_end = PRG_START, PRG_END
    elif chr_only:
        search_start, search_end = CHR_START, CHR_END
    elif bank_filter is not None:
        search_start = INES_HEADER_SIZE + bank_filter * PRG_BANK_SIZE
        search_end = search_start + PRG_BANK_SIZE
    else:
        search_start, search_end = 0, len(rom_data)

    # Search
    matches = []
    pos = search_start
    while pos < search_end:
        idx = rom_data.find(pattern, pos, search_end)
        if idx == -1:
            break
        matches.append(idx)
        pos = idx + 1

    print(f"Pattern: {' '.join(f'{b:02X}' for b in pattern)}")
    print(f"Matches: {len(matches)}")
    print()

    # Import disassembler if needed
    if disasm_bytes > 0:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from instruction_set import decode_instruction, format_operand

    for match_offset in matches:
        bank_addr = file_offset_to_bank_addr(match_offset)
        bank, addr = bank_addr

        if isinstance(bank, int):
            loc_str = f"Bank {bank} ${addr:04X}"
        else:
            loc_str = f"{bank} offset 0x{addr:04X}"

        print(f"  0x{match_offset:05X} ({loc_str}):")

        # Show context
        if context_bytes > 0:
            ctx_start = max(0, match_offset - context_bytes)
            ctx_end = min(len(rom_data), match_offset + len(pattern) + context_bytes)
            ctx_data = rom_data[ctx_start:ctx_end]
            hex_ctx = " ".join(f"{b:02X}" for b in ctx_data)
            # Mark the match region
            pre_len = match_offset - ctx_start
            match_hex = " ".join(f"{b:02X}" for b in ctx_data[pre_len:pre_len + len(pattern)])
            print(f"    Context: ...{hex_ctx}...")
            print(f"    Match at byte {pre_len}: [{match_hex}]")

        # Disassemble at match
        if disasm_bytes > 0 and isinstance(bank, int):
            data = rom_data[match_offset:match_offset + disasm_bytes]
            pc = addr
            offset = 0
            while offset < len(data):
                result = decode_instruction(data, offset)
                if result is None:
                    print(f"    ${pc:04X}: {data[offset]:02X}          .db ${data[offset]:02X}")
                    offset += 1
                    pc += 1
                    continue
                mnemonic, mode, nbytes_i, operand_bytes = result
                raw = data[offset:offset + nbytes_i]
                hex_str = " ".join(f"{b:02X}" for b in raw)
                operand_str = format_operand(mode, operand_bytes, pc)
                instr = f"{mnemonic} {operand_str}" if operand_str else mnemonic
                print(f"    ${pc:04X}: {hex_str:<10s} {instr}")
                offset += nbytes_i
                pc += nbytes_i
            print()


if __name__ == "__main__":
    main()
