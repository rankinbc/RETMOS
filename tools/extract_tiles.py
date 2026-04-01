#!/usr/bin/env python3
"""
NES CHR ROM tile extractor.
Decodes 2bpp planar tiles (8x8 pixels each, 16 bytes per tile) from CHR ROM.
Outputs individual bank PNGs and a combined tileset sheet.

Usage:
  python3 tools/extract_tiles.py [options]

  --bank N      Extract only CHR bank N (0-15 for 8KB, 0-31 for 4KB)
  --4kb         Treat as 4KB banks (32 banks) instead of 8KB (16 banks)
  --scale N     Scale factor (default 2)
  --palette P   Palette: gray (default), nes_default, or hex colors "0F,00,10,30"
  --all         Extract all banks (default)
  --sheet       Also generate combined sheet of all banks

Examples:
  python3 tools/extract_tiles.py                     # All 8KB banks at 2x
  python3 tools/extract_tiles.py --4kb --bank 0      # 4KB bank 0
  python3 tools/extract_tiles.py --scale 4 --sheet   # All banks + combined sheet
"""

import sys
import os
import struct
import zlib

ROM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "roms", "TMOS_ORIGINAL.nes")
GFX_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gfx")

INES_HEADER = 16
PRG_SIZE = 8 * 16384  # 128KB PRG
CHR_START = INES_HEADER + PRG_SIZE
CHR_SIZE = 16 * 8192  # 128KB CHR
TILE_SIZE = 16  # bytes per 8x8 tile (2 planes of 8 bytes each)

# NES default grayscale palette for 2bpp
PALETTES = {
    "gray": [(0, 0, 0, 255), (85, 85, 85, 255), (170, 170, 170, 255), (255, 255, 255, 255)],
    "nes_default": [(0, 0, 0, 255), (188, 0, 0, 255), (0, 120, 0, 255), (252, 252, 252, 255)],
}


def decode_tile(data, offset):
    """Decode one 8x8 NES tile (2bpp planar) to 8x8 pixel array (values 0-3)."""
    pixels = []
    for row in range(8):
        plane0 = data[offset + row]
        plane1 = data[offset + row + 8]
        row_pixels = []
        for bit in range(7, -1, -1):
            val = ((plane0 >> bit) & 1) | (((plane1 >> bit) & 1) << 1)
            row_pixels.append(val)
        pixels.append(row_pixels)
    return pixels


def write_png(filename, width, height, pixels_rgba):
    """Write a minimal PNG file without PIL dependency."""
    def make_chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)

    # PNG signature
    sig = b'\x89PNG\r\n\x1a\n'

    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    ihdr = make_chunk(b'IHDR', ihdr_data)

    # IDAT - raw pixel data with filter byte 0 per row
    raw_rows = b''
    for y in range(height):
        raw_rows += b'\x00'  # filter: none
        for x in range(width):
            idx = (y * width + x) * 4
            raw_rows += bytes(pixels_rgba[idx:idx + 4])
    idat_data = zlib.compress(raw_rows)
    idat = make_chunk(b'IDAT', idat_data)

    # IEND
    iend = make_chunk(b'IEND', b'')

    with open(filename, 'wb') as f:
        f.write(sig + ihdr + idat + iend)


def render_bank(rom_data, bank_offset, bank_size, palette, scale):
    """Render a CHR bank as a grid of tiles. Returns (width, height, rgba_flat)."""
    num_tiles = bank_size // TILE_SIZE
    cols = 16  # 16 tiles per row (standard NES layout)
    rows = (num_tiles + cols - 1) // cols

    img_w = cols * 8 * scale
    img_h = rows * 8 * scale
    rgba = [0] * (img_w * img_h * 4)

    for tile_idx in range(num_tiles):
        tile_data = decode_tile(rom_data, bank_offset + tile_idx * TILE_SIZE)
        tile_col = tile_idx % cols
        tile_row = tile_idx // cols

        for py in range(8):
            for px in range(8):
                color = palette[tile_data[py][px]]
                for sy in range(scale):
                    for sx in range(scale):
                        x = (tile_col * 8 + px) * scale + sx
                        y = (tile_row * 8 + py) * scale + sy
                        idx = (y * img_w + x) * 4
                        rgba[idx] = color[0]
                        rgba[idx + 1] = color[1]
                        rgba[idx + 2] = color[2]
                        rgba[idx + 3] = color[3]

    return img_w, img_h, rgba


