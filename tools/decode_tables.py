#!/usr/bin/env python3
"""
Table/struct decoder for NES ROM.

Usage:
  python3 tools/decode_tables.py <bank> <addr> <count> <fmt> [options]

  bank   - PRG bank (0-7) or 'c' for CHR region
  addr   - start address in hex
  count  - number of entries to decode
  fmt    - format: u8, s8, u16, s16, ptr16, nullstr, b8 (binary)
           struct:<stride>:<field_list>
  --follow N FMT - for ptr16: follow pointers, read N bytes using FMT
  --chr          - address is CHR ROM offset (not CPU address)

Formats:
  u8       - unsigned byte
  s8       - signed byte
  u16      - unsigned 16-bit little-endian
  s16      - signed 16-bit little-endian
  ptr16    - 16-bit pointer (little-endian), displayed as $XXXX
  nullstr  - null-terminated string (raw bytes, not ASCII)
  b8       - byte as binary (8 bits)
  struct:<stride>:<f1,f2,...>  - struct with named fields
    each field: name:type or name:type:offset
    types: u8, s8, u16, s16, ptr16, b8

Examples:
  python3 tools/decode_tables.py 7 FFF0 8 u16
  python3 tools/decode_tables.py 0 8000 16 u8
  python3 tools/decode_tables.py 7 E000 4 ptr16 --follow 8 u8
  python3 tools/decode_tables.py 3 8000 5 struct:8:x:u8,y:u8,tile:u8,attr:u8
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
PRG_END = INES_HEADER_SIZE + PRG_BANKS * PRG_BANK_SIZE
CHR_START = PRG_END


def addr_to_file_offset(bank, addr, is_chr=False):
    """Convert bank + address to file offset."""
    if is_chr:
        return CHR_START + addr
    if bank == 7 or (0xC000 <= addr <= 0xFFFF):
        return INES_HEADER_SIZE + 7 * PRG_BANK_SIZE + (addr - 0xC000)
    else:
        return INES_HEADER_SIZE + bank * PRG_BANK_SIZE + (addr - 0x8000)


def load_labels():
    labels = {}
    if not os.path.exists(LABELS_PATH):
        return labels
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
    return labels


def read_u8(data, off):
    return data[off] if off < len(data) else 0

def read_s8(data, off):
    v = read_u8(data, off)
    return v - 256 if v >= 128 else v

def read_u16(data, off):
    if off + 1 >= len(data):
        return 0
    return data[off] | (data[off + 1] << 8)

def read_s16(data, off):
    v = read_u16(data, off)
    return v - 65536 if v >= 32768 else v


def decode_value(data, off, fmt):
    """Decode a value at offset. Returns (formatted_string, bytes_consumed)."""
    if fmt == "u8":
        return f"${read_u8(data, off):02X} ({read_u8(data, off):3d})", 1
    elif fmt == "s8":
        return f"${read_u8(data, off):02X} ({read_s8(data, off):4d})", 1
    elif fmt == "u16":
        v = read_u16(data, off)
        return f"${v:04X} ({v:5d})", 2
    elif fmt == "s16":
        v = read_u16(data, off)
        return f"${v:04X} ({read_s16(data, off):6d})", 2
    elif fmt == "ptr16":
        v = read_u16(data, off)
        return f"${v:04X}", 2
    elif fmt == "b8":
        v = read_u8(data, off)
        return f"{v:08b} (${v:02X})", 1
    elif fmt == "nullstr":
        end = off
        while end < len(data) and data[end] != 0:
            end += 1
        raw = data[off:end]
        hex_str = " ".join(f"{b:02X}" for b in raw[:32])
        consumed = end - off + 1  # include null terminator
        return f"[{len(raw)} bytes] {hex_str}", consumed
    return f"???", 1


FMT_SIZE = {"u8": 1, "s8": 1, "u16": 2, "s16": 2, "ptr16": 2, "b8": 1}


def main():
    args = sys.argv[1:]
    if len(args) < 4:
        print(__doc__)
        sys.exit(1)

    bank_arg = args[0]
    addr = int(args[1], 16)
    count = int(args[2])
    fmt = args[3]

    is_chr = False
    follow_n = 0
    follow_fmt = ""

    if bank_arg.lower() in ("c", "chr"):
        is_chr = True
        bank = 0
    elif bank_arg.lower() in ("fixed", "f"):
        bank = 7
    else:
        bank = int(bank_arg)

    # Parse options
    i = 4
    while i < len(args):
        if args[i] == "--follow":
            follow_n = int(args[i + 1])
            follow_fmt = args[i + 2]
            i += 3
        elif args[i] == "--chr":
            is_chr = True
            i += 1
        else:
            i += 1

    # Load ROM
    with open(ROM_PATH, "rb") as f:
        rom_data = f.read()

    labels = load_labels()
    file_offset = addr_to_file_offset(bank, addr, is_chr)

    region = "CHR" if is_chr else f"Bank {bank}"
    print(f"; {region} ${addr:04X} (file 0x{file_offset:05X}), {count} x {fmt}")
    print()

    # Handle struct format
    if fmt.startswith("struct:"):
        parts = fmt.split(":", 2)
        stride = int(parts[1])
        fields_str = parts[2]
        fields = []
        for fd in fields_str.split(","):
            fparts = fd.split(":")
            fname = fparts[0]
            ftype = fparts[1] if len(fparts) > 1 else "u8"
            foff = int(fparts[2]) if len(fparts) > 2 else None
            fields.append((fname, ftype, foff))

        # Auto-assign offsets if not specified
        auto_off = 0
        for idx, (fname, ftype, foff) in enumerate(fields):
            if foff is None:
                fields[idx] = (fname, ftype, auto_off)
                foff = auto_off
            auto_off = foff + FMT_SIZE.get(ftype, 1)

        for entry_i in range(count):
            entry_addr = addr + entry_i * stride
            entry_file = file_offset + entry_i * stride
            label = labels.get(entry_addr, "")
            label_str = f" ({label})" if label else ""
            print(f"  [{entry_i:3d}] ${entry_addr:04X}{label_str}:")
            for fname, ftype, foff in fields:
                val_str, _ = decode_value(rom_data, entry_file + foff, ftype)
                print(f"         {fname:12s} = {val_str}")
        return

    # Simple format
    entry_size = FMT_SIZE.get(fmt, 1)
    off = file_offset
    current_addr = addr

    for entry_i in range(count):
        if fmt == "nullstr":
            val_str, consumed = decode_value(rom_data, off, fmt)
            label = labels.get(current_addr, "")
            label_str = f" ({label})" if label else ""
            print(f"  [{entry_i:3d}] ${current_addr:04X}: {val_str}{label_str}")
            off += consumed
            current_addr += consumed
        else:
            val_str, consumed = decode_value(rom_data, off, fmt)
            label = labels.get(current_addr, "")
            label_str = f" ({label})" if label else ""
            print(f"  [{entry_i:3d}] ${current_addr:04X}: {val_str}{label_str}")

            # Follow pointers
            if fmt == "ptr16" and follow_n > 0:
                ptr_val = read_u16(rom_data, off)
                # Try to follow - assume same bank for $8000-$BFFF, bank 7 for $C000+
                ptr_bank = 7 if ptr_val >= 0xC000 else bank
                ptr_file = addr_to_file_offset(ptr_bank, ptr_val)
                follow_addr = ptr_val
                print(f"        -> ${ptr_val:04X} (bank {ptr_bank}):")
                for fi in range(follow_n):
                    fval_str, fconsumed = decode_value(rom_data, ptr_file, follow_fmt)
                    print(f"           [{fi:2d}] ${follow_addr:04X}: {fval_str}")
                    ptr_file += fconsumed
                    follow_addr += fconsumed

            off += consumed
            current_addr += consumed


if __name__ == "__main__":
    main()