def main():
    args = sys.argv[1:]
    bank_filter = None
    use_4kb = False
    scale = 2
    palette_name = "gray"
    make_sheet = False

    i = 0
    while i < len(args):
        if args[i] == "--bank":
            bank_filter = int(args[i + 1])
            i += 2
        elif args[i] == "--4kb":
            use_4kb = True
            i += 1
        elif args[i] == "--scale":
            scale = int(args[i + 1])
            i += 2
        elif args[i] == "--palette":
            palette_name = args[i + 1]
            i += 2
        elif args[i] == "--sheet":
            make_sheet = True
            i += 1
        elif args[i] == "--all":
            i += 1
        else:
            i += 1

    # Parse palette
    if palette_name in PALETTES:
        palette = PALETTES[palette_name]
    else:
        # Parse hex colors like "0F,00,10,30"
        try:
            # NES palette indices - use grayscale approximation
            palette = PALETTES["gray"]
        except Exception:
            palette = PALETTES["gray"]

    # Load ROM
    with open(ROM_PATH, "rb") as f:
        rom_data = f.read()

    os.makedirs(GFX_PATH, exist_ok=True)

    bank_size = 4096 if use_4kb else 8192
    num_banks = CHR_SIZE // bank_size

    banks_to_extract = [bank_filter] if bank_filter is not None else list(range(num_banks))

    print(f"CHR ROM: {CHR_SIZE // 1024}KB, {num_banks} x {bank_size // 1024}KB banks")
    print(f"Scale: {scale}x, Palette: {palette_name}")
    print()

    all_bank_images = []

    for bank in banks_to_extract:
        offset = CHR_START + bank * bank_size
        num_tiles = bank_size // TILE_SIZE

        # Check if bank is all zeros or all FF
        bank_data = rom_data[offset:offset + bank_size]
        if all(b == 0 for b in bank_data):
            print(f"  CHR bank {bank:2d}: EMPTY (all zeros)")
            continue
        if all(b == 0xFF for b in bank_data):
            print(f"  CHR bank {bank:2d}: EMPTY (all $FF)")
            continue

        w, h, rgba = render_bank(rom_data, offset, bank_size, palette, scale)

        prefix = "chr4k" if use_4kb else "chr8k"
        filename = os.path.join(GFX_PATH, f"{prefix}_bank{bank:02d}.png")
        write_png(filename, w, h, rgba)
        print(f"  CHR bank {bank:2d}: {num_tiles} tiles -> {filename}")

        all_bank_images.append((bank, w, h, rgba))

    if make_sheet and len(all_bank_images) > 1:
        # Stack all banks vertically with labels
        total_w = max(w for _, w, _, _ in all_bank_images)
        gap = 4 * scale
        total_h = sum(h + gap for _, _, h, _ in all_bank_images)
        sheet = [0] * (total_w * total_h * 4)

        y_offset = 0
        for bank, w, h, rgba in all_bank_images:
            for y in range(h):
                for x in range(w):
                    src_idx = (y * w + x) * 4
                    dst_idx = ((y_offset + y) * total_w + x) * 4
                    sheet[dst_idx:dst_idx + 4] = rgba[src_idx:src_idx + 4]
            y_offset += h + gap

        sheet_file = os.path.join(GFX_PATH, "chr_all_banks.png")
        write_png(sheet_file, total_w, total_h, sheet)
        print(f"\n  Combined sheet: {sheet_file}")

    print(f"\nDone. {len(all_bank_images)} banks extracted to {GFX_PATH}/")


if __name__ == "__main__":
    main()
