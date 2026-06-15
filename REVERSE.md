# The Magic of Scheherazade (NES/MMC1) -- Reverse Engineering Notes

## Binary Identification

| Field | Value |
|-------|-------|
| File | `roms/TMOS_ORIGINAL.nes` |
| Format | iNES (header: `4E 45 53 1A`) |
| Platform | NES (Nintendo Entertainment System) |
| CPU | Ricoh 2A03 (MOS 6502 variant, no BCD) |
| Mapper | 1 (MMC1 / SxROM) |
| PRG ROM | 8 x 16KB = 128KB |
| CHR ROM | 16 x 8KB = 128KB |
| Total file size | 262,160 bytes (256 KB) |
| Header size | 16 bytes |
| Mirroring | Horizontal (vertical arrangement) |
| Battery | No |
| RESET vector | $E19B (bank 7, fixed at $C000-$FFFF) |
| NMI vector | $E3C9 (bank 7) |
| IRQ vector | $E19B (same as RESET) |

---

## Memory Map

### CPU Address Space (Ricoh 2A03)

| Address Range | Size | Purpose |
|---------------|------|---------|
| $0000-$00FF | 256B | Zero Page RAM |
| $0100-$01FF | 256B | Stack |
| $0200-$07FF | 1.5KB | RAM |
| $0800-$1FFF | 6KB | RAM mirrors ($0000-$07FF x3) |
| $2000-$2007 | 8B | PPU registers |
| $2008-$3FFF | -- | PPU register mirrors |
| $4000-$4017 | 24B | APU + I/O registers |
| $4018-$5FFF | -- | Expansion area |
| $6000-$7FFF | 8KB | PRG RAM (if present) |
| $8000-$BFFF | 16KB | PRG ROM switchable bank (MMC1) |
| $C000-$FFFF | 16KB | PRG ROM fixed bank 7 |

### MMC1 Bank Configuration

| PRG Bank | File Offset | CPU Address | Notes |
|----------|-------------|-------------|-------|
| 0 | 0x00010-0x0400F | $8000-$BFFF | Switchable |
| 1 | 0x04010-0x0800F | $8000-$BFFF | Switchable |
| 2 | 0x08010-0x0C00F | $8000-$BFFF | Switchable |
| 3 | 0x0C010-0x1000F | $8000-$BFFF | Switchable |
| 4 | 0x10010-0x1400F | $8000-$BFFF | Switchable |
| 5 | 0x14010-0x1800F | $8000-$BFFF | Switchable |
| 6 | 0x18010-0x1C00F | $8000-$BFFF | Switchable |
| 7 | 0x1C010-0x2000F | $C000-$FFFF | Fixed |

### CHR ROM Banks

| CHR Bank | File Offset | PPU Address | Notes |
|----------|-------------|-------------|-------|
| 0 | 0x20010-0x2200F | $0000-$1FFF | 8KB mode, or split 4KB |
| 1 | 0x22010-0x2400F | $0000-$1FFF | |
| 2 | 0x24010-0x2600F | $0000-$1FFF | |
| 3 | 0x26010-0x2800F | $0000-$1FFF | |
| 4 | 0x28010-0x2A00F | $0000-$1FFF | |
| 5 | 0x2A010-0x2C00F | $0000-$1FFF | |
| 6 | 0x2C010-0x2E00F | $0000-$1FFF | |
| 7 | 0x2E010-0x3000F | $0000-$1FFF | |
| 8 | 0x30010-0x3200F | $0000-$1FFF | |
| 9 | 0x32010-0x3400F | $0000-$1FFF | |
| 10 | 0x34010-0x3600F | $0000-$1FFF | |
| 11 | 0x36010-0x3800F | $0000-$1FFF | |
| 12 | 0x38010-0x3A00F | $0000-$1FFF | |
| 13 | 0x3A010-0x3C00F | $0000-$1FFF | |
| 14 | 0x3C010-0x3E00F | $0000-$1FFF | |
| 15 | 0x3E010-0x4000F | $0000-$1FFF | |

---

## Data-Range Map

| Start | End | Size | Classification | Notes |
|-------|-----|------|----------------|-------|
| 0x00000 | 0x0000F | 16B | header | iNES header |
| 0x00010 | 0x0400F | 16KB | PRG bank 0 | Sound engine ($809E entry) |
| 0x04010 | 0x0800F | 16KB | PRG bank 1 | Screen/UI engine + dialogue text + dictionary |
| 0x08010 | 0x0C00F | 16KB | PRG bank 2 | Music data/driver ($B000 entry) |
| 0x0C010 | 0x1000F | 16KB | PRG bank 3 | RPG battle engine + encounter data |
| 0x10010 | 0x1400F | 16KB | PRG bank 4 | Screen/tile/entity data engine (see detailed map below) |
| 0x14010 | 0x1800F | 16KB | PRG bank 5 | Entity/sprite behavior engine |
| 0x18010 | 0x1C00F | 16KB | PRG bank 6 | Game logic (jump table at $8000) |
| 0x1C010 | 0x2000F | 16KB | PRG bank 7 | Core engine (fixed at $C000) |
| 0x20010 | 0x2A00F | 40KB | CHR 4KB 0-9 | Active tile graphics (fonts, sprites, BG) |
| 0x2A010 | 0x2C00F | 8KB | CHR 4KB 10-11 | Tile graphics (level themes) |
| 0x2C010 | 0x2E00F | 8KB | CHR 4KB 12-13 | Tile graphics (partial use, 13 in table) |
| 0x2E010 | 0x3000F | 8KB | CHR 4KB 14-15 | Tile graphics (14 in table) |
| 0x30010 | 0x3200F | 8KB | CHR 4KB 16-17 | Tile graphics (16 in table) |
| 0x32010 | 0x3600F | 16KB | CHR 4KB 18-19 | Tile graphics via dynamic CHR switching |
| 0x36010 | 0x3700F | 4KB | CHR 4KB 20 | Tile graphics (in bank table as CHR0=$14) |
| 0x35010 | 0x3600F | 4KB | CHR 4KB 21 | Screen/room pointer table |
| 0x36010 | 0x3900F | 12KB | CHR 4KB 22-24 | NPC dialogue text (token compressed) |
| 0x39010 | 0x3A00F | 4KB | CHR 4KB 25 | Nametable layout commands (PPU addr + tiles) |
| 0x3A010 | 0x3D00F | 12KB | CHR 4KB 26-28 | Level/entity structured data |
| 0x3D010 | 0x4000F | 12KB | CHR 4KB 29-31 | Tilemap data (raw tile indices for maps) |

### Bank 4 Detailed Data-Range Map ($8000-$BFFF)

| Address | Size | Classification | Notes |
|---------|------|----------------|-------|
| $8000-$8031 | 50B | Jump table | 25 entries x 2B dispatch table |
| $8032-$804F | 30B | Pointer table | 7 code ptrs + 21 string ptrs into $BD34+ |
| $8050-$93E2 | ~5KB | Code | Screen load, entity mgmt, tile rendering, collision grid |
| $93E3-$93F2 | 16B | Data: ambient cfg | 4 x 4B records -> ZP $C7-$CA |
| $93F3-$951E | 300B | Data: palette index | 75 palette defs x 4B -> color group indices |
| $951F-$95FA | 220B | Data: palette colors | NES color values ($00-$3F) |
| $95FB-$99FA | 1024B | Data: MiniTile | 256 MiniTiles x 4B = 2x2 CHR tile indices |
| $99FB-$9AFA | 256B | Data: tile attrib | 256 tiles x 1B = collision/attribute flags |
| $9AFB-$9EFA | 1024B | Data: tile table | 256 tiles x 4B = 2x2 MiniTile IDs |
| $9EFB-$9F1A | 32B | Data: entity OAM flags | Per-type OAM attribute flags (values 0/1/3) |
| $9F1B-$9F3A | 32B | Data: entity size flags | Per-type size/priority flags |
| $9F3B-$9F7A | 64B | Ptr table: sprite | 32 types -> CHR tile data at $A630+ |
| $9F7B-$9FBA | 64B | Ptr table: OAM layout | 32 types -> multi-sprite layout at $A98C+ |
| $9FBB-$9FFA | 64B | Ptr table: sequence | 32 types -> animation sequences at $A429+ |
| $9FFB-$A03A | 64B | Ptr table: animation | 32 types -> animation state data |
| $A03B-$A07A | 64B | Ptr table: processing | 32 types -> behavior sub-tables at $A0BB+ |
| $A07B-$A0BA | 64B | Data/padding | Transition zone |
| $A0BB-$A428 | ~878B | Data: proc sub-tables | Nested ptr16 -> behavior routines at $AC00+ |
| $A429-$A62F | ~519B | Data: sequences | Animation frame streams ($FE/$FF/$80 control) |
| $A630-$A98B | ~860B | Data: sprite tiles | CHR tile base + OAM attr per direction |
| $A98C-$ABFF | ~628B | Data: OAM layouts | Multi-sprite piece definitions, $FF-terminated |
| $AC00-$BD33 | ~1332B | Code/Data: behavior | Entity-specific AI routines and parameters |
| $BD34-$BFFF | ~716B | Data: dictionary | 119 bit7-terminated strings (NPC names, game terms) |

### Bank 5 Detailed Data-Range Map ($8000-$BFFF)

| Address | Size | Classification | Notes |
|---------|------|----------------|-------|
| $8000-$8027 | 40B | Jump table | 20 entries x 2B dispatch table |
| $8028-$8089 | ~98B | Code: tick loop | Entity tick all (entry 18) + per-entity tick (entry 1) |
| $808D-$80E4 | ~88B | Code: dispatch | Entity dispatch, extended check, helper routines |
| $80E5-$8164 | 128B | Ptr table: type | 64 entity types -> per-type sub-state tables |
| $8165-$8420 | ~700B | Ptr tables: sub-state | Per-type sub-state function tables (8-16 entries each) |
| $8427-$9B75 | ~6.2KB | Code: behavior | Entity behavior handlers (player, enemies, items, NPCs) |
| $9B76-$9FDF | ~1.1KB | Code: spawn/setup | Player spawn, entity init, screen-specific handlers |
| $9FE0-$A172 | ~403B | Code: sprite/OAM | Player sprite positioning, entity rendering helpers |
| $A173-$ACFF | ~3KB | Code: combat/event | Damage, attack, collision, event triggers, AI routines |
| $AD00-$BFFF | ~4.9KB | Code: screen/HUD | Screen entry, bounds check, HUD writer, patrol/wander AI |

Bank 5 is ~99% code. No large data tables -- entity data lives in bank 4, behavior logic lives here.

---

## Key Findings

### Architecture

#### MMC1 Bank Switching

MMC1 uses serial writes (5 consecutive stores of bit 0) to set registers:

| Register | Address Range | Init Value | Function |
|----------|---------------|------------|----------|
| Control  | $8000-$9FFF | $1F | PRG mode 3 (fix last), CHR 4KB, horiz mirror |
| CHR Bank 0 | $A000-$BFFF | $00 | Selects 4KB CHR at PPU $0000 |
| CHR Bank 1 | $C000-$DFFF | $01 | Selects 4KB CHR at PPU $1000 |
| PRG Bank | $E000-$FFFF | $06 | Selects 16KB PRG at CPU $8000 |

Key routines (all in bank 7, fixed):
- `$EB93` mmc1_write_ctrl: serial write to $9FFF
- `$E56E` mmc1_write_chr0: serial write to $BFFF
- `$E582` mmc1_write_chr1: serial write to $DFFF
- `$E596` mmc1_write_prg: serial write to $FFDF
- `$E871` init_mmc1: resets shift reg ($FF to $9FFF), sets ctrl=$1F, chr0=$00, chr1=$01, prg=$06

#### RESET Flow ($E19B)

1. SEI, CLD, disable PPU ($2000/$2001 = 0)
2. Wait for PPU warmup (3x vblank polls via $2002)
3. TXS (SP = $FF)
4. Disable APU ($4017 = $FF, $4015 = $00)
5. Clear RAM: $0000-$01FF, $0300-$05FF (skips $0200 OAM buffer)
6. Fill $04A0-$04BF with $0F, set $04A1-$04A3 to $20
7. JSR init_mmc1 ($E871)
8. JSR init_sprites ($EA7E) -- fill OAM with Y=$F8 (offscreen)
9. Set ZP vars: $E0=$A5, $1C=$14, $11=$06, $10=$A0
10. Enable PPU ($2000 = $A0 = NMI on, bg pattern $1000, sprite pattern $0000)
11. Fall into game state machine

#### Frame Sync / Wait Routines

The game uses a spin-wait frame sync tied to the NMI (vblank) interrupt:

```
$F24A (nmi_spin_wait):
  1. Clear $1C bit 7 (acknowledge previous NMI)
  2. Spin: LDA $1C; BPL spin  (wait until NMI handler sets bit 7)
  3. ASL A; RTS  (return shifted flags)

$E95B (wait_nmi):
  1. JSR $F24A (spin until vblank)
  2. INC $7F (frame counter)
  3. LSR A; STA $1C (process flags)

$F73D (game_frame_proc):
  1. JSR $F743 (frame_check: verify rendering active + sprites visible)
  2. JMP wait_nmi

$E2B8 (vram_drain_loop):
  Loop: JSR $EEB3 (process VRAM transfer + wait_nmi)
        Until $18 AND $0162 AND $0163 all zero (all pending transfers flushed)
```

The NMI handler ($E3C9) sets $1C bit 7 during vblank, which releases the spin-wait. This ensures all game logic runs between vblanks, synchronized at 60Hz (NTSC).

**Dispatch sled corrections:** $E06B and $E0EC were previously labeled as frame sync routines. They are actually bank dispatch sled entries:
- $E06B: bank 3 dispatch (entry 1, $3A=1) -> $C6FD party/entity stat processing
- $E0EC: bank 6 dispatch (entry 22, $3A=22) -> game state exit handler (called when $80==0)

#### OAM Buffer ($0200-$02FF)

Standard NES OAM shadow buffer: 64 sprites x 4 bytes, transferred to PPU via DMA ($4014) during NMI.

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| +0 | 1B | Y position | $F8 = offscreen (hidden) |
| +1 | 1B | Tile index | CHR pattern table index |
| +2 | 1B | Attributes | Bits 1:0=palette, 5=priority, 6=H-flip, 7=V-flip |
| +3 | 1B | X position | Screen X coordinate |

**Layout:**

| Sprite | Address | Purpose |
|--------|---------|---------|
| 0 | $0200-$0203 | Sprite-0 hit detect (Y=$BF, tile=$2E, attr=$22, X=$DF) |
| 1-4 | $0204-$0213 | Reserved: player sprite pieces (bank 5 $9FE0 writes here) |
| 5-63 | $0214-$02FF | Dynamic: entities, HUD icons, effects |

**Allocation:**
- ZP $16: Current OAM write pointer (next available byte offset)
- ZP $17: OAM write limit
- init_sprites ($EA7E) fills all with $F8, sets sprite 0, starts $16/$17 at $14
- Entity rendering adds `$84` to X offset and wraps, skipping reserved sprites 0-4 (check `CMP #$14`)

**Sprite rendering ($C3A8):** Reads sprite data from pointer ($D5), count in $D2, adds Y-offset $D3 and X-offset $D4 to each 4-byte sprite entry. Directly writes NES OAM format to $0200+X.

#### NMI Handler ($E3C9 - $E56D)

Full traced flow:

1. **Save state** ($E3C9): PHA, read $2002 (clear vblank), set NMI flag (bit 7 of $1C)
2. **OAM DMA** ($E3D7): If bit 0 of $1C clear, transfer $0200-$02FF to PPU via $4014
3. **Save X,Y** ($E3ED): TXA/PHA, TYA/PHA
4. **Palette update** ($E3F5): If bit 2 of $1C set, copy 32 bytes from $04A0 to PPU $3F00
5. **PPU column read** ($E41A): JSR $EEEE, then if bit 3 of $1C set, read VRAM columns into RAM
   - Source: PPU addr in $EB(lo)/$EC(hi), Count: $EA, Dest: ($E8/$E9)
6. **CHR bank switch** ($E48E): Index $38 into table at $ED43 (pairs of chr0/chr1 values)
7. **PPU address reset** ($E49E): Write $3F00 then $0000 to $2006 (reset scroll latch)
8. **Set rendering** ($E4AE): $2001 = $11 (PPU mask), scroll = $12(X)/$14(Y), nametable from $13/$15 into $2000
9. **Controller read** ($E4D0): Read $4016 with debounce (require 2 identical reads)
   - $C0 = current buttons, $C1 = previous, $C2 = new presses (edges)
10. **Frame counter** ($E523): Increment 16-bit counter at $1E/$1F
11. **Timer system** ($E529): Decrement timers $20-$2F based on frame count (every 8 or 16 frames)
12. **Bank 0 trampoline** ($E548): Switch PRG to bank 0, JSR $8000, restore PRG from $39
13. **Sound** ($E555): If $57 nonzero, JSR $CFE0 (sound/music engine in current bank)
14. **Restore & RTI** ($E55C): Restore Y,X, re-enable NMI ($2000 bit 7), restore A, RTI

#### CHR Bank Selection Table ($ED43)

Indexed by $38 (chr_bank_index), read as pairs (chr0, chr1) for 4KB CHR banking.
NMI reads `$38`, doubles it as table index, and calls mmc1_write_chr0/chr1 with the pair.

Full 32-entry table:

| $38 | CHR0 | CHR1 | Game Context |
|-----|------|------|--------------|
| $00 | $00 | $14 | Default (init), title screen reset, text display reset |
| $01 | $05 | $14 | Dungeon interior (Ch 1-4) |
| $02 | $05 | $06 | Dungeon interior (Ch 5) |
| $03 | $07 | $0E | RPG battle, warp/boss transition |
| $04 | $08 | $09 | -- |
| $05 | $10 | $09 | RPG battle screen (bank 3 $90CF, bank 7 $DE93) |
| $06 | $0D | $06 | HUD/menu overlay, shop screen (bank 1 $A2F4, $B480) |
| $07 | $0A | $14 | Overworld variant (Ch 1, 4) |
| $08 | $02 | $06 | Overworld variant (Ch 2) |
| $09 | $03 | $06 | Overworld variant (Ch 4) |
| $0A | $04 | $06 | Overworld variant (Ch 5) |
| $0B | $01 | $06 | Overworld variant (Ch 1, 3) |
| $0C | $07 | $0E | Dungeon variant (Ch 3-5) |
| $0D | $07 | $0F | Dungeon variant (Ch 3-5) |
| $0E | $0A | $11 | Town/building (Ch 2-4) |
| $0F | $0A | $12 | Overworld primary (most common: 279 screens, all chapters) |
| $10 | $0A | $13 | Overworld variant (Ch 3-5) |
| $11 | $0C | $11 | Town/dungeon (all chapters) |
| $12 | -- | -- | (no WorldScreen usage; see $14+) |
| $13 | $0B | $06 | Town interior (all chapters, 99 screens) |
| $14 | $05 | $12 | Multi-chapter variant (Ch 2-5) |
| $15 | -- | -- | (not used in WorldScreen data) |
| $16 | $05 | $11 | Multi-chapter overworld/town (112 screens) |
| $17 | $05 | $12 | Chapter-specific areas (Ch 1-3, 5) |
| $18 | $05 | $13 | Chapter-specific areas (all chapters) |
| $19 | $07 | $14 | Chapter intro cinematic (bank 1 $B00E) |
| $1A | $0C | $06 | Special overworld (Ch 1, 4) |
| $1B | $0A | $09 | Boss/encounter setup (bank 6 $95E8) |
| $1C | $0C | $13 | Dungeon variant (Ch 4-5) |
| $1D | $05 | $06 | -- |
| $1E | $0B | $14 | Screen transition / warp (bank 1 $AFFF, bank 6 $8D26) |
| $1F | $00 | $06 | Game-over/special screen init (bank 6 $923D) |

**$38 sources** -- how chr_bank_index gets set:

| Source | Code | When |
|--------|------|------|
| DataPointer ($B8) bits 0-5 | Bank 4 $8436: `LDA $B8; AND #$3F; STA $38` | Every screen load (739 WorldScreen records) |
| DataPointer restore | Bank 6 $94F2, $9706: same AND #$3F pattern | Re-entering overworld after sub-mode |
| Direct immediate | Various `LDA #imm; JSR $E8C8` | Mode transitions (see below) |
| RAM variable $0525 | Bank 1 $8198: `LDA $0525; JSR $E8C8` | Screen/UI engine restore |
| RAM variable $04D0 | Bank 2 $AA58: `LDA $04D0; JSR $E8C8` | Music driver CHR restore |

**Direct CHR mode sets by game function:**

| Caller | $38 | CHR0/1 | Function |
|--------|-----|--------|----------|
| Bank 7 $DEA0 | $05 | $10/$09 | RPG battle screen layout |
| Bank 7 $DF01 | $0F | $0A/$12 | Post-battle return to overworld |
| Bank 3 $90CF | $05 | $10/$09 | Battle engine init |
| Bank 1 $A116 | $00 | $00/$14 | Screen engine default reset |
| Bank 1 $A2F4 | $06 | $0D/$06 | Shop/menu HUD |
| Bank 1 $AA13 | $03 | $07/$0E | Dialogue portrait display |
| Bank 1 $AFFF | $1E | $0B/$14 | Transition/warp screen |
| Bank 1 $B00E | $19 | $07/$14 | Chapter intro cinematic |
| Bank 1 $B341 | $00 | $00/$14 | Text display init |
| Bank 1 $B480 | $06 | $0D/$06 | Menu overlay |
| Bank 6 $8D26 | $1E | $0B/$14 | Warp/transition (overworld) |
| Bank 6 $8E05 | $03 | $07/$0E | Entity spawn transition |
| Bank 6 $923D | $1F | $00/$06 | Game-over screen init |
| Bank 6 $95E8 | $1B | $0A/$09 | Boss encounter setup |
| Bank 6 $B37C | $03 | $07/$0E | Warp zone/boss |

#### CHR Bank Pairing by Game Mode

**Overworld action** ($19=0): $38 set from DataPointer per screen. Most common $38=$0F (CHR0=$0A/CHR1=$12). CHR0 bank 10 ($0A) = overworld sprites+bg. CHR1 varies by chapter tileset ($11-$13 = banks 17-19).

**RPG battle** ($19=5): $38=$05 (CHR0=$10/CHR1=$09 = battle sprites and battle background). Set at bank 7 $DEA0 and bank 3 $90CF.

**Post-battle return** ($19=6): $38=$0F restored (CHR0=$0A/CHR1=$12 = back to overworld).

**Town/NPC/shop** ($19=3): DataPointer-driven for town visuals, then $38=$06 (CHR0=$0D/CHR1=$06) for shop/menu HUD overlay.

**Dialogue/text** ($19=7): $38=$03 (CHR0=$07/CHR1=$0E) for portrait dialogue, $38=$00 for simple text reset.

**Screen transitions** ($19=1,2): $38=$1E (CHR0=$0B/CHR1=$14) during warp, DataPointer restored on arrival.

**Chapter intro** ($19=8): $38=$19 (CHR0=$07/CHR1=$14) for cinematic sequences.

**Title screen** ($19=11): $38=$00 (default CHR), then per-phase setup.

**Game over** ($19=10): $38=$1F (CHR0=$00/CHR1=$06) for death screen.

**Boss encounter** (special): $38=$1B (CHR0=$0A/CHR1=$09) for boss setup at bank 6 $95E8.

#### CHR 4KB Bank Content Summary (by bank number)

| 4KB Bank | Content | Used By |
|----------|---------|---------|
| $00 | Font + basic tiles | Title, text, game-over |
| $01 | Dungeon tileset A | Ch 1,3 dungeons ($0B) |
| $02 | Dungeon tileset B | Ch 2 overworld variant ($08) |
| $03 | Area tileset C | Ch 4 overworld variant ($09) |
| $04 | Area tileset D | Ch 5 overworld variant ($0A) |
| $05 | Dungeon/interior sprites | Multiple dungeon modes ($01,$02,$14,$16-$18) |
| $06 | Common background tiles | Shared CHR1 for 12+ modes |
| $07 | Battle/cinematic sprites | Battle ($03,$0C,$0D), cinematic ($19) |
| $08 | Player/NPC sprites A | Mode $04 |
| $09 | Battle background | RPG battle CHR1 ($04,$05,$1B) |
| $0A | Overworld sprites | Primary overworld CHR0 ($0E-$10,$1B) |
| $0B | Transition sprites | Warp/transition ($1E), town interior ($13) |
| $0C | Town sprites variant | Town/dungeon CHR0 ($11,$1A,$1C) |
| $0D | Menu/HUD tiles | Shop/menu overlay ($06) |
| $0E | Battle background B | Battle CHR1 ($03,$0C) |
| $0F | Battle background C | Dungeon variant CHR1 ($0D) |
| $10 | Battle sprites | RPG battle CHR0 ($05) |
| $11 | Chapter tileset 1 | Towns ($0E,$11), multi-chapter ($16) |
| $12 | Chapter tileset 2 | Primary overworld ($0F), multi ($14,$17) |
| $13 | Chapter tileset 3 | Overworld ($10,$18,$1C) |
| $14 | Default CHR1 (init) | Default mode ($00), dungeons ($01,$07), cinematic ($19) |

#### Main Game Loop ($E290)

The game uses a state machine driven by zero-page variable $80:
- $E290: JSR $F73D (frame sync + validation check)
- Check $18 (mode flag), conditionally call $E110 (adds 5 to dispatch index $3A)
- JSR $E11A (bank-switch dispatch - switches to bank 6, looks up $8000+$3A*2 for target)
- If $19 negative: exit loop
- If $80 != 0: loop back to $E290
- If $80 == 0: clear $60, call $E0EC, then check $19 for level transition
- JMP $E20B to restart level/mode setup

#### Bank-Switch Dispatch System ($E11A / $E16A)

The game uses a **coroutine dispatch** pattern:
1. $3A = routine index (modified by game logic, $E110 adds 5)
2. $E11A saves current PRG bank, switches to bank 6
3. $E16A reads a 16-bit address from bank 6's jump table at $8000 + ($3A * 2)
4. JMP ($3E) executes the target routine (in bank 6 address space)
5. On return, restores the previous PRG bank

Bank 6 jump table at $8000 (32 entries, 3 null):

| Idx | Address | Notes |
|-----|---------|-------|
| 0 | $8041 | Two-level dispatch via $19 (game mode sub-states) |
| 1 | $0000 | null |
| 2 | $8A78 | Game logic - checks $C4 table, processes entities |
| 3 | $8AE4 | |
| 4 | $8AF4 | |
| 5 | $8BB5 | Wait loop - polls $031C flags, calls $F0B2 |
| 6 | $8C76 | |
| 7 | $978B | |
| 8 | $97A4 | |
| 9 | $910B | |
| 10 | $9140 | |
| 11 | $94E5 | |
| 12 | $9085 | |
| 13 | $8EFF | |
| 14 | $917D | |
| 15 | $9233 | |
| 16 | $984C | |
| 17 | $A1C4 | |
| 18 | $A1F0 | |
| 19 | $A239 | |
| 20 | $A27B | |
| 21 | $AE75 | |
| 22 | $A896 | |
| 23 | $ADF6 | |
| 24 | $9591 | |
| 28 | $977E | |
| 29 | $AE1A | |
| 30 | $AE47 | |
| 31 | $BC7F | |

Entry 0 ($8041) is itself a sub-dispatch via $E97D, reading an address table indexed by $19.

#### Bank Dispatch Trampolines ($E000-$E0D5)

In addition to the bank 6-specific dispatch at $E11A, the engine has a **general trampoline** at $E11E that accepts any bank number in A. Banks 0-5 each have an INC $3A chain in the $E000-$E0D5 region. Callers enter at a specific address in the chain to set the routine index ($3A) via increments, then dispatch to the target bank.

| Bank | Trampoline Range | Max $3A | Jump Table Size | Key Entry Points |
|------|-----------------|---------|----------------|-----------------|
| 0 | $E000-$E010 | 5 | 6 entries | $E000 (+5), $E00A (+0) |
| 1 | $E011-$E045 | 23 | 24 entries | $E03F (+0), $E02F (+8), $E011 (+23) |
| 2 | $E046-$E05E | 9 | 10 entries | $E058 (+0), $E054 (+2), $E046 (+9) |
| 3 | $E05F-$E073 | 7 | 8 entries | $E06D (+0), $E06B/wait_frame (+1), $E069 (+2) |
| 4 | $E074-$E0AA | 24 | 25 entries | $E0A4 (+0), $E074 (+24) |
| 5 | $E0AB-$E0D5 | 21 | 22 entries | $E0D5/text_complete (+0), $E0CD/text_advance (+4), $E0AB (+21) |

The $E17B (inline_dispatch) variant reads $3A and bank number from inline data bytes after the JSR, used for direct cross-bank calls without going through the INC chain.

#### PRG Bank Roles

| Bank | Role | Evidence |
|------|------|----------|
| 0 | Sound engine + display | NMI sound engine ($809E-$889B), SFX data/sequences ($889C-$AFFF), display rendering code ($B000-$BF8D) |
| 1 | Screen/UI engine + dialogue | 24-entry jump table at $8000; dispatched via $E03F-$E011 trampoline. Code for title screen, chapter intros, menu layouts, HUD rendering, NPC dialogue display. Contains word dictionary at $B8B1 and formatted dialogue text at $BB-$BF |
| 2 | Music data/driver | 33 songs + 18 SFX sequences. Music sequencer ($BE81) drives 4 APU channels. Called from bank 0 $80D8 via $E9DD trampoline |
| 3 | RPG battle engine | 5-entry jtable at $8000, dispatched via $E06D-$E05F sled. $8000-$8FFF=data (encounters/palettes/sprites), $90AD-$BFEF=code (~12KB battle engine). See Bank 3 detail section |
| 4 | Data tables | $E776: LDA #$04, JSR mmc1_write_prg, then pointer reads via ($D1),Y |
| 5 | Entity behavior engine | 20-entry jtable at $8000; dispatched via $E0D5 trampoline. Two-level entity AI dispatch: type table ($80E5, 64 entries) -> per-type sub-state tables -> behavior functions. Manages player (type 5), NPCs, enemies, projectiles. See Bank 5 detail section |
| 6 | Game logic | Jump table at $8000, dispatched via $3A from bank6_dispatch |
| 7 | Core engine (fixed) | NMI, bank switching, dispatch, I/O, frame sync |

Dynamic bank access: $EFA3 uses `$EA & 7` as bank number for VRAM data reads (level/tilemap data).

#### Sound System Architecture (Banks 0 + 2)

The sound system spans two PRG banks with a clear division of labor:

**Bank 0 -- SFX Engine (called every NMI via $E548 trampoline)**

1. `$809E` (sound_main): Saves ZP $D9-$DF, processes queued sound requests from `$03E5`/`$03E7` buffer, enables APU ($4015=$0F), calls `$85A7` (audio_process), then calls bank 2 music driver via `LDA #$02; JSR $E9DD`.
2. `$883F` (play_sound): Dispatches SFX by ID. `$FF` = silence all channels + reset state. IDs < $90 look up `$800E+ID` for channel assignment (bits 7:6 = channel 0-3, bits 5:0 = priority). Higher priority overrides current SFX on that channel.
3. `$85A7` (audio_process): Reads `$FB` (SFX channel request), looks up pointer pair from `$8D17+ID*4`, sets up channel data at `$0340`/`$0349` for Pulse1/Triangle SFX overlay.
4. `$80F9`: Post-music processing for `$F8` (SFX request). Special values: `$3F` = tempo change, `$3E` = pitch bend. Normal values index into `$8B90` SFX data table.

**Bank 2 -- Music Sequencer ($B000, called from bank 0 $80D8)**

Entry point `$B000`: JSR `$BE81` (tone channel sequencer) then JSR `$B73E` (noise channel handler).

`$BE81` (music_seq_tick): Processes 4 tone channels (Pulse1, Pulse2, Triangle, DMC) in a loop:
- Channel state at `$0380+X*4`: [ptr_lo, ptr_hi, duration, last_period_hi]
- X iterates 0, 4, 8, 12 (CPX #$10 loop)
- `$D4` = channel bitmask (ASL each iteration: $01, $02, $04, $08)
- If duration ($0382,X) nonzero and bit 7 clear: decrement and skip (note sustain)
- If duration expired: read next sequence bytes from ($D0),Y
  - Byte 0 = APU volume/duty register ($4000+X)
  - Byte 1 = duration counter -> $0382,X
  - If duration bit 7 set: JSR `$BF3B` (sweep + period lookup) -- note with sweep
  - If duration bit 7 clear: JSR `$BF64` (direct period write) -- note without sweep
- Special bytes: $00 = channel end (silence + clear), $01 = loop/repeat command
- Sequence pointer advances by 4 bytes per note event

`$B73E` (noise_seq_tick): Dedicated noise channel ($400C-$400F) handler:
- `$FA` = noise SFX request ID, `$FE` = current noise track ID
- Pointer pair from `$B157+ID*2` -> noise sequence data at `$0158`/`$0159`
- Noise note format: byte 0 = volume (low nibble -> $400C with $F0 mask), byte 1 = duration -> `$015A`
- Period: byte 0 >> 4 combined with `$D5` (from byte 1 bit 7) -> `$400E`
- `$400F` always written as `$88` (length counter load)
- Special bytes: $00 = stop noise, $01 = loop marker (read next 2 bytes as new pointer)

**Note Period Tables:**

`$B189` (40 entries, 16-bit LE): Pulse/Triangle periods covering ~3.3 octaves (A1=$07F0 to ~C#5=$00D4). Standard NES APU period values: freq = 1789773 / (16 * (period + 1)).

`$B1D8` (40 entries, 16-bit LE): Triangle-specific period table (used when X=$0C). Triangle periods are different due to the triangle channel running at 1 octave lower for the same period value.

**Song Data Organization:**

Song pointer table at `$B005` (34 entries, 16-bit LE). Entry 0 = $60B7 (invalid/no-song sentinel). Entries 1-33 point to 8-byte song headers at $B051-$B151.

Each song header = 4 x 16-bit pointers (one per channel):
- Channel 0: Pulse 1 (used by 1 song only -- #23; otherwise reserved for bank 0 SFX)
- Channel 1: Pulse 2 (primary melody, used by 29 of 33 songs)
- Channel 2: Triangle (bass line, used by 2 songs: #23, #32)
- Channel 3: Noise (percussion, used by 7 songs: #4, #8, #10, #13, #25, #29, #31, #33)

Song #11 and #12 are empty (all channels $0000) -- likely placeholder/silent entries.
Song #23 is the most complex: Pulse1 + Pulse2 + Triangle (3 channels).
Song #32 shares the same data pointer ($B4E8) for Pulse2 and Triangle.

SFX pointer table at `$B157` (18 entries, 16-bit LE): Noise/percussion sequence pointers for the $B73E handler. These handle rhythm/percussion effects independently from the song system.

**Request Interface (ZP $F8-$FB):**

| Addr | Name | Written By | Read By | Purpose |
|------|------|-----------|---------|---------|
| $F8 | sfx_request | Game code via $03E5/$03E7 queue | Bank 0 $80F9 | SFX ID for bank 0 channel overlay |
| $F9 | song_request | Game code (indirect) | Bank 2 $BE81 | Song ID (1-33) to start playing |
| $FA | noise_request | Game code (indirect) | Bank 2 $B73E | Noise SFX ID (1-18) |
| $FB | sfx_channel_req | Game code (indirect) | Bank 0 $85A7 | SFX channel setup request |

All four are cleared to 0 by bank 0 `$80E2` after each frame's processing.

#### Secret Name Codes (Bank 6 $B78C)

The character name entry system (bank 6) checks the entered name against a table of secret codes at `$B7CC` before falling through to the normal password/continuation code verifier at `$B7E6`.

**Name entry grid** uses CHR page 7 tile mapping at `$B9A6`: A-Z = tiles `$30`-`$49`, digits 1-9 = tiles `$01`-`$09`, 0 = tile `$00`, plus period and special symbols.

**Comparison routine at `$B78C`**: Iterates through the length-prefixed entries in the table at `$B7CC`. For each entry, compares the entry bytes against the name buffer at `$0400`,Y. If all bytes match AND the matched length equals the total name length (`$05`), it dispatches based on the entry number (`$3B`, 1-based):

| Entry | Name | Length | Tile Bytes | Handler | Effect |
|-------|------|--------|------------|---------|--------|
| 1 | `1W` | 2 | `$01 $46` | `$BAD1` | Start at Chapter 1 with preset stats |
| 2 | `2W` | 2 | `$02 $46` | `$BAD1` | Start at Chapter 2 with preset stats |
| 3 | `3W` | 2 | `$03 $46` | `$BAD1` | Start at Chapter 3 with preset stats |
| 4 | `4W` | 2 | `$04 $46` | `$BAD1` | Start at Chapter 4 with preset stats |
| 5 | `5W` | 2 | `$05 $46` | `$BAD1` | Start at Chapter 5 with preset stats |
| 6 | `END` | 3 | `$34 $3D $33` | `$BA25` | Play ending/credits sequence |
| 7 | `SOUND` | 5 | `$42 $3E $44 $3D $33` | `$BA3C` | Enter sound test mode |

**Chapter warp handler (`$BAD1`)**: Reads chapter index from `$3B` (1-5 for 1W-5W, mapped to chapters 0-4). Iterates through 50 seven-byte records at `$BB1F`-`$BC7C`, terminated by `$FF` sentinel at `$BC7D`. Each record: bytes 0-1 = target address (little-endian), bytes 2-6 = per-chapter values (chapters 0-4). The handler writes the chapter-specific byte to the target address, initializing the full game state for that chapter.

Key warp data addresses:
| Target | Ch0 | Ch1 | Ch2 | Ch3 | Ch4 | Purpose |
|--------|-----|-----|-----|-----|-----|---------|
| $0084 | $04 | $09 | $0E | $13 | $18 | Screen/world position |
| $0087 | $3F | $17 | $37 | $37 | $07 | World/overworld flags |
| $0089 | $01 | $02 | $03 | $04 | $05 | Chapter number |
| $0300 | $03 | $04 | $05 | $06 | $07 | Game progress level |
| $0301 | $03 | $04 | $05 | $06 | $07 | Party progress |
| $0302 | $00 | $00 | $01 | $01 | $02 | Armor level |
| $03D6 | $01 | $02 | $03 | $04 | $05 | Chapter-keyed stat |
| ...+44 more | -- | -- | -- | -- | -- | Inventory, spells, party, flags |

After all records: loads chapter data from `$F71A` pointer table via `$EC46`. Sets `$0C`=`$80` to signal warp.

**Ending/Credits State Machine (`$BC7F` -> `$BCA6`):**

Entry at `$BC7F`: clears all entity slots, sets `$1A`=1 (starting state), enters main loop: wait_nmi -> dispatch state via indexed_jmp at `$BCA6` -> loop.

| State | Handler | Sound | Description |
|-------|---------|-------|-------------|
| 1 | $BCC1 | $63 (credits music) | Screen setup type 0 via $BFE5 |
| 2 | $BCD0 | -- | Render display page ($82=6) via $BFDA |
| 3 | $BCDB | $49 (ending jingle) | Scene transition ($BDE6), character animation ($BDF8), scroll ($BE19), CHR setup ($E89D) |
| 4 | $BCFF | $64 (credits pt2 music) | Scene transition, character sprite render ($BD8E), animation ($BDD5), 30-frame delay |
| 5 | $BD30 | $68 (story event music) | Scroll wait, 60-frame delay with NMI sync |
| 6 | $BD4A | -- | Screen setup type 1 via $BFE5 |
| 7 | $BD54 | -- | Scene transition, character render, scroll wait, 60-frame delay |
| 8 | $BD79 | -- | Screen setup type 2 via $BFE5 |
| 9 | $BD83 | -- | Render display page ($82=8) via $BFDA |
| 10 | $BE3E | -- | Final setup via $F7B1(2), 180-frame delay (3 seconds) |
| 11 | $BE53 | -- | **Credits scroll loop**: scroll $14 at 1px/4 frames, load text lines from ($0E) via $BF30/$BF51, $FF-terminated. Freezes when done |

Helper functions: `$BDE6(A)` = screen transition effect (A=type), `$BFE5(A)` = full screen setup, `$BFDA` = render current page, `$BD8E` = character sprite composition, `$BDD5` = character walk animation, `$BE19` = scroll wait loop, `$BF30` = load credits text line, `$BF51` = process credit entry.

**Sound test handler (`$BA3C`)**: Enters an infinite loop that cycles through 32 sound IDs in a table at `$BAAE`. No exit mechanism -- console must be reset.

Sound test controls:
- Up (new press `$C2` AND `$08`): Play currently selected sound via `queue_sound`
- B or Start (held `$C0` AND `$50`, rate-limited to every 8 frames): Next sound
- A or Select (held `$C0` AND `$A0`): Previous sound
- Wraps from entry 31 back to 0; clamps at 0 going backwards
- Displays current index as 2-digit decimal at PPU `$02CA`

Sound test table at `$BAAE` (32 entries): `$05 $5F $60 $53 $50 $48 $49 $5C $3D $4E $2A $62 $79 $65 $5A $7A $0D $5B $7C $3E $5D $55 $54 $4B $25 $5E $52 $57 $59 $64 $68 $63`

#### Continuation Code Passwords (Bank 2 $AC08)

Separate from the character name entry, the continuation code / password entry screen (bank 2 bytecode interpreter) checks entered 7-character passwords against a secret table at `$AC27`:

| Entry | Password | Tile Bytes | Condition |
|-------|----------|------------|-----------|
| 0 | `CHOCOLA` | `$32 $37 $3E $32 $3E $3B $30` | When `$04D0` = 0 |
| 1 | `CORONYA` | `$32 $3E $41 $3E $3D $48 $30` | When `$04D0` = 1 |

These passwords bypass the normal checksum-based continuation code validation. When matched, the bytecode interpreter continues with the current script pointer (`$CE`/`$CF`), which produces different behavior than the failed-validation path.

The password entry screen uses zero page `$00`-`$06` as its input buffer. Characters cycle through Latin letters A-Z (tiles `$30`-`$49`) on the grid.

**Sound request queue** ($03E5/$03E7): Game code writes sound IDs to `$03E7+N` and increments `$03E5` (count). Bank 0 `$809E` drains this queue each frame, calling `$883F` (play_sound) for each entry.

**queue_sound ($E992)**: The main API for triggering sounds from game code. A=sound ID. Called from 199 sites across all banks. Special values: $FF = silence all channels + reset, $00 = no-op. Normal values (1-$8F) are enqueued to $03E7 (max 6 pending). The enqueued IDs are processed by `play_sound` ($883F) in bank 0, which routes them to the appropriate APU channel based on a priority table at `$800E`.

**play_sound ($883F)** routing: Each sound ID indexes into `$800E+ID` for a channel/priority byte:
- Bits 7:6 = channel (0=SFX jingle via $F8, 1=Song via $F9, 2=Noise via $FA, 3=Overlay via $FB)
- Bits 5:0 = priority value written to $F8+channel (higher overrides current)
- $00 = silent/no-op (23 IDs are silent including $00, $77-$78)
- IDs >= $90 are out of range and ignored
- SFX data pointers at `$8B90+ID*2` point to 8-byte SFX records (57 entries: IDs 0-56). Records at $8C02-$8D16 for IDs 1-35; variable-length sequences at $897A-$8B8F for IDs 36-56

**Sound ID Map (186 static + 13 dynamic call sites, 85 unique IDs):**

Priority table routing: 41 IDs -> SFX jingle (channel 0, $F8), 40 -> Song (channel 1, $F9), 33 -> Noise (channel 2, $FA), 14 -> Overlay (channel 3, $FB), 23 silent.

*Songs (channel 1 -> $F9 song request, bank 2 sequencer):*

| ID | Pri | Sites | Context |
|----|-----|-------|---------|
| $01 | 32 | B6(3) | Overworld/adventure music (game start, area entry) |
| $02 | 17 | B5(1) | Entity/knockback music cue |
| $03 | 28 | B6+B7 | UI transition music |
| $0B | 20 | B6(1) | RPG party command |
| $0C | 18 | B6(1) | RPG battle phase |
| $0F | 18 | B5+B7 | Entity hurt music cue |
| $10 | 4 | B4+B5 | Screen/tile change cue |
| $11 | 9 | B5(1) | Entity AI trigger |
| $13 | 25 | B5+B7 | Screen scroll transition |
| $19 | 14 | B5(2) | Chapter event cue |
| $1A | 16 | B5+B6+B7 | Area entry / warp |
| $1B | 16 | B5+B7 | Ambient / area change |
| $1C | 18 | B5(1) | Hit/attack connect |
| $1F | 15 | B5(1) | Ambient SFX |
| $20 | 15 | B5(1) | Ambient SFX |
| $21 | 2 | B5(1) | Entity despawn |
| $26 | 8 | B3+B5 | Warp/spell cast |
| $27 | 8 | B5(1) | Item get |
| $28 | 2 | B5(1) | Equip/use |
| $2B | 3 | B5(2) | NPC interaction |
| $31 | 20 | B6(1) | Area/zone music |
| $3A | 18 | B5(3) | Player attack swing |
| $3B | 26 | B6(1) | Treasure open |
| $42 | 5 | B1(1) | Title screen phase |
| $43 | 6 | B1(1) | Title screen phase |
| $44 | 7 | B1(1) | Title screen phase |
| $45 | 8 | B1(1) | Chapter intro |
| $46 | 9 | B1(1) | Chapter screen |
| $47 | 10 | -- | (unused in code) |
| $4C | 30 | B7(1) | Game over |
| $67 | 28 | B5(1) | Object interact |
| $7D | 12 | B1+B2+B7 | Text/dialogue scroll |
| $7F | 14 | B3+B5+B6 | Boss battle / special event |
| $81 | 1 | -- | (minimal priority, likely unused) |
| $83 | 11 | B6(1) | HP restore |
| $8F | 33 | -- | (highest song priority, unused in code) |

*SFX Jingles (channel 0 -> $F8 process_sfx_request, bank 0 4-channel engine):*

| ID | Pri | Sites | Context |
|----|-----|-------|---------|
| $05 | 7 | B6(5) | Overworld area music (long jingle) |
| $0D | 27 | B6(1) | Scene/cutscene fanfare |
| $0E | 27 | B6(1) | Battle result fanfare |
| $3C | 24 | B6(1) | Key item get jingle |
| $3D | 23 | B1(2) | Shop/menu jingle |
| $3E | 16 | B1(1) | Continue/password jingle |
| $49 | 22 | B6(2) | Ending/credits jingle |
| $4F | 34 | B1(2) | Chapter title fanfare |
| $5F | 32 | B6(2) | Dungeon/cave music |
| $60 | 18 | B6(1) | Town music |
| $62 | 8 | B3(1) | **RPG battle music** (started at battle init after $FF silence) |
| $63 | 9 | B6(1) | Credits/ending music |
| $64 | 15 | B6(1) | Credits phase 2 music |
| $65 | 35 | B6(1) | Victory/clear fanfare (highest SFX priority) |
| $66 | 9 | B1+B6 | Game clear music |
| $68 | 13 | B1+B6 | Story event music |
| $79 | 25 | B3(1) | RPG victory fanfare |
| $7A | 26 | B2(1) | Music system internal |
| $7B | 9 | B6(1) | Dungeon event music |
| $7C | 24 | -- | (unused in code) |

*Noise SFX (channel 2 -> $FA noise request, bank 2 noise handler):*

| ID | Pri | Sites | Context |
|----|-----|-------|---------|
| $04 | 7 | B5+B7 | Chapter/warp noise |
| $07 | 3 | B5(2) | Entity collision noise |
| $0A | 8 | B5+B6 | Entity/battle hit noise |
| $15 | 24 | B7(1) | RPG battle start drum |
| $17 | 18 | B7(1) | RPG victory drum |
| $18 | 12 | B1+B5 | Screen scroll noise |
| $1E | 17 | B6(2) | Menu/dialogue noise |
| $23 | 14 | B5(1) | Boss attack noise |
| $30 | 17 | B5(1) | Entity event noise |
| $32 | 6 | B6(1) | Battle result noise |
| $33 | 7 | B3(2) | RPG spell cast noise |
| $34 | 10 | B3+B6 | RPG battle fanfare drum |
| $39 | 29 | B1+B6 | Dialogue/UI noise |
| $61 | 10 | B4+B5 | Screen load noise |
| $6E | 8 | B3+B7 | RPG battle noise (boss?) |
| $71 | 6 | B3(2) | RPG magic cast noise |
| $75 | 1 | B6(1) | Area transition noise |
| $7E | 15 | B5(1) | Entity spawn noise |
| $80 | 21 | B2(1) | Music init noise |
| $84 | 24 | B1(1) | Magic cast noise (high pri) |

*Overlay SFX (channel 3 -> $FB audio_process, bank 0 2-channel overlay):*

| ID | Pri | Sites | Context |
|----|-----|-------|---------|
| $1D | 3 | B5(1) | Death/kill overlay |
| $25 | 30 | B6(1) | UI confirm overlay |
| $2D | 19 | B5(1) | Boss phase transition overlay |
| $2F | 5 | B5(2) | Entity projectile overlay |

*Silent/No-op IDs (priority 0, 23 IDs):* $00, $06, $14, $16, $22, $29, $2E, $35, $3F, $6C, $73, $77-$78, $82, $85, $87-$8E. Note: $77 is called 30 times from bank 3 (RPG battle engine) as a no-op sync marker -- the actual battle music is $62.

*Sound test table at $BAAE* (32 entries): Maps sound test index to IDs: $05, $5F, $60, $53, $50, $48, $49, $5C, $3D, $4E, $2A, $62, $79, $65, $5A, $7A, $0D, $5B, $7C, $3E, $5D, $55, $54, $4B, $25, $5E, $52, $57, $59, $64, $68, $63. Covers all major jingles/music tracks from the SFX engine.

**NMI audio call chain:**
1. NMI -> $E548: switch to bank 0, JSR $8000 (-> JMP $809E sound_main)
2. $809E: drain $03E7 queue via play_sound, enable APU, ASL $F6, call $85A7 (audio_process)
3. $80D8: LDA #$02, JSR $E9DD -> switch to bank 2, JSR $B000 (music sequencer)
4. $80F9: process $F8 SFX request (bank 0 SFX overlay)
5. $80E2: clear $F8-$FB requests
6. Restore ZP $D9-$DF, return

#### Bank 0 -- Sound Engine + Display Rendering

Bank 0 serves dual purposes: the lower half ($8000-$AFFF) is the SFX engine and its data, called every NMI via the $E548 trampoline. The upper portion ($B000-$BF8D) is a display/rendering module called via the $E9DD bank trampoline (with A=0) for screen building operations.

**Data-Range Map:**

| Range | Size | Description |
|-------|------|-------------|
| $8000-$8002 | 3B | Entry: JMP $809E |
| $8003-$800D | 11B | Sound engine configuration data |
| $800E-$809D | 144B | Sound priority/channel table (indexed by sound ID 0-$8F) |
| $809E-$80F8 | 91B | `sound_main` -- NMI entry, drains queue, calls subsystems |
| $80F9-$81FD | 261B | `process_sfx_request` -- 4-channel SFX jingle player |
| $81FE-$83C3 | 454B | Music channel tick -- processes 4 channels (stride $16 state blocks at $0100-$0157) |
| $83C4-$85A6 | 483B | Sequence command parser + note/envelope/APU register writers |
| $85A7-$8641 | 155B | `audio_process` -- SFX overlay on Pulse1 ($0340) and Noise ($0349) |
| $8642-$883E | 509B | SFX channel tick + command dispatch (4 types via $86DF table) |
| $883F-$889B | 93B | `play_sound` -- route sound ID to channel by priority |
| $889C-$891B | 128B | Note frequency table (64 entries, 16-bit NES APU periods) |
| $891C-$8959 | 62B | Noise period lookup table |
| $895A-$8979 | 32B | Noise envelope/volume table |
| $897A-$8B8F | 534B | Variable-length SFX sequences (complex multi-step effects) |
| $8B90-$8C01 | 114B | SFX pointer table (57 entries: ID -> 8-byte channel record) |
| $8C02-$8D16 | 277B | SFX channel records (35 x 8B: 4 channel ptrs per SFX) |
| $8D17-$8E08 | 242B | SFX overlay channel data + short sequence fragments |
| $8E09-$AFFF | 8695B | SFX sequence data (multi-channel jingles + long effects) |
| $B000-$BBA1 | 2978B | Display rendering engine (screen/nametable building code) |
| $B3A0-$BBA1 | ~2KB | Screen text-layout streams (32 status/results templates, $2F-terminated) |
| $BBA1-$BBE1 | 64B | Screen data index table (32 x 2B: page/flags + lo offset) |
| $BBE2-$BF8D | 940B | Display subroutines + helper data |
| $BF8E-$BFFF | 114B | $FF padding (unused) |

**SFX Engine Architecture:**

The SFX engine (process_sfx_request at $80F9) manages 4 independent APU channels for sound effects that temporarily override the music:

- 4 channel state blocks at $0100-$0157, stride $16 (22 bytes each):
  - $0100+N: sequence data pointer (lo/hi)
  - $0102+N: transpose offset
  - $0104+N: volume decay counter
  - $0106+N: duration counter
  - $0108+N: envelope index
  - $010E+N: flags (bit 7 = reload period)
  - $0114+N: channel state flags
  - $0115+N: base note value

- Channels map to APU registers via `$DA * 4` -> $4000/$4004/$4008/$400C
- Channel 0-1 ($0100-$012B): Pulse 1+2, bit 7 set in $010E (reload on first note)
- Channel 2-3 ($012C-$0157): Triangle+Noise, $010E cleared

- Sequence format: 4-byte commands parsed at $82CF, dispatched by bits 6-7 of byte 0:
  - Type 0 ($82F7): Set note + duration + decay envelope
  - Type 1 ($830D): Set note + duration + volume with optional portamento
  - Type 2 ($8344): Control command (transpose, envelope select, loop, etc.)
  - Type 3 ($835E): Extended control (tempo, SFX trigger, channel link)
  - Sub-commands under Type 2/3 handle: subroutine call/return ($84E4/$84FE), loop with counter ($850B), rest with mute ($8538), transpose ($8552), sustain toggle ($855E), volume override ($8569), trigger nested sound ($8571/$8579)

- SFX ID $FF: silence all -- disable/re-enable APU, clear all channel state
- SFX ID $3F: tempo change -- modifies $F4 timing accumulator
- SFX ID $3E: pitch bend -- sets global pitch offset

**SFX Data Tables:**

The pointer table at $8B90 has 57 entries (IDs 0-56). Entry 0 points to RAM ($06B1, null/inactive). The remaining entries split into two groups:

- IDs 1-35: Fixed 8-byte records at $8C02-$8D16 (stride 8). Each record has 4 channel pointers to sequence data in the $8E09-$AFFF range. Pointer $8D1A = null/silence (channel unused). These are the multi-channel jingles (item get, level up, game over, etc).

- IDs 36-56: Variable-length SFX sequences at $897A-$8B8F. These are simpler single-channel effects (menu blips, hits, explosions).

**Note Frequency Table ($889C):**

64 entries covering ~5.3 octaves. Values are NES APU timer periods: freq = 1789773 / (16 * (period + 1)).

| Index | Period | ~Note |
|-------|--------|-------|
| 0 | $07F0 | A1 (55 Hz) |
| 12 | $03F8 | A2 (110 Hz) |
| 24 | $01FC | A3 (220 Hz) |
| 36 | $00FD | A4 (440 Hz) |
| 48 | $007E | A5 (880 Hz) |
| 63 | $0034 | ~D#7 |

**SFX Overlay ($85A7):**

Separate from the main 4-channel SFX, the audio_process handles two overlay channels for short sound effects that layer on top of music:

- Pulse 1 overlay: state at $0340-$0348
- Noise overlay: state at $0349-$0351
- Channel data from table at $8D17 (indexed by $FB * 4, each entry = 2 pointer pairs)
- $0395 bitmask tracks active overlay channels (bit 0 = Pulse, bit 3 = Noise)

**Display Rendering Module ($B000-$BF8D):**

The $B000 entry point is reached via bank_trampoline ($E9DD) with A=0 (switching PRG to bank 0). This is a self-contained display system that builds nametable screen data:

- Entry at $B000: saves A, calls wait_nmi, processes display parameter
- Reads screen layout index from table at $BBA2 (packed: bits 2-0 = page hi offset, bits 5-3 = flags, low byte + $A0 = data address). Data stored at $B3A0-$BAFF.
- Uses nametable tile buffer ($0500+) and PPU addressing through fixed-bank helpers ($DDEA, $DE5B, $DF79)
- Multi-frame operation with wait_nmi synchronization
- Internal jump table at $BD0D dispatches via indexed_jmp ($E97D) to 6 sub-handlers at $BF09-$BE45

##### Screen Data: index table $BBA1 + layout streams $B3A0-$BAFF

The $B3A0-$BAFF region is a packed blob of 32 **text-layout command streams** (status/results/info screens), addressed via the 2-byte index table at $BBA1.

**Index entry** (entry `i` at `$BBA1 + 2i`, indexed by screen_param*2 in $0422):
- byte0 (`$BBA1,X`): bits 0-2 = page offset (+$B3), bits 3-4 = vertical-offset selector into $B1F1 (4 entries: $00,$09,$0B,...), bits 5-7 = flags (bit7/6/5 control border/centering paths)
- byte1 (`$BBA2,X`): low offset (+$A0)
- Stream address = `(($B3 + (byte0 & 7) + carry) << 8) | (($A0 + byte1) & $FF)`

**Stream command format** (interpreter at $B0D9):
| Byte | Meaning |
|------|---------|
| $2F | End of stream |
| $2E | Row advance (INC $0423, next nametable row) |
| $2C | Space (stored to buffer $0168) |
| $2D | Emit `$4F` ('-') + terminate row |
| $30-$49 | Letters A-Z (stored directly) |
| $00-$09 | Digits 0-9 |
| $0A-$2B | PPU-write/positioning commands (`ADC #$E0` -> $B331 tile writer) |
| $80-$8F | **Dynamic value insert** via $B241 (A&$0F -> inline jump table at $B24C, 16 sub-handlers). Insert player/game state: HP/MP from $0501, item counts from $0503/$0504, battle vars from $05CC etc. |
| $8B-$FF | Raw tile index (border/icon/pre-composed word glyphs from CHR page) stored directly |

**Content** (decoded via `tools/dump_screendata.py`): item/equipment names (SHOT, ARROW, ROD, ARMORS), stat labels (EXPERIENCE POINTS), enemy/boss army names (GIGADA, CYTRO, GAZEI, GANGA, MEDUSA, GORGON at stream 0 / $B953), and spell/event result text. Streams overlap and chain through the shared blob -- the index just selects an entry point. These are the templates the display module renders for chapter-title, victory, game-clear, and status screens.

**Callers (9 call sites via dispatch sled $E006 -> bank 0 entry 2):**

| Caller | A (sound/mode) | Context |
|--------|----------------|---------|
| $CFA6 | varies | RPG battle display update (between rounds) |
| $D170 | $4F | Chapter title screen (chapter fanfare jingle) |
| $D1CE | $12 | Screen transition display |
| $D1E4 | $67/$66 | Game clear screen ($67 if flag set, $66 otherwise) |
| $D26E | $65 | Victory fanfare screen (after final battle) |
| $D4D0 | $5F | Dungeon/cave entry screen |
| $D4F9 | $60 | Town entry screen |
| $D590 | varies | Generic area display (parameterized by caller) |
| $D5A2 | $0F | Entity/status display with follow-up processing |

The A register is passed as $3B to $B000 and determines which screen to render + which sound to play. Sound IDs match the sound system ($4F=chapter fanfare, $5F=dungeon music, $60=town music, $65=victory, $66/$67=game clear).

#### Bank 3 -- RPG Battle Engine

Bank 3 is the turn-based RPG battle system. Dispatched via the INC $3A sled at $E05F-$E06D -> `LDA #$03; JMP $E11E`. The first 4KB ($8000-$8FFF) is data, the remaining ~12KB ($90AD-$BFEF) is code. Called from bank 7 $C883/$C89D and bank 5 $AE8D.

**Jump table at $8000** (5 active entries):

| Idx | Address | Location | Function |
|-----|---------|----------|----------|
| 0 | $90AD | Bank 3 | Battle init (check $B593, then full init sequence) |
| 1 | $C6FD | Bank 7 | Party stat processing (mode 0: normal stat update) |
| 2 | $90B2 | Bank 3 | No-op RTS (battle already running) |
| 3 | $C703 | Bank 7 | Party stat processing (mode 1: battle stat update) |
| 4 | $C295 | Bank 7 | Battle UI/display helper |

**Data-Range Map:**

| Range | Size | Description |
|-------|------|-------------|
| $8000-$800F | 16B | Jump table (5 entries + 3 null) |
| $8010-$8018 | 9B | Battle configuration header (3 x 3-byte records) |
| $8019-$845F | ~1095B | Encounter index groups (per chapter/area, navigated by $B56D) |
| $8460-$84E4 | 133B | Enemy formation table (12 x 10B: count + enemy IDs, $FF-padded) |
| $84E5-$8605 | ~289B | Battle grid layouts (~29 x 10B: header + 3x3 cell grid, $26=empty) |
| $8606-$865B | 86B | Enemy stat table (HP, attack, defense, speed values) |
| $865C-$8BFF | ~1444B | Sparse encounter placement data ($FF-heavy, $F3/$F4 markers) |
| $8C00-$8FFF | ~1024B | Palette, sprite, and tile layout data (includes $8B56 palette block) |
| $9000-$90AC | ~173B | Tile/sprite animation data |
| $90AD-$967A | ~462B | Battle init + screen setup + enemy turn processing |
| $967B-$9FFF | ~2437B | Battle state management, command processing, spell/attack dispatch |
| $A000-$A7EF | ~2032B | Spell/attack computation and damage effects |
| $A7F0-$AFFF | ~2064B | Attack handlers, encounter stat initialization |
| $B000-$B7E0 | ~2017B | State computation, damage calculation, data transformation |
| $B7E1-$B7FF | ~31B | Palette/config data (embedded) |
| $B800-$BFEF | ~2032B | Round execution, audio/animation, action dispatcher |
| $BFF0-$BFFF | 16B | Padding/unused |

**Battle Init Sequence ($90B3):**

1. `queue_sound($FF)` -- silence all audio
2. Check $32 (encounter type): if set, $2A=3, set $0707 bit 1
3. `queue_sound($62)` -- start RPG battle music
4. `set_chr_mode(5)` -- load battle CHR tiles
5. Compute battle difficulty: `$56 = ($E0 >> 1) + $E1` (world + chapter derived)
6. `JSR $940A` -- battle screen setup (PPU off, init $91DE/$921C/$928E/$9315/$92D7, draw screen, PPU on)
7. `JSR $9374` -- battle state initialization
8. `JSR $B5AB` -- encounter party setup
9. Load nametable from $05D4, start battle with `JSR $CFA1(1)`

**Battle Main Loop ($90ED):**

```
$90ED: JSR $D000                   ; frame processing (bank 7 helper)
       LDA $0506                   ; battle state
       BNE -> state 1/2 handling   ; non-zero = ending/over
       ; --- State 0: battle in progress ---
       JSR $CA04                   ; player input/command check
       BEQ -> cleanup              ; no input = battle over
       JSR $9444                   ; round setup (redraw, init)
       $57 = 1                     ; round active flag
       JSR $B826                   ; execute round (resolve actions)
       DEC $05DA                   ; decrement turn limit timer
       JSR $9857                   ; party result processing (scan $0529 for active members)
       JSR $D049                   ; frame update
       JSR $CFA9                   ; display update
       JSR $987F                   ; enemy result processing (check $C837 alive count)
       JSR $9658                   ; enemy turn processing
       INC $05CE                   ; round counter
       ; --- State 1: battle ending ---
       JSR $CFA1($0E)              ; transition display
       JSR $CF88                   ; cleanup display
       ; --- Cleanup (all states) ---
       JSR $91C3                   ; reset battle state
       JSR $947F                   ; finalize screen
       wait_nmi
       Clear $0620-$07FF           ; wipe entity slots (battle entities)
       $031C = $0E, $57 = 0        ; restore game state
```

**Battle State ($0506):** 0 = in progress, 1 = ending (win/loss transition with display), 2 = immediate cleanup.

**Key Battle RAM:**

| Address | Purpose |
|---------|---------|
| $0500 | Nametable tile buffer (shared) |
| $0503 | Current command/action |
| $0506 | Battle state (0=running, 1=ending, 2=over) |
| $050E | Enemy alive status ($FF=all dead) |
| $0529+ | Party member status slots |
| $054D+ | Party member action results |
| $05A0-$05AD | Party attack targets (14 bytes, $FF=inactive) |
| $05AE-$05BB | Enemy attack targets (14 bytes) |
| $05CE | Round counter |
| $05D4 | Base nametable config |
| $05DA | Turn limit timer |
| $05E0-$05E5 | Action resolution data (attacker/target/result) |

**Enemy Turn Processing ($9658):**

Clears turn state ($05D7, $05CD, $05D9, $0506). Checks special action codes at $05A0: $28 = call $A4EE (formation change), $27 = call $A510 (special command). Then: wait_nmi, JSR $C7F9 (enemy AI decision), JSR $C837 (alive count check), check battle state and $050E. If enemies remain, call $CA04 for next player input.

**Round Execution ($B826):**

Initializes action slots $05E0-$05E5. Calls $B805 (compute action order). If no party action ($05E1=0), sets $05E0=$FF (skip). If no enemy action ($05E4=0), sets $05E3=$FF. Resolves party action first; if $05E0 negative (no action), copies enemy data. This implements the turn-based priority system.

**Encounter Data System ($8019-$8BFF):**

The encounter data is a multi-level structure navigated by $B56D based on $82 (chapter/area index).

*Level 1 -- Index groups ($8019+):* Each group: 1 count byte + count * 3-byte records. Format: match_value (compared to $94 at $B59E), flags (bit 7 = special encounter at $05CC), sub-count (AND $7F = number of 12-byte sub-entries to skip). $B593 searches for $94 match within the current group.

*Level 2 -- Enemy formations ($8460):* Block header byte = total formations (12). Each formation: 10 bytes (1 count + up to 9 enemy IDs, $FF-padded). The header formation at $8461 has 8 enemies for the tutorial/default encounter. Formation enemy IDs reference army types:

| ID | Likely Army (dict group 13) |
|----|----------------------------|
| $23 | BASIDO SQUAD area enemies |
| $24 | AIR SQUAD area enemies |
| $26 | ZODOR DIVISION area enemies |
| $0B-$1D | Individual unit types within armies |

*Level 3 -- Grid layouts ($84E5):* ~29 records of 10 bytes: header ($08 = standard) + 9 cells (3x3 battle grid). Each cell = enemy unit ID or $26 (empty). Defines the spatial arrangement of enemies on the RPG battle screen.

*Level 4 -- Enemy stats ($8606):* Numeric stat table with small values (0-$32). Contains HP, attack, defense, speed per enemy unit type.

*Level 5 -- Placement data ($865C-$8BFF):* Sparse $FF-filled table with occasional enemy type IDs and $F3/$F4 markers (encounter triggers or special formation variants). Indexed by encounter type for special placement rules.

**Attack/Spell System (bank 3 $A000+ and bank 7 $C0C4+):**

The RPG battle uses a FORMATION-BASED tactical system, not traditional HP subtraction. Attacks either hit or miss enemy units on a 3x3 grid. The outcome is determined by formation matchups and RNG, displayed as palette changes (damaged/destroyed).

*Attack parameter setup (bank 3):* Functions at $A02A, $A047, etc. load 5 parameters into $046E-$0472:

| Address | Purpose |
|---------|---------|
| $046E | Attack flag bitmask (which target slots this affects) |
| $046F | Base animation type (X for damage dispatch: 0=basic, 1=spell, 2=magic, $0C=special) |
| $0470 | Display/animation ID for $CFA1 (screen effect) |
| $0471 | Target offset for result storage ($054D + attacker + $0471) |
| $0472 | Critical hit flag mask (AND with target to check vulnerability) |

*Attack execution ($A74A):*
1. Check target flags $054F,Y: if already attacked (bit 0), play result animation
2. If not attacked: check $046E AND flags for valid target
3. Hit check via bank 7 $CC43: reads $0502 (command type), checks $0503 (subtype), RNG via $CE8D
4. If hit: dispatch animation ($C0C4 with X=$046F), mark target ($054F |= $046E), set result ($054D = 3)
5. If miss: display "miss" ($CFA1 #$07)

*Damage dispatch (bank 7 $C0C4):*
- Checks $0555,Y (target defense): defended -> $C4E3 (row $C6), undefended -> $C52E (row $C7)
- Dispatches animation by damage type X: 0=$C185 (sword, sound $15), 1=$C1A5 (spell, sound $17), 2=$C1B2 (magic, sound $0F), $0C=$C124 (special)
- Other X values (3-11): lookup sub-index from $C115 table -> $C1E1 (generic animation with entity spawn)

*Effectiveness tables ($B8B0, bank 3 $8A26/$8A43):*
- Base table at $8A26 (29 entries): normal formation effectiveness per unit matchup
- Enhanced table at $8A43 (29 entries, when $05CA set): stronger version (first 3 entries differ: $88->$C8, $89->$C9, $8A->$CA)
- Each byte encodes: bits 7-6 = palette group (visual damage level), bits 5-0 = tile index. Applied to $04A1+ (palette shadow RAM) to show damaged/destroyed units on the 3x3 grid

*Spell effects ($A553):*
1. Check MP availability ($CB16)
2. Optional: spend resource via $99BF (returns negative = insufficient)
3. Attacker animation via $C793
4. Command type check ($0502): $0C-$0E = formation commands (LIBCOM/MONECOM/MOSCOM), $10 = enhanced
5. Target resolution ($CB83): check if spell affects target
6. If effective: sound $33 (spell cast noise), apply result

*Player commands ($0502 values):*

| ID | Command | Effect |
|----|---------|--------|
| $02 | Standard attack | Direct unit attack on grid |
| $0C | LIBCOM | Formation: offensive pattern |
| $0D | MONECOM | Formation: economic/resource |
| $0E | MOSCOM | Formation: defensive pattern |
| $10 | Enhanced | Boosted version of current formation |
| $15 | Shield 1 | Defense (sets $054F bit 5) |
| $17 | Shield 2 | Defense variant (sets $054F bit 4) |

**Battle Command System (bank 7 $CA04-$CAF9):**

Six functions handle party management, stat lookup, and rewards during RPG battles:

| Address | Function | Description |
|---------|----------|-------------|
| $CA04 | Find alive member | Scan $054D slots 6..0 for != $FF. Returns X=slot index, or X=0 if all dead |
| $CA16 | Find target | Scan $054D for enemy in range $19-$1B (targetable types). Returns A=0 hit or A=$45 none |
| $CA30 | Command menu | Read formation ($05C2/$05C3), lookup bitmask from $8C50/$8C56. Shift-test for available commands. Set $0503 from $05D4 |
| $CA62 | HP lookup | Base HP from $8C10[($84+5)*2]. If enemy: adjusted by $03BE stats - $8CA1[type] difficulty |
| $CA9A | MP lookup | Base MP from $8C10[($84+5)*2+1]. If enemy: adjusted similarly. Result stored in $8C-$8E (BCD) |
| $CAE1 | Reward accum | Read 2-byte (gold, XP) from ($00) pointer via $CDD5. Add to $05C0/$05C1 totals |

**Battle Stat Progression Table (bank 3 $8C10, 30 x 2 bytes):**

| Level | HP | MP | | Level | HP | MP |
|-------|----|----|---|-------|----|----|
| 0 | 20 | 10 | | 15 | 140 | 148 |
| 1 | 25 | 10 | | 16 | 148 | 155 |
| 2 | 30 | 10 | | 17 | 156 | 165 |
| 3 | 34 | 10 | | 18 | 164 | 180 |
| 4 | 42 | 12 | | 19 | 172 | 185 |
| 5 | 50 | 16 | | 20 | 180 | 190 |
| 6 | 58 | 20 | | 21 | 188 | 200 |
| 7 | 66 | 52 | | 22 | 196 | 204 |
| 8 | 74 | 68 | | 23 | 204 | 208 |
| 9 | 82 | 78 | | 24 | 212 | 218 |
| 10 | 90 | 84 | | 25 | 220 | 220 |
| 11 | 98 | 94 | | 26 | 228 | 228 |
| 12 | 116 | 100 | | 27 | 236 | 236 |
| 13 | 124 | 108 | | 28 | 244 | 245 |
| 14 | 132 | 115 | | 29 | 255 | 255 |

Indexed by `($84 + 5) * 2` where $84 = screen/world position (acts as level indicator). Enemy stats use the same table but offset by $8CA1[type] difficulty modifier (values 3-7, subtracted from player level).

**Command Availability (bank 3 $8C50/$8C56):** Bitmask tables. $8C50+X (6 bytes) = formation X's command bits, shifted right by $05C3 count. Carry after shift = command available. $8C56+Y = target formation bits.

**Bank 3 Sound Usage:**

$77 (30 call sites) is the battle sync marker -- priority 0 in $800E table, intentionally no-op. Used as rhythm signal during battle processing. Actual sounds: $62=battle music (init), $79=victory, $34=battle result fanfare, $33/$26=spell cast, $7F/$6E=boss battle variants, $71=magic cast noise, $00=silence marker.

#### Bank 4 -- Screen/Tile/Entity Data Engine

Bank 4 is the primary data-processing bank, responsible for loading WorldScreen records, rendering tile nametables, setting palettes, and spawning entities. It has a 25-entry jump table at $8000 and is dispatched via the INC $3A chain at $E074-$E0A4 (trampoline loads bank 4 at $E0A6).

**Jump table at $8000** (25 entries):

| Idx | Address | Function |
|-----|---------|----------|
| 0 | $8930 | Entity sprite attribute lookup (via $9F3B table) |
| 1 | $896E | Entity behavior sequence advance (via $9FBB table) |
| 2 | $89A7 | Entity type-specific processing dispatch (via $A03B table) |
| 3 | $8AB8 | Post-screen-load OAM/sprite fixup |
| 4 | $8AFA | Entity collision/interaction check |
| 5 | $8B80 | Entity state reset |
| 6 | $8B86 | Entity state cleanup |
| 7 | $8FEE | CHR data loader for nametable/screen layout |
| 8 | $8D37 | Sprite visibility manager (OAM culling + ambient sound) |
| 9 | $8B19 | Entity movement update (projectile velocity + position) |
| 10 | $8BE3 | Ambient sound setup (called when $B1 bit 7 set) |
| 11 | $812E | Screen load phase selector (reads $82 for phase) |
| 12 | $813B | **Full screen load sequence** (main entry) |
| 13 | $81D2 | Single tile nametable update (tile -> metatile -> PPU addr) |
| 14 | $825A | Tile collision type lookup ($0500 buf -> $99FB attrib >> 4) |
| 15 | $826B | Entity grid position set (packed coord -> screen X/Y + 8px center) |
| 16 | $8282 | Clear OAM + entity slots |
| 17 | $830A | Screen event/music selector ($BF event + $B2 content -> sound ID) |
| 18 | $8354 | **Palette loader** (reads $BC/$BD from WorldScreen) |
| 19 | $8500 | **Nametable column builder** (tile -> metatile -> CHR tile pipeline) |
| 20 | $8640 | **Entity/object spawn** (reads ObjectSet $B3 from CHR data) |
| 21 | $841B | **Tile section loader** (DataPointer $B8 -> CHR bank + tile sections) |
| 22 | $8CD2 | OAM sprite icon renderer (tile IDs from $8D23 -> OAM buffer) |
| 23 | $83DB | Ambient sound config loader ($B1 bits 0-1 -> $93E3 table) |
| 24 | $8747 | Entity spawn validation + type dispatch |

**Screen Load Sequence** ($813B):

The full screen load calls these subroutines in order:
1. `$819F` -- Compare new/old $B0 (ParentWorld), queue transition sound $61 if changed
2. `$E5AA` -- PRG bank + mode setup
3. `$841B` -- Tile section loader (DataPointer -> CHR bank selection + tile data read)
4. `$8500` -- Nametable column builder (tile IDs -> metatiles -> PPU nametable data)
5. `$8354` -- Palette loader ($BC -> BG palette, $BD -> sprite palette)
6. `$83DB` -- Ambient sound config ($B1 bits 0-1 -> ZP $C7-$CA)
7. `$8282` -- Clear OAM buffer ($0200) and entity slots ($0601+)
8. `$8640` -- Entity/object spawn setup (read ObjectSet data from CHR)
9. `$83F4` -- EntityFlags ($BE) type extraction (AND #$0F, clamp to 0-3)
10. `init_sprites` ($EA7E) + entity bank 5 dispatch

**Key Data Tables in Bank 4:**

| Address | Size | Name | Format | Purpose |
|---------|------|------|--------|---------|
| $8000 | 50B | jump_table_b4 | 25 x u16 | Bank 4 dispatch table |
| $93E3 | 16B | ambient_sound_cfg | 4 x 4B records | ZP $C7-$CA per $B1 type (ambient sound params) |
| $93F3 | varies | palette_index | 4B per palette ID | BG/sprite palette -> color group indices |
| $951F | varies | palette_colors | 1B per entry | NES color values ($00-$3F) for palette construction |
| $95FB | varies | minitile_table | 4B per MiniTile ID | 2x2 CHR tile indices per MiniTile |
| $99FB | varies | tile_attrib | 1B per tile ID | Collision/attribute flags per game tile |
| $9AFB | varies | tile_table | 4B per tile ID | 2x2 MiniTile IDs per game tile |
| $9EFB | 32B | entity_oam_flags | 32 x u8 | OAM attribute flags per entity type (values 0/1/3) |
| $9F1B | 32B | entity_size_flags | 32 x u8 | Entity size/priority flags per type (values 0/1/3) |
| $9F3B | 64B | entity_sprite_tbl | 32 x u16 | Entity type -> sprite CHR tile data ($A630-$A978) |
| $9F7B | 64B | entity_oam_layout | 32 x u16 | Entity type -> OAM sprite layout data ($A98C-$ABEC) |
| $9FBB | 64B | entity_seq_tbl | 32 x u16 | Entity type -> animation sequence data ($A429-$A628) |
| $9FFB | 64B | entity_anim_tbl | 32 x u16 | Entity type -> animation state data (many=$A54C) |
| $A03B | 64B | entity_sprite_comp_tbl | 32 x u16 | Entity type -> sprite composition sub-tables ($A0BB-$A32B) |
| $A07B | 64B | entity_hitbox_tbl | 32 x u16 | Entity type -> hitbox/collision data ($A32F-$A425, $AFD9+) |
| $A0BB | ~622B | entity_comp_subtables | nested ptr16 | Per-sub-state sprite composition pointers -> $AC00+ data |
| $A32F | ~256B | entity_hitbox_data | count+4B records | Hitbox definitions: count + N*(Y-off, X-off, W, H) per type |
| $A429 | ~512B | entity_seq_data | u8 stream | Animation frame sequences ($FE=group sep, $FF=end, $80=loop) |
| $A630 | ~856B | entity_sprite_data | 4+4B records | CHR tile base (4B) + OAM attributes (4B) per direction |
| $A98C | ~612B | entity_oam_data | Y/tile/attr groups | Multi-sprite layout: offsets + tile/attr pairs, $FF=end |
| $AC00 | ~4404B | entity_sprite_comp | count+4B records | Per-frame sprite OAM data: count + N*(Y-off, attr, tile, X-off). Written to $0200 shadow OAM by bank 4 entry 2 ($89A7) |
| $BD34 | ~700B | dict_b4 | bit7-term strings | Dictionary: 119 entries (NPC names + game terms) |

**Tile Rendering Data Flow (3-level hierarchy):**

```
WorldScreen.TopTiles/BottomTiles ($BA/$BB)
    -> TileSection (32B, 8x4 grid of Tile IDs, at CHR bank 29-31 via $E8D1)
        -> tile_table ($9AFB + tile_id*4): 4 MiniTile IDs (2x2 game-tile)
            -> minitile_table ($95FB + minitile_id*4): 4 CHR tile indices (2x2 pixels)
                -> PPU nametable data (written to $0163 buffer for NMI transfer)

tile_attrib ($99FB + tile_id): collision flags per game tile
    Bit 7: walkable/property flag
    Bit 6: special interaction flag
    Bits 5-4: NES attribute (palette group) for this tile
    Bits 3-0: tile property type
```

**Palette Loading ($8354/$8399):**

Reads WorldScreenColor ($BC) and SpritesColor ($BD). Each palette ID is multiplied by 4 and added to $93F3 base to get 4 color group indices. Each group index is then used to read 3 colors from $951F (NES $00-$3F color values), with $0F (black) as the first color of each subpalette. Result written to $04A0-$04BF (palette shadow RAM, transferred to PPU $3F00 during NMI).

**Entity Spawn Data ($8640):**

ObjectSet ($B3) from WorldScreen specifies an entity data block in CHR bank 23 (0x17). The data is read into $0400 buffer and parsed:
- Bytes $F0-$FF: Position commands (high nibble $F = position setter, low nibble = slot, next byte = coordinate)
- Bytes $01-$EF: Entity spawn records (type, sub-type, position parameters)
- Byte $00: End of entity list

**Entity Data System (5 parallel tables):**

All 7 tables are 32 entries (entity types 0-31), stored contiguously from $9EFB-$A0BA:

```
$9EFB  entity_oam_flags[32]         1B each    OAM attribute base (0/1/3 -> sprite priority/palette)
$9F1B  entity_size_flags[32]        1B each    Entity size/render flags
$9F3B  entity_sprite_tbl[32]        ptr16      -> sprite CHR tile data at $A630-$A978
$9F7B  entity_oam_layout[32]        ptr16      -> OAM multi-sprite layout at $A98C-$ABEC
$9FBB  entity_seq_tbl[32]           ptr16      -> animation sequence data at $A429-$A628
$9FFB  entity_anim_tbl[32]          ptr16      -> animation state data
$A03B  entity_sprite_comp_tbl[32]   ptr16      -> per-frame sprite composition sub-tables at $A0BB-$A32B
$A07B  entity_hitbox_tbl[32]        ptr16      -> hitbox/collision data at $A32F-$A425 + $AFD9+
```

**Entity Slot Structure (stride 8, 32 slots at $0600-$06FF + $0700-$07FF):**

Primary array at $0600+X (X = slot * 8, slot 0 = player):

| Offset | Purpose |
|--------|---------|
| +0 | Entity type (0-31, indexes all 5 bank 4 tables; bit 7 = extended flag) |
| +1 | State/direction: hi4=direction/flags, lo4=behavior sub-state (indexes bank 5 sub-table) |
| +2 | X pixel position |
| +3 | Y pixel position |
| +4 | Animation sequence index ($FF=idle) |
| +5 | Packed grid pos: hi4=Y row, lo4=X col (computed from +2/+3) |
| +6 | Saved X position (used during movement animations) |
| +7 | Entity-specific data (direction result, etc.) |

Extended array at $0700+X:

| Offset | Purpose |
|--------|---------|
| +0 | Timer/counter (decremented per tick, triggers state change at 0) |
| +1 | Sub-phase within current sub-state (for multi-step actions via indexed_jmp) |
| +4 | Behavior modifier flags |
| +7 | Entity flags (bit 2 = spawn config interaction) |

32 entity slots total. Slot 0 ($0600/$0700) = player. Slots 1-31 ($0608-$06F8 / $0708-$07F8) = NPCs/enemies/objects, ticked by bank 5 entry 18 loop.

**Sprite Lookup ($8930):** type -> $9F3B ptr -> sprite data record. Sub-state bits select animation direction (lo4 * 4), then frame bits walk to the correct tile index. Each record is 4 CHR tile bases + 4 OAM attribute bytes per direction.

**Sequence Advance ($896E):** type -> $9FBB ptr -> sequence stream. Stream bytes: $00-$7F = animation frame IDs (advance one per tick), $FE = group separator (advance past), $FF = end of group (return to caller), $80 = loop back (relative jump).

**OAM Layout ($9F7B pointers):** Each layout record defines a multi-sprite entity: groups of Y-offsets, tile+attribute pairs for each 8x8 sprite piece, $FF-terminated.

**Sprite Composition ($A03B pointers, entry 2 at $89A7):** Each type has a sub-table of ptr16 values at $A0BB+, indexed by animation frame. These point to sprite composition records at $AC00+. Each record: count byte + count * 4-byte OAM entries (Y-offset, attribute, tile-ID, X-offset). The renderer at $89A7 reads the entity's animation frame from $0604+seq_data, looks up the composition record, and writes sprite pieces to the $0200 OAM shadow buffer. Handles horizontal flip (bit 7 of count = mirror, XOR $40 into attrs, negate X-offsets).

**Hitbox Data ($A07B pointers):** 6th parallel entity table. Each type points to variable-length hitbox records at $A32F-$A425 (and $AFD9+ for extended types). Format: count byte + count * 4-byte boxes (Y-offset, X-offset, width, height). Multiple boxes per type allow irregular collision shapes. Types 8-10, 11-13, 14-16, 17-19, 24-26 share the same hitbox data (groups of 3 types).

**World Map & Screen Rendering System:**

**WorldScreen Record (16 bytes per screen, stored in CHR ROM):**

Screen records are read from CHR ROM via PPU by `read_worldscreen` at bank 4 $82A1. The function reads 16 bytes into ZP $B0-$BF based on screen index $AB. CHR bank is computed as `(high_offset >> 4) + 23` from the base address returned by $EE93.

| ZP | Field | Purpose |
|----|-------|---------|
| $B0 | ParentWorld | High nibble = world area (changed triggers transition sound $61) |
| $B1 | AmbientFlags | Bit 7 = ambient sound, bits 0-1 = sound type |
| $B2 | ScreenType | Screen behavior flags |
| $B3 | ObjectSet | Entity spawn data block index (loaded from CHR bank 23 by $8640) |
| $B8 | TileFlags | Bits 5-0 = CHR mode ($38), bit 7 = carry for tile address |
| $B9 | ExitPosition | $25 = overworld, $41/$47 = town/palace |
| $BA | TopTiles | TileSection ID for upper screen half |
| $BB | BottomTiles | TileSection ID for lower screen half |
| $BC | WorldScreenColor | BG palette selector |
| $BD | SpritesColor | Sprite palette selector ($E0 = overworld, $10 = indoor) |
| $BE-$BF | Extra | Additional flags |

Adjacency/navigation data is in bytes 8-11 of the record. $FF = impassable edge.

**Screen Rendering Pipeline (bank 4 entry 12, $813B):**

```
1. $819F: Check ParentWorld change -> queue transition sound $61
2. $82A1: Read 16-byte WorldScreen record from CHR into $B0-$BF
3. $841B: Load TileSections from CHR:
   a. $EE93(bank $1A): setup CHR data read base -> $A8/$A9
   b. Compute CHR address: $BA * 32 + base (TopTiles)
   c. CHR bank = (high_offset >> 4) + 23
   d. $E8D1: NMI-driven PPU read -> 32 bytes into $0400 buffer
   e. Repeat for $BB (BottomTiles)
4. $8500: Build nametable: expand 8x4 TileSection tile IDs:
   a. Each tile ID -> tile_table ($9AFB + ID*4) -> 2x2 MiniTile IDs
   b. Each MiniTile -> minitile_table ($95FB + ID*4) -> 2x2 CHR tile indices
   c. Write to $0163 nametable buffer (8 cols x 4 rows x 4 CHR tiles = 128 entries)
5. $8354: Load palette from $BC/$BD via $93F3/$951F color tables
6. $83DB: Load ambient sound from $B1 flags
7. $8282: Clear OAM + entity slots
8. $8640: Spawn entities from ObjectSet $B3 (CHR bank 23 data -> $0400 buffer)
9. $EA7E: Initialize sprites
```

**Screen Tile Hierarchy (3-level, 32x32 pixel game tiles):**

```
Screen (256x256 pixels) = 2 TileSections stacked (8x4 + 8x4 = 8x8 game tiles)
  Game Tile (32x32 px) = 2x2 MiniTiles (tile_table $9AFB, 4 bytes per tile)
    MiniTile (16x16 px) = 2x2 CHR tiles (minitile_table $95FB, 4 bytes)
      CHR Tile (8x8 px) = raw pattern data in CHR ROM pattern table
```

- 8x8 = 64 game tiles per screen
- tile_attrib at $99FB: per-tile collision (bit 7 = walkable, bits 3-0 = property type)

**Map Navigation:**

- $AB = current screen index (lookup into WorldScreen records)
- $82 = screen index parameter for read_worldscreen
- $84 = linear progression counter (0-24, maps to level/chapter via $D386)
- Chapter boundaries at bank 7 $D386: 1(Ch1), 6(Ch2), 10(Ch3), 16(Ch4), 20(Ch5)
- Screen transitions: bank 6 $BF9B copies 6 bytes from $0590 buffer to $B8-$BD
- Navigation code at bank 7 $DCF0+: uses $0401 direction and $D332 table for transition type, checks chapter boundaries, loads adjacent screen

**Limitations:** The exact CHR bank/offset mapping for TileSection data requires tracing the NMI PPU bank switching ($E8D1 -> $EE93 base + $BA*32). The file offset of specific TileSection data cannot be determined statically without emulating the CHR bank register state.

**Data Read Helper ($EFA8):**

The universal data read function used throughout bank 4:
- If $18 >= 0 (PRG data): `LDA ($E8),Y` -- direct CPU memory read
- If $EA bit 5 set (CHR data): compute PPU address from $E8/$E9+Y, read via $2006/$2007

This allows the same code to transparently read from either PRG ROM (bank-switched) or CHR ROM (via PPU reads), controlled by $EA flags set during $EE93 setup.

#### Bank 5 -- Entity Behavior Engine

Bank 5 is the runtime behavior engine for all entities. It's dispatched via the INC $3A sled at $E0AB-$E0D3 -> `LDA #$05; JMP $E11E` at $E0D5. Almost entirely code (~16KB), no large data tables.

**Jump table at $8000** (20 entries):

| Idx | Address | Function |
|-----|---------|----------|
| 0 | $9B76 | Player spawn/init (set type 5, position, queue sound) |
| 1 | $803A | **Entity behavior tick** (per-entity: type -> sub-table -> sub-state -> handler) |
| 2 | $9FE0 | Player sprite OAM positioning |
| 3 | $A173 | Event-triggered entity spawn (from WorldScreen $BF flags) |
| 4 | $A43E | Player damage calculation (HP -= amount, set hurt flags) |
| 5 | $A482 | Player attack initiation (set type 2, queue sound $3A) |
| 6 | $A50F | Entity interaction check |
| 7 | $A52C | Entity collision response |
| 8 | $A59D | Entity death/despawn handler |
| 9 | $A55A | Entity knockback/stun |
| 10 | $A604 | Player item/magic use |
| 11 | $A839 | Entity AI waypoint movement |
| 12 | $A874 | Entity aggro/pursuit AI |
| 13 | $A896 | Entity patrol/wander AI |
| 14 | $AD1E | Event/progress trigger check ($95 chapter state) |
| 15 | $AEBD | Screen entry entity placement ($B9 ExitPosition) |
| 16 | $AEE3 | Entity screen bounds checker (edge proximity flags) |
| 17 | $BD18 | HUD/status nametable writer (PPU addr from $FF24 table) |
| 18 | $8028 | **Entity tick all** (loops slots 1-31, calls entry 1 for each) |
| 19 | $AE0D | Screen transition entity cleanup |

**Two-Level Entity AI Dispatch (entry 1 at $803A):**

```
entity_type ($0600,X) AND #$7F
    -> type_behavior_table[$80E5 + type*2] = per-type sub-table pointer
        -> sub_state ($0601,X) AND #$0F
            -> sub_table[sub_state*2] = behavior function pointer
                -> JMP ($0002) = execute handler
```

The type behavior table at $80E5 holds 64 entries (types 0-63). Each points to a sub-table of up to 16 ptr16 function pointers (one per sub-state). Types >= $10 with extended flag trigger additional processing at $80AD.

**Complete Entity Type Map (64 types at $80E5):**

*Simple Enemies & Projectiles:*

| Type | Sub-table | States | AI Handler | Role |
|------|-----------|--------|------------|------|
| 0-1 | $8165 | 10 | $893F | Basic melee enemies (standard AI: patrol + pursue) |
| 2 | $8179 | 10 | $893F | Player attack/projectile entity |
| 7-9 | $81DB | 16 | $893F | Ranged enemy variants (all states use standard AI; state 15 -> $B4DA special) |
| 13-14 | $822B | 16 | $8D45 | Contact damage enemies (check proximity via $F40D, call player_damage with $0701 as amount) |
| 15 | $824B | 4 | $8DA4 | Timed animation enemy (timer + blink, on expire -> $A4AE/$A5CB death check) |

*Player System:*

| Type | Sub-table | States | Role |
|------|-----------|--------|------|
| 5 | $81A3 | 16 | **Player character** (see Player Sub-States section above) |
| 10 | $81FB | 4 | Grid trigger/pickup (activates when player steps on same tile, reads $8A23 data tables) |
| 11 | $8203 | 4 | Interactive object (proximity + button check, sound $67, multi-state: idle/dir/move/wait) |

*NPC & Interaction:*

| Type | Sub-table | States | Role |
|------|-----------|--------|------|
| 3 | $818D | 8 | NPC dialogue entity |
| 4 | $819D | 3 | Collectible/item entity |
| 6 | $81C1 | 13 | Door/portal (timer animations, state 1 = attack check, state 3 = sound, states 11-12 = scripted) |
| 12 | $820B | 16 | Proximity sensor (computes grid pos, compares to player + $0317/$0318, multi-mode: states 7/9-11/13-14 are unique) |
| 40-51 | $8373 | 9 | **NPC/companion** (12 types share handler $9C7F: 12-frame delay, check readiness via $994D, store target in $031A, call $F0BE spawn helper) |

*Extended Enemies (types >= 16, use $80AD extended check):*

| Type | Sub-table | States | AI Handler | Role |
|------|-----------|--------|------------|------|
| 16 | $8253 | 8 | $8DCE | Enemy spawner (timer -> spawn entity via $F0BE based on $0607 config) |
| 17 | $8263 | 8 | $8E80 | Timed spawner/emitter (randomized delay from $E0 table, spawn via $F0BE with A=5) |
| 18 | $8271 | 8 | $8FEF | Pursuit enemy (standard aggro AI $A874, decrements $93 on flag) |
| 19 | $8279 | 6 | $9014 | Pursuit + ranged (calls $A666 range check, fires projectile) |
| 20 | $8285 | 6 | $90E7 | Patrol enemy (standard movement + bank 4 dispatch) |
| 21 | $828F | 7 | $917C | Multi-phase enemy (7 sub-states with unique behaviors) |
| 22 | $829D | 8 | $929B | Complex enemy (8 states including $9314 special attack) |
| 23 | $82BD | 5 | $93D6 | Special enemy (5 states, extended flag sets $71) |
| 24 | $82C7 | 6 | $94DA | Boss-type enemy (6 states, $71 flag only in non-idle states) |
| 25 | $82D3 | 5 | $8EB8/$8ECB + custom | Variant enemy (blink/move + custom states) |
| 26 | $82DD | 5 | similar | Variant enemy |
| 27 | $82E7 | 5 | similar | Variant enemy |
| 28 | $82F1 | 6 | similar | Variant enemy (extended flag sets $71) |
| 29 | $82FD | 5 | similar | Variant enemy (extended flag sets $71) |
| 30-31 | $8307 | 5 | $8FEF | Pursuit enemy pair (shared sub-table, aggro AI) |
| 32 | $8311 | 5 | $8FEF | Pursuit enemy variant (state 3-4 = $98A5/$98B6 custom) |
| 33 | $831B | 4 | $98F9 | Timer enemy ($71 flag only in non-idle; state 3 = $8F29 special) |
| 34 | $8323 | 9 | $990D | Aggressive enemy (pursuit AI $A874 on ready, states 3-4 = $9979/$999B attack) |
| 35 | $8335 | 9 | $990D | Aggressive enemy variant (states 3-4 = $9A02 shared attack) |

*Boss Enemies (complex multi-phase):*

| Type | Sub-table | States | AI Handler | Role |
|------|-----------|--------|------------|------|
| 36 | $8347 | 7 | $9A81 | Boss A (90-frame timer, states 3-6 = $9AD5/$9BA1/$9BA6/$9BC5 attack phases) |
| 37-38 | $8355 | 7 | $9A81 | Boss B pair (same structure, state 3 = $9BD6 variant attack) |
| 39 | $8363 | 8 | $9A81 | Boss C (8 states, states 6-7 = $9C17/$9C70 extra phases) |
| 59-61 | $8409 | 6 | $95F0 | Boss minions (pursuit via $9001, states 3-5 = $9E2D/$970F/$9E98 unique) |
| 62 | $8415 | 5 | $95F0 | Boss minion variant (state 3 = $9F18, state 4 = $8F78 grid pos) |
| 63 | $841F | 4 | $9F2B | Final boss (calls $90E7, sets $26=$30 invuln timer, state 3 = $B0F2 special attack, $71 flag) |

*Visual/Scripted Entities:*

| Type | Sub-table | States | Role |
|------|-----------|--------|------|
| 52 | $8385 | 16 | Tile animator (timer -> PPU tile writes via $E964, states 3-4 = $B66C/$B6BD sequence, states 8-15 = $B705 shared) |
| 53 | $83A5 | 8 | Animated tile (cycles tile $20/$26 based on $0702 parity, state 3-4 = $B774 alt, state 5 = $B7C1) |
| 54 | $83BB | 14 | Scripted NPC (fixed position $58/$80, state $83, 6 unique handlers for cutscene movement) |
| 55 | $83D7 | 4 | Spell/magic effect (checks $0338 flag, positions at X=$58, decrements $93 counter) |
| 56 | $83E5 | 6 | Random spawn/projectile (positions relative to player with $E6/$E7 randomization, states 3-4 = $BA99 variant) |
| 57 | $83F1 | 6 | Event trigger (checks $25 flag, dispatches bank 4 entry $3E, states 3-4 = $BB3A, state 5 = $BBBB) |
| 58 | $83FD | 6 | Multi-phase scripted (indexed_jmp on $0706, reads position from $FFB0 table, states 3-4 = $BC89) |

**Extended Type Flag ($80AD)**: Types 19, 20, 23, 28, 29, 61, 63 always set $71 (blocks certain game actions while active). Types 24, 33 only set $71 when not in sub-state 0 (idle). This prevents player actions during boss attack sequences.

**Common State Pattern** (types 16+): State 0 = main AI/behavior, State 1 = $8EB8 (hit blink: decrement timer, toggle visibility, on expire -> $A4AE/$A5CB death check), State 2 = $8ECB (movement step: increment $0606 to 9 steps then reposition on grid).

**Entity Tick Flow (per frame):**

1. Bank 6 game_loop calls bank 5 entry 18 (tick all entities)
2. Entry 18 loops X=$08,$10,...,$F8 (slots 1-31), calls entry 1 for each
3. Entry 1 skips inactive ($0601=0) and projectile ($0601>=$F0) entities
4. Type lookup -> sub-table -> sub-state -> specific behavior handler
5. Handler may call bank 4 (sprite lookup, collision grid) or queue sounds

**Player Sub-States (Type 5, sub-table at $81A3):**

Entity state byte $0601 format: bits 7-4 = facing direction ($10=right, $20=left, $40=up, $80=down), bits 3-0 = sub-state (0-15). Direction mapping table at $89AC.

| Sub | Handler | Name | Description |
|-----|---------|------|-------------|
| 0 | $873D | Idle | Timer tick ($874F), animate bank 4 entry 7. On expire: clear state, silence ($FF) |
| 1 | $873D | Walk | Same as idle (direction in high nibble drives movement at higher level) |
| 2 | $873D | Walk | Same |
| 3 | $873D | Walk | Same |
| 4 | $873D | Walk | Same |
| 5 | $875E | Screen scroll | 4-phase via indexed_jmp on $0701 sub-phase: (0) save X pos, set state $15, sound $13; (1) slide up -2px/frame until X<$18; (2) slide down +2px/frame until X>=$B0; (3) slide back to saved pos. Sound $18 on completion |
| 6 | $873D | Post-scroll | Same as idle handler (entered after screen scroll completes) |
| 7 | $87CB | NPC interact | Timer + check $033E (NPC flag) AND $BF bit 2 (interact). If met: change entity type to 0 or 2 (based on $32), call $F0BE, set $95=8 |
| 8 | $87F6 | Event interact | Timer + check $0303 (event flag). Shares interact path with sub-state 7 ($87D5) |
| 9 | $873D | (Reserved) | Same as idle (no known trigger) |
| 10 | $8802 | Position sync | Copy slot 0 X/Y ($0602/$0603) to entity. If slot 0 idle: copy state. If active: bank 4 entry 3 (OAM fixup) |
| 11 | $881F | Hurt/knockback | Decrement $0700 timer. While active: knockback physics via $FBE9 with A=7, bank 4 dispatch. On expire: return to idle |
| 12 | $8836 | Stunned | Animation only -- dispatch bank 4 entry 7, no input processing |
| 13 | $8836 | Stunned | Same as sub-state 12 |
| 14 | $883B | Slide/attack | Slide X -= ($7F AND 3) per frame. If X < $10: return to idle. Then check attack conditions: $0336 (weapon equipped), $03C2 (cooldown ready), $82 (game mode). If eligible: set $0607=$20, compute direction vector from $0601, call collision $F8E6 |
| 15 | $88F6 | Death | Timer increments $0700 from 0 to $78 (120 frames). At $3C (60 frames): if sub-state=6, sound $1D; check $BE bits 5-4 for death flags -> $0334/$031C. Blink effect (frame AND 7 or AND 3 -> $E39B/$E3A3 dispatch). At $78: clear $0601=0 (respawn). If $0704 reaches $20: clear 9 adjacent entity slots (death cleanup) |

Sub-state activity flags at $89BC (1=busy/skip AI, 0=allow AI processing):
```
Sub:   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
Flag:  0  1  1  0  0  1  1  1  0  0  0  1  0  1  1  0
```

**Common helper $874F** (timer tick): Sets $22=2 (speed divisor). Decrements $0700,X. If >0: dispatch bank 4 entry 7 (CHR animation update), return NZ. If expired: return Z (caller then transitions to idle).

**Player damage ($A43E, entry 4):** A = damage amount. Checks defense flags ($28, $0302) -- armor halves damage ($0302=1), double armor quarters it ($0302=2). Subtracts from $81 (HP) with floor at 0. Sets $0707 bit 7 (damage indicator), increments $03F6 (hit counter), invulnerability timer $20=4.

**Player attack ($A482, entry 5):** Checks entity type < 4 (attack state only). Queues sound $3A, calls $85C2 (spawn attack projectile). Changes player type to 2 (attack entity), preserves direction in $0601 high nibble, dispatches bank 4 for animation setup.

#### Text/Dialogue Engine (Banks 1 + 2)

The text system spans three banks: bank 1 (UI/screen setup), bank 2 (text decode/render), and CHR banks 22-24 (dialogue data). Bank 7 coordinates via dispatch trampolines.

**CHR Dialogue Data Format (CHR banks 22-24):**

Dialogue text is stored in CHR ROM (normally used for graphics) and read via PPU $2006/$2007. The game repurposes 12KB of CHR space as a text database, accessed through the data read helper at $EFA8.

CHR bank mapping (mode 3, bank 1 $80B3): sub-index 0-7 -> CHR bank 22, sub-index 8-29 -> CHR bank 23, sub-index 30 -> CHR bank 24, sub-index 31 -> CHR bank 25.

File offsets: bank 22 = $36010, bank 23 = $37010, bank 24 = $38010.

Entry counts: bank 22 ~77 entries (NPC/shop/service dialogue), bank 23 ~3 long entries (RPG battle text + story, mixed with tile data), bank 24 ~11 entries (quest/story dialogue).

Encoding (same tile IDs as dictionary):
- $00-$09: digits 0-9
- $2C: space
- $30-$49: letters A-Z
- $4A-$4F: punctuation (. , ' ? ' -)
- $79: period (sentence end)

Stream control codes:
- $7A: newline (advance to next line)
- $7C: question mark
- $7D: exclamation mark
- $7E: paragraph break / new text box
- $7F: end of dialogue entry
- $FA/$FE: padding bytes after control codes (skip)

Inline parameter codes ($50-$6F):
- $52: {HERO} -- insert player character name
- $50-$51, $53-$6F: inline references to game values (item counts, spell names, NPC names, gold amounts). Exact mapping varies by context.

Format codes ($10-$2F):
- $1E: conditional text branch
- $2D-$2F: text box formatting/positioning
- Others: menu indices, display mode switches

Sample decoded dialogue (bank 22, entry 0):
```
WHAT ELSE?
HOW MUCH MONEY DO {HERO} NEED?
WE CAN'T LOAN {HERO} ANY MORE-
```

**Text Command Byte Format (bank 1 entry 0 at $8044):**

| Bits | Field | Values |
|------|-------|--------|
| 7:5 | Mode | 0=simple, 1=dialogue box, 3=CHR dialogue, 5=special dialogue |
| 4:0 | Sub-index | Selects text entry within mode (0-31) |

Mode 3 sub-index maps to CHR bank: 0-7=bank+0, 8-29=bank+1, 30=bank+2, 31=bank+3. These correspond to CHR banks 22-24 (dialogue data).

**Dictionary System (bank 2):**

Dictionary pointer table at $99B7 (16 entries, ptr16 each) points to 16 word groups at $99D7-$9C37. Each word is a sequence of tile IDs terminated by bit 7 on the last byte. 97 words total.

Dictionary reference byte: high nibble selects group (index into $99B7), low nibble selects word within group (skip N bit-7-terminated entries). Format: `$GW` where G=group, W=word index.

**Complete Dictionary (97 words, decoded via `tools/temp_decode_dict.py`):**

| Grp | # | Contents | Category |
|-----|---|----------|----------|
| 0 | 1 | (spaces -- padding) | Blank |
| 1 | 2 | KEY, AMULET | Key items |
| 2 | 2 | R-ARMOR, L-ARMOR | Equipment |
| 3 | 5 | HOLYROBE, M-BOOTS, M-SHIELD, BREAD, MASHROOB | Equipment/consumables |
| 4 | 7 | (space), ROD, FLAME, STARDUST, CIMARON, CRYSTAL, ISFA | Weapons/items |
| 5 | 9 | HAMMER, R-SEED, CARPET, HORN, OPRIN, RING, (sp), (sp), MAP | Items |
| 6 | 7 | (space), SWORD, SIMITAR, DRAGOON, KASHIM, ROSTAM, LEGEND | Weapons (named swords) |
| 7 | 15 | BOLTTOR1-3, FLAMOL1-3, PAMPOO, MARITA, RESEALO, VELVER, CORBOCK, SHRINK, CARABA, DEFENEE, RAMIPAS | Magic spells (levels 1-3) |
| 8 | 5 | LIBCOM, MONECOM, MOSCOM, RAINCOM, SPRICOM | Formations/commands |
| 9 | 11 | CORONYA, SUPICA, GUN MECA, PUKIN, GUBIBI, MUSTAFA, EPIN, RAINY, KEBABU, FARUK, HASSAN | Party members / NPCs |
| 10 | 3 | FIGHTER, SAINT, MAGICIAN | Character classes |
| 11 | 1 | (space) | Blank |
| 12 | 12 | CYGNUS, LIBRA, ARIES, SIRIUS, KAITOS, DRAGON, ALALART, MONECOM, RAINCOM, SPRICOM, MOSCOM, LIBCOM | Constellations + formations |
| 13 | 16 | BASIDO SQUAD, AIR SQUAD, FIRE SQUAD, GILAS REGIMENT, MAGMA REGIMENT, ZODOR DIVISION, AMARIES, CORSA, PANDARM, CYTRON, PHARYAD, ROMSARB, WAZARN, GAZEIL, RAZALEO, MEGARL | Enemy armies + bosses |
| 14 | 1 | (space) | Blank |
| 15 | 0 | (empty) | Unused |

Character encoding confirmed: $4F = '-' (hyphen, in R-ARMOR, M-BOOTS, etc.). Digits $01-$03 used in spell level suffixes (BOLTTOR1-3).

**Text Entry Table ($9C3A in bank 2):**

Each entry is 6 bytes, indexed by text_id * 6:
- Bytes 0-1: Pointer to text data (within bank 2 or CHR)
- Bytes 2-3: PPU nametable address (destination for rendering)
- Bytes 4-5: Text parameters (length, flags)

**Text Rendering Flow:**

```
1. Bank 6 mode_dispatch -> mode 7 (dialogue) or mode 8 (cinematic)
2. -> Bank 1 entry 0 ($8044): parse command byte, select mode (0-6 via indexed_jmp)
3.    -> Mode 3: calculate CHR bank from sub-index ($80B3), call $8181 (set CHR mode)
4.    -> Bank 2 entry 1 ($A61C): lookup text by ID in $9C3A table (ID * 6 -> 6-byte header)
5.       Read 6-byte header: data_ptr + PPU_addr + params -> $0528+, ZP $00-$05
6.    -> Bank 2 $A4DB: init position buffer $0550 (16 slots, $FF = end marker)
7.    -> Bank 2 entry 2 ($A91A): init data pointer from $05F0, load position from $A9CA table
7.    -> $A55C: text stream loop (one char per NMI via $A0DB/wait_nmi)
8.       -> $A3D8: per-char decode: read ($00),Y
9.          Tile ID < $80: write to $0163 nametable buffer via $A377
10.         Tile ID >= $80: end-of-word marker (AND #$7F, write char, pad spaces)
11.      -> $A40B: dictionary lookup (ref byte -> $99B7 table -> word data)
12. Bank 7 NMI: $EEEE transfers $0163 buffer to PPU VRAM
```

**Bank 2 $A000-$AFFF Data-Range Map:**

| Range | Size | Description |
|-------|------|-------------|
| $A000-$A0DA | 219B | Nametable layout data (tile/screen templates for text boxes) |
| $A0DB-$A0EF | 21B | `nmi_text_sync` -- NMI sync for text rendering ($04E3 flag check + wait_nmi) |
| $A0F0-$A100 | 17B | PPU control helpers (disable/enable rendering bits in $11/$2001) |
| $A101-$A1BB | 187B | `int_to_bcd_b2` -- 16-bit to BCD conversion (bank 2 copy of bank 1 $8BBC) |
| $A1BC-$A1E2 | 39B | `multiply_16bit` -- 16-bit multiply ($0C:$0D * $0E:$0F -> $0A:$0B) |
| $A1E3-$A376 | 404B | Text helper functions (buffer management, position computation) |
| $A377-$A398 | 34B | `text_write_char` -- write char $06 to $0163 nametable buffer ($0505 = write index, $0502 bit 7 forces space) |
| $A399-$A3D7 | 63B | Position/word boundary computation |
| $A3D8-$A40A | 51B | `text_char_loop` -- per-char decode: read ($00),Y, bit 7 = end-of-word (strip, write, pad spaces), else write + advance |
| $A40B-$A448 | 62B | `dict_lookup` -- dictionary reference: hi4=group index into $99B7, lo4=word (skip N bit7-terminated entries), return pointer to word data |
| $A449-$A4DA | 146B | Dictionary word writer (8 chars max) + helpers |
| $A4DB-$A55B | 129B | `text_position_init` + column/row management ($0550 position buffer, 16 slots) |
| $A55C-$A572 | 23B | `text_stream_loop` -- main render loop: wait NMI per char until $18=0 |
| $A573-$A5CC | 90B | `text_fill_background` -- space-pad nametable rows, render text line, advance |
| $A5CD-$A61B | 79B | Display helpers (scroll, PPU address setup) |
| $A61C-$A919 | 766B | `text_entry_lookup` -- text ID*6 into $9C3A table, read 6-byte header (ptr+PPU addr+params), init rendering state |
| $A91A-$A9C9 | 176B | `text_data_init` -- load state from $05F0, setup position from $A9CA, fill background, init stream |
| $A9CA-$A9DD | 20B | Position data table (4 entries x 4B: PPU addr + dimensions per text box type) |
| $A9DE-$ABFF | 546B | Text processing: line wrapping, scroll handling, text box management |
| $AC00-$AC36 | 55B | `pwd_secret_check` -- CHOCOLA/CORONYA password comparison ($AC08) + table ($AC27) |
| $AC37-$AF06 | 720B | Script VM opcode handlers + helpers (see Script VM section) |
| $AF07-$AFFF | 249B | Zero padding (unused) |

#### Bank 2 Script VM (dialogue / shop / password / events)

The bank 2 "bytecode interpreter" is a general-purpose **script virtual machine** that drives NPC dialogue, shop transactions, the password/continuation screen, and scripted events. The shop logic editors couldn't find is **script bytecode embedded in the CHR-ROM text database** (banks 22-24), interpreted by this VM -- not a flat table. Shop entry: bank 6 `mode3_npc` ($818A) with `$03CC`=shop_flag spawns shopkeeper entity $36; the dialogue/shop script is then run by this VM.

**Main loop ($AA1D `script_vm_loop`):**
```
LDY #0; LDA ($CE),Y    ; fetch opcode (script ptr = $CE/$CF)
ASL A; TAX             ; opcode * 2
LDA $AC9D,X -> $0E/$0F ; handler addr from jump table $AC9D
JSR $ACCC              ; advance $CE past opcode byte
JMP ($000E)            ; dispatch to handler; handler JMPs back to $AA1D
```

**Operand helpers:** `$ACBD` reads X operand bytes from script into scratch `$04D0+` (advancing $CE). `$ACE6` resolves an operand into a target address: high 3 bits index the address-space base table at `$ACF8`, low 5 bits = offset. `$AD08` writes `$04D1` to the resolved address (the conditional write-back).

**Address-space base table ($ACF8, 8 x ptr16):** `$00A0, $0300, $0320, $0080, $0480, $03E0, $0000, $0000`. Index 1 (`$0300`) = game-state / item-count region -- this is how shops read/write CARPET, R.SEED, HORN, HAMMER, RING and other consumables.

**Opcode set (jump table $AC9D, 14 opcodes):**

| Op | Handler | Operands | Function |
|----|---------|----------|----------|
| 0 | $AA35 | ptr16 list | Execute sub-block list: JMP ($0E) for each 16-bit ptr until $0000 (render/sequence) |
| 1 | $AA3F | 1 | **Play sound**: id -> $0526, queue_sound |
| 2 | $AA50 | 1 | **Set CHR bank/mode**: -> $38 via set_chr_mode |
| 3 | $AA5E | 2 | **JUMP** (goto): set $CE/$CF to new script address |
| 4 | $AA6C | 2 | **CALL** sub-block, then continue |
| 5 | $AA78 | 2 | **STORE byte**: write value ($04D1) to resolved game-state address (deliver item / set flag) |
| 6 | $AA91 | 3 | **Render text box**: PPU addr -> $E8/$E9, flags $EA, layout ptr from $AC74 table, trigger VRAM xfer |
| 7 | $AADF | 1 | **Init text rendering** (text_data_init $A91A) |
| 8 | $AAED | 2 | **Load text entry**: text_entry_lookup (mode $0A) -> set $CE/$CF to entry data (switch script to dialogue text) |
| 9 | $AB06 | 7 | **Compare & 3-way branch**: read var at resolved addr, CMP immediate ($04D1); <,=,> each select branch target ($04D3/$04D5) + optional write-back via $AD08. **Shop gold/price/inventory checks + deduct/add** |
| 10 | $AB5B | 2 | **Set text window type** ($0523; type 6->$0524=$33, 7->$0524=$2D) + init |
| 11 | $AB84 | 3 | **Numeric input**: digit buffer $00-$07, reads $C2 button presses to enter a number (**shop "how many to buy" quantity selector**) |
| 12 | $AC7C | -- | Password-screen continuation: save $CE/$CF, load $04D0/$04D1, run pwd secret check (CHOCOLA/CORONYA) |
| 13 | $AC94 | -- | RETURN: restore $CE/$CF from stack (end of CALL) |

**Shop transaction flow (composed from opcodes):** op8 loads item-menu text -> op6 renders shop window -> op11 reads purchase quantity -> op9 checks gold >= price and inventory < max (with write-back to deduct gold / increment item count at $0300+) -> op1 plays purchase jingle -> op5/op9 store the delivered item. Per-shop inventory, prices, and item IDs are encoded as operand bytes in each shop's script.

**Script storage and the bank-1 driver:**

VM scripts are byte-streams of opcodes, stored in **bank 2 PRG `$B800-$BFFF`** (read via $CE/$CF while bank 2 is mapped). The driver that runs them is in **bank 1** (`$810D`): screen type `$82` (0-4) selects a sub-table via master table `$8B32`; sub-index `$04E1` picks the script pointer. Sub-tables at `$9046` (type 0), `$9058` (1), `$9066` (2), `$9078` (3), `$9088` (4) -- 37 scripts total, all pointing into bank 2 `$B800+`. The VM is dispatched as bank 2 jump-table entry 9 (`$8012` -> `$AA08`) via the bank-2 trampoline `$E046`, called from bank 1 `$814C`/`$8211`.

Tools: `dis_script.py <bank> <addr>` disassembles a VM script; `scan_scripts.py` walks all 37 entry points.

**Finding -- these 37 scripts are STORY/CUTSCENE events, not shops:** scanning all 37 shows only SOUND/WINDOW/TEXTINIT/LOADTEXT/IF/STORE/CALL/JUMP opcodes, with IF conditions branching on progress flags `$03E0-$03E4` (chapter/event completion). **No `NUMINPUT` (op11) and no STOREs to item-count addresses ($0306+) appear** -- so the player-facing shop *purchase* transaction is NOT driven by this bank-1 script set. Example (script type 0 entry 0, $B800): `SOUND $5F; WINDOW; BLOCK $BC06; IF [$033E]==1; SOUND $49; STORE [$033E]=1; STORE [$0490]=9; ...` -- a scripted scene, not a store.

The VM and its opcodes (incl. op11 NUMINPUT, op9 with item/gold write-back) are real and drive cutscenes/dialogue/password, but the shop buy-loop is NOT a VM script. **The real shop inventory and pricing are flat tables in bank 1 -- see next section.**

#### Shop Inventory & Pricing (bank 1) -- VERIFIED

The shop system is **not** bytecode and **not** in bank 2. It is a pair of flat tables in **bank 1**, confirmed against the ROM. This definitively corrects both the old "shop tables at file offset $D544" claim (that's the bank 3 inventory max-cap table) and the bank-2 bytecode dead-end.

**Shop-pointer table `$94ED`** -- 8 entries x 2-byte LE pointers, indexed by shop id `$04E1`. Exactly 8 shops. Entries point to `$94FD, $9505, $950D, $9515, $951D, $9525, $952D, $9535` (8 bytes apart).

**Shop data `$94FD+`** -- each shop = **4 slots x 2 bytes** (the "4 items per visit"). Slot format = **`[code, price]`**: byte0 = item/name code, byte1 = price. Read at `$8680` into `$04D5` (code) / `$04D6` (price), slot index from `$04D8`*2.

Decoded shops (price in decimal, chapter-scaled):

| Shop | Ptr | Codes | Prices |
|------|-----|-------|--------|
| 0 | $94FD | 33 34 10 53 | 20 20 40 40 |
| 1 | $9505 | 33 34 52 51 | 20 20 20 100 |
| 2 | $950D | 33 34 52 51 | 60 60 60 100 |
| 3 | $9515 | 52 10 53 11 | 20 40 40 40 |
| 4 | $951D | 33 34 52 58 | 20 20 20 88 |

Shops 0/1 = early-chapter (20s), shop 2 = late-chapter (60s) -- the per-chapter pricing. Shops 5/6/7 mirror 1/2/3 (chapter variants).

**Item code byte structure** (decoded at bank 1 $8A9A / $8A71): the code is `category:index`.
- **Low nibble** (`code & $0F`) = item index into the `$03C0` ownership/count array. `$8A9A`: `LDA $04D5; AND #$0F; ASL; TAY; LDA $03C0,Y` is the "already owned?" check (spells can't be rebought).
- **High nibble** = category: `$1x`/`$3x` = regular consumable item, `$5x` = spell.
- Recurring `$33`(item/3) and `$34`(item/4) are the staple consumables (bread/mashroob; cf. $0306/$0307); `$51`/`$52`/`$53`/`$58` are spells.

**Magic-shop pricing**: instead of the table's byte1, magic shops scale a base price from `$8AAC[code & $0F]` (`20,30,40,20,40,30,20,40,30,40,50`) by chapter via the `$8B89` multiply.

Decoded by `tools/dump_shops.py`. NOTE: the literal item-NAME strings are **not** a flat code-indexed table -- they are baked into each shop's text-entry screen layout. The code byte is the ownership-array index + category, not a name-string pointer.

**Full shop pricing pipeline (all bank 1):**

| Addr | Role |
|------|------|
| `$94ED` | Shop-pointer table (indexed by shop id `$04E1`) |
| `$94FD` | Shop data: 8 shops x 4 slots x `[code, price]` |
| `$8680` | Inventory read -> `$04D5` (code), `$04D6` (price) |
| `$A5A0` | Total = price x quantity (qty table `$A3CB,X`) -> `$04D2` |
| `$A33B` | Haggle / price adjustment (BCD math on gold `$89` + price) |
| `$8A71` | Magic-shop path: chapter-scaled price (`$0540,Y` x chapter via `$8B89`) |
| `$A736` | Animated gold change (carry set = spend) -> `$EBDD` -- the single spend chokepoint |

**Key RAM Addresses (text system):**

| Address | Purpose |
|---------|---------|
| $0163+ | Nametable write buffer (transferred to PPU during NMI by bank 7 $EEEE) |
| $0162 | Nametable buffer write index |
| $0500-$050F | Text state block (flags, counters, current text ID) |
| $0502 | Text flags: bit 0=fast mode, bit 7=force spaces (hide text) |
| $0505 | Current write position in $0163 buffer |
| $0528-$052D | Current text entry header (6 bytes: ptr, PPU addr, params) |
| $0550-$055F | Character position buffer (16 slots, $FF=end) |
| $05F0-$05FF | Saved text state (restored during init) |
| $04E3 | Text display sync flag (bit 7=update pending, bit 6=skip NMI check) |

**Character Encoding:**
- $00-$09: Digits 0-9 (confirmed: spell suffixes BOLTTOR1/2/3 use $01/$02/$03)
- $2C: Space
- $30-$49: A-Z ($30=A, $31=B, ..., $49=Z)
- $4F: Hyphen '-' (confirmed: R-ARMOR, M-BOOTS, M-SHIELD, R-SEED)
- $4A-$4E: Likely punctuation (not found in dictionary data, may appear in dialogue)
- Bit 7 ($80+): End-of-word marker (clear before rendering, pad remaining with spaces)

#### Game State Memory Map ($0300-$03E4)

Game state is stored at $0300+ and encoded into the password system. Mapped by cross-referencing chapter warp data ($BB1F), password commands, item use code, and death/combat handlers.

**Consumable Items:**

| Address | Name | Warp Values | Password | Notes |
|---------|------|-------------|----------|-------|
| $0300 | Gortrat bread counter | 3,4,5,6,7 | $10 (max 9) | "Bread of Gortrat" map event uses remaining. DEC at $8A87 (heals ~20 HP), INC at $8C15 (pickup). NOT the carried Bread item |
| $0301 | Gortrat mashroob counter | 3,4,5,6,7 | $11 (max 9) | MP equivalent of Gortrat bread. NOT the carried Mashroob item |

**Equipment & Armor:**

| Address | Name | Warp Values | Notes |
|---------|------|-------------|-------|
| $0302 | Armor level | 0,0,1,1,2 | 0=none (full dmg), 1=R-ARMOR (half dmg via LSR at $A44D), 2=L-ARMOR (quarter dmg via double LSR at $A456). Password decode hi4=$20 |
| $0303 | M-SHIELD | 0,0,0,1,1 | Defense upgrade, unlocked ch3+. Boolean flag |
| $0304 | M-BOOTS | 0,1,1,1,1 | Movement upgrade, unlocked ch1+. Checked at bank 5 $A8FD in mode 1 |
| $0305 | HOLYROBE | 1,1,1,1,1 | Base defense item, always available. Checked at bank 5 $A3F6 for entity interaction |

**Vital Stats:**

| Address | Name | Warp Values | Password | Notes |
|---------|------|-------------|----------|-------|
| $0306 | **BREAD** | 6,7,8,9,10 | $33 (max 10) | Auto-restore 50 HP on death (bank 7 $F1FA + bank 6 $8AB5). DEC on death, game over if 0. Bought in shops. After RPG battles, summed from party slots ($0515+$051E+$0527) at $91CD |
| $0307 | **MASHROOB** | 6,7,8,9,10 | $34 (max 10) | Auto-restore 50 MP on depletion (bank 6 $8BFB). Bought in shops. After RPG battles, summed from party slots ($0516+$051F+$0528) |
| $030D | Base flag | 1,1,1,1,1 | $58 (max 1) | Always set, initialization marker |
| $030E | Player level | 2,3,4,5,6 | -- | Password decode hi4=$40 updates. Used by entity spawn scaling ($F0F8) |
| $030F | ROD charges | 2,2,3,4,5 | $50 | Rod weapon ammo. Item table index 1 ($99D8). Decremented on use ($9563) |
| $0310 | FLAME charges | 2,2,3,4,5 | $51 (max 5) | Flame weapon ammo. Item table index 2. Decremented on use |
| $0311 | STARDUST charges | 6,7,8,9,10 | $52 (max 15) | Stardust weapon ammo. Item table index 3. Higher capacity |
| $0312 | Max MP/power | 3,3,3,3,3 | $53 | Constant across chapters |
| $0313 | Init flag A | 1,1,1,1,1 | -- | Always set |
| $0314 | Init flag B | 1,1,1,1,1 | -- | Always set |
| $0322 | Magic level | 2,3,4,5,6 | -- | Password decode hi4=$60 updates. Checked by entity spawn system ($F0CF) |

**Spell/Ability Unlock System ($0323-$033F):**

Spell flags are set=1 when learned. Unlocked via XP progression reward table at bank 6 $97EC (24 x 4-byte records: threshold_lo, threshold_hi, reward_data, flag_offset). Flag read via `LDA $0300,Y` where Y comes from lookup tables ($99D8 or $97EF).

The reward data byte (stored at $03ED) encodes: hi4 = display category ($80/$A0/$C0/$E0), lo4 = progression index (1-13). The spell display table at $A886 converts progression index to dictionary group 7 spell index.

**XP -> Spell/Level Progression (bank 6 $97EC, verified against game data):**

XP thresholds are EP-1 (game displays EP, code checks EP-1). The $A886 display table uses an INTERNAL spell ordering that differs from dictionary group 7 order. Some spells UPGRADE previous ones (e.g., BOLTTOR1->BOLTTOR2).

| Lv | EP | XP-1 | Flag | Spell | Weapon | Ch |
|----|-----|------|------|-------|--------|----|
| 1 | 0 | -- | -- | OPRIN (starting spell) | -- | 1 |
| 2 | 20 | 19 | $0329 | PAMPOO | -- | 1 |
| 3 | 80 | 79 | $0323 | BOLTTOR1 | SWORD | 1 |
| 4 | 240 | 239 | $0330 | **DEFENEE** (2 MP, temp defense) | ROD | 1 |
| 5 | 560 | 559 | -- | (stat upgrade) | SWORD | 1 |
| 6 | 640 | 639 | -- | (stat upgrade) | -- | 2 |
| 7 | 780 | 779 | $0326 | FLAMOL1 | ROD | 2 |
| 8 | 980 | 979 | -- | (stat upgrade) | SWORD | 2 |
| 9 | 1280 | 1279 | $032D | CORBOCK | SWORD/ROD | 2 |
| 10 | 1800 | 1799 | -- | (stat upgrade) | -- | 2 |
| 11 | 2000 | 1999 | $0324 | BOLTTOR1->BOLTTOR2 | ROD | 3 |
| 12 | 2400 | 2399 | -- | (stat upgrade) | SWORD | 3 |
| 13 | 3000 | 2999 | $032E | CORBOCK->SHRINK | SWORD/ROD | 3 |
| 14 | 3800 | 3799 | $0327 | FLAMOL1->FLAMOL2 | SWORD | 3 |
| 15 | 4800 | 4799 | $0331 | **RAMIPAS** (10 MP, no encounters) | ROD | 3 |
| 16 | 5200 | 5199 | -- | (stat upgrade) | -- | 4 |
| 17 | 6000 | 5999 | $0325 | BOLTTOR2->BOLTTOR3 | SWORD/ROD | 4 |
| 18 | 7200 | 7199 | -- | (stat upgrade) | -- | 4 |
| 19 | 8800 | 8799 | -- | (stat upgrade) | SWORD/ROD | 4 |
| 20 | 10800 | 10799 | $032F | SHRINK->CARABA | SWORD | 4 |
| 21 | 11300 | 11299 | $032A | MARITA | SWORD/ROD | 5 |
| 22 | 12550 | 12549 | -- | (stat upgrade) | SWORD | 5 |
| 23 | 14550 | 14549 | $0328 | FLAMOL2->FLAMOL3 | SWORD/ROD | 5 |
| 24 | 17300 | 17299 | -- | (stat upgrade) | -- | 5 |
| 25 | 20800 | 20799 | -- | (stat upgrade, max level) | -- | 5 |

HP/MP values match the $8C10 stat table (30 entries). Stat upgrade entries (no flag) have reward byte hi4=$80/$C0 = HP/weapon increase.

Non-spell XP rewards (flag=$00, no unlock): entries at XP 559, 639, 1799, 5199, 7199, 8799, 12549, 17299 -- these are stat/HP upgrades (reward byte hi4=$80/$C0/$E0 with no flag offset).

**Equipment/Combat Flags ($0332-$033F):**

$0332/$0333 = equipped sword slot (dynamic, written by sword pickup handler $8E3D). $0336-$033F = permanent progression gates (set ONLY by chapter warp data, never by item code).

| Address | Ch0 | Ch1 | Ch2 | Ch3 | Ch4 | Purpose |
|---------|-----|-----|-----|-----|-----|---------|
| $0332 | -- | -- | -- | -- | -- | **Equipped sword ID** (dynamic; items 9-14 write here via $8E3D/$8E47) |
| $0336 | 0 | 1 | 1 | 1 | 1 | **Sword gate** (enables attack; bank 5 $8854 + bank 4 $86B5). Set at ch1 when first sword obtained |
| $0337 | 0 | 1 | 1 | 1 | 1 | **Rod gate** (enables rod weapons). Set at ch1 |
| $0338 | 0 | 0 | 1 | 1 | 1 | **Magic gate** (enables spells in mode 2; bank 5 $8867 + bank 4 $86C5). Set at ch2 |
| $0339 | 0 | 0 | 0 | 1 | 1 | **Advanced magic gate**. Set at ch3 |
| $033A | 0 | 0 | 1 | 1 | 1 | **Formation gate** (enables RPG formations). Set at ch2 |
| $033B | 0 | 1 | 1 | 1 | 1 | **Party gate** (enables party commands). Set at ch1 |
| $033C | 0 | 0 | 0 | 1 | 1 | **Advanced formation gate**. Set at ch3 |
| $033D | 1 | 1 | 1 | 1 | 1 | **Base melee** (always available) |
| $033E | 1 | 1 | 1 | 1 | 1 | **Base defense** (always available) |
| $033F | 0 | 0 | 0 | 0 | 1 | **Ultimate ability gate**. Set at ch4 only |

**Currency & Chapter:**

| Address | Name | Warp Values | Notes |
|---------|------|-------------|-------|
| $03D6 | Chapter (BCD) | 1,2,3,4,5 | Current chapter number |
| $03D7 | Max chapter | 5,5,5,5,5 | Constant (total chapters) |
| $03D9 | Gold digit 1 | -- | BCD hundreds digit (0-9). Used by password BCD add at $8849 |
| $03DA | Gold digit 2 | -- | BCD tens digit |
| $03DB | Gold digit 3 | -- | BCD ones digit |

**Late-Game Event Flags ($03E0-$03E4):**

Accessed via $99D8 item lookup table indices 24-28. These are EVENT TRIGGERS, not inventory items -- they track whether specific game events have been activated for the current chapter. Set by warp data and quest progression ($97CD).

| Address | Ch0 | Ch1 | Ch2 | Ch3 | Ch4 | Item | Effect |
|---------|-----|-----|-----|-----|-----|------|--------|
| $03E0 | 0 | 0 | 0 | 0 | 1 | 24 | Battle event trigger (RPG battle via $DE93) |
| $03E1 | 1 | 1 | 1 | 1 | 1 | 25 | Full resource restore (max all ammo/lives/items, zero gold) |
| $03E2 | 0 | 0 | 0 | 1 | 1 | 26 | Screen transition event ($E019) |
| $03E3 | 0 | 1 | 1 | 1 | 1 | 27 | Ceremony/blessing cutscene (sound $1E + $4F jingle) |
| $03E4 | 0 | 0 | 1 | 1 | 1 | 28 | Magic visual effect (palette cycling) |

**Item Data Table (bank 6 $98E8, 30 entries x 8 bytes):**

Each item has an 8-byte record accessed as $98E8 + item_ID * 8. Lookup function at $950F converts item ID to Y offset. The $99D8 table maps 8 active item indices to $0300+ addresses (1-3 -> $030F-$0311 rod ammo; 24-28 -> $03E0-$03E4 special items).

Record format: byte 0 = item ID, byte 1 = pickup sound ($74=common, $69/$6A/$70=variants), byte 2 = flags (bit 4=HP cost, bit 6=skip display, bit 7=skip, $FE=one-time), bytes 3-4 = handler pointer (LE), byte 5 = unused (0), bytes 6-7 = sub-type/parameter.

**Complete Item ID Map (30 items):**

| ID | Name | Dict | Sound | Flags | Handler | Count Addr | Notes |
|----|------|------|-------|-------|---------|------------|-------|
| 0 | (null) | -- | $00 | $26 | -- | -- | Empty/placeholder |
| 1 | ROD | G4:1 | $74 | $3E | $8CA9 | $030F | Consumable weapon ammo |
| 2 | FLAME | G4:2 | $1A | $3E | $8CCF | $0310 | Consumable weapon ammo |
| 3 | STARDUST | G4:3 | $00 | $FE | $8CFE | $0311 | One-time activate |
| 4 | CIMARON | G4:4 | $00 | $FE | -- | -- | One-time quest pickup |
| 5 | CRYSTAL | G4:5 | $00 | $EE | $9106 | -- | Active item (param=5) |
| 6 | ISFA | G4:6 | $00 | $C6 | $8D8E | -- | Active item |
| 7 | KEY | G1:0 | $00 | $FE | -- | -- | One-time quest key |
| 8 | AMULET | G1:1 | $00 | $FE | -- | -- | One-time quest key |
| 9 | SWORD | G6:1 | $74 | $E6 | $8E3D | $0332 | Equip: sword tier 0 |
| 10 | SIMITAR | G6:2 | $74 | $E6 | $8E3D | $0332 | Equip: sword tier 1 |
| 11 | DRAGOON | G6:3 | $74 | $E6 | $8E3D | $0332 | Equip: sword tier 2 |
| 12 | KASHIM | G6:4 | $74 | $06 | $8ECE | $0332 | Equip: named sword |
| 13 | ROSTAM | G6:5 | $74 | $06 | $8ECE | $0332 | Equip: named sword |
| 14 | LEGEND | G6:6 | $74 | $06 | $8ECE | $0332 | Equip: named sword (best) |
| 15 | HAMMER | G5:0 | $6A | $26 | $8F4F | -- | Quest item |
| 16 | R-SEED | G5:1 | $6A | $26 | $8F4F | -- | Quest item (Rupia seed) |
| 17 | CARPET | G5:2 | $00 | $06 | -- | -- | Passive equip |
| 18 | HORN | G5:3 | $00 | $FE | -- | -- | One-time quest item |
| 19 | OPRIN | G5:4 | $69 | $06 | $8F73 | -- | Quest item |
| 20 | RING | G5:5 | $69 | $06 | $8F73 | -- | Quest item |
| 21 | (blank) | G5:6 | $69 | $06 | $8F73 | -- | Quest variant |
| 22 | MAP | G5:8 | $6A | $26 | $8F7B | -- | Quest item |
| 23 | Mode change | -- | $70 | $26 | $9654 | -- | Sets $72=5 (area/mode flag) |
| 24 | Battle event | -- | $00 | $0E | $9659 | $03E0 | Triggers RPG battle via $DE93. Ch4-only |
| 25 | Full restore | -- | $39 | $0E | $966A | $03E1 | Max all resources (ROD=5, FLAME=5, STARDUST=15, Lives=10, Magic=10, Bread=9, Mashroob=9), zeros gold, triggers battle event |
| 26 | Screen event | -- | $00 | $0E | $96AE | $03E2 | Screen transition via $E019. Ch3+ |
| 27 | Ceremony | -- | $00 | $6E | $96B9 | $03E3 | Cutscene: sound $1E + jingle $4F, animation wait loop. Blessing/ceremony. Ch1+ |
| 28 | Magic effect | -- | $00 | $6E | $9725 | $03E4 | Palette cycle effect (3-entry table at $977B on $04A4). Visual magic. Ch2+ |
| 29 | Entity action | -- | $00 | $F6 | $91DC | -- | NPC/entity interaction: reads $0319 slot, branches by entity type bit 0 |

Items display their name via CHR tile graphics (loaded from CHR bank 23 via $9140), not through the dictionary text system. The CHR page lookup at $9163 maps item categories to tile offsets.

**Key ZP State (set by warp):** $81 = current HP, $84 = screen position (4,9,14,19,24 per chapter), $87 = world/overworld flags, $89-$8B = chapter name/number, $91 = max HP.

#### Password System (Bank 1 $86EA-$94FF)

The game uses a password-based continue system (no battery save). The password encodes game state as BCD digits displayed as grid symbols.

**Password UI Flow (in CHR bank 24 dialogue data):**
1. Title screen -> "CONTINUE" -> "ENTER THE PASSWORD" grid input screen
2. Game over -> password displayed for the player to record
3. "ENTER YOUR NAME" follows successful password decode

**Key Memory Areas:**
- $04D1-$04D5: Password character buffer (input symbols)
- $0570-$057F: Decoded game state buffer (16 bytes)
- $89-$8B: 3-digit BCD accumulator (checksum/running total)
- $09-$0B: 3-digit BCD comparison value
- $0300+: Game state variables (chapter, items, stats)

**Password Encoding Flow ($8250 -> $8680 -> $8746):**

The password generation pipeline converts game state into a 7-character checksum-encoded string:

1. **Template load** ($93A6): Copy 16-byte base template from $93D0 to $0570 buffer. For chapter continues, the alternative path at $93B3 copies 4-byte chapter data from $9430 (index = (password_char AND $0F - 6) * 4).

2. **Command processing loop** ($8680): Reads 2-byte commands from ($04D1) pointer list, indexed by $04D8:
   - $04D5: command type (hi4) + index (lo4)
   - $04D6: value/multiplier
   - Calls checksum ($86EA), then pwd_encode_state ($8746) or display path

3. **State encode** ($8746): Based on command type hi4:
   - $10: Read `$0300+lo4`, increment (max 9). Special: indices 6/7 add $049B instead
   - $30: Read `$0303+lo4`, increment (max 10)
   - $50: Special stat addresses at `$030F+lo4` with per-index limits ($0F, $05, or table at $87F2)
   Each step does BCD subtract on the 3-digit accumulator, then NMI-synced display update

4. **Checksum** ($86EA): `value * position_weight ($049B)` -> 16-bit multiply -> BCD convert. Verifies high 2 digits are 0 (value fits in 3 BCD digits). Compares result against accumulator $89:$8A:$8B.

5. **Character output** ($82CC): For each position, computes grid symbol as `10 - $02D3[X]`. Position weight ($049B) multiplied by $04D6 determines encoding scale. Display via $8304 (write to $0163 nametable buffer) + $8AC4 (NMI sync).

**Password Structure (8 groups, 32 command positions):**

The password is organized as 8 display groups (indexed by $04E1), each with 4 command pairs from the $94ED pointer table. Display layout entries at $94FD-$953C define the screen position and command type for each symbol:

| Group | Ptr | Commands (type+index, weight) |
|-------|-----|------|
| 0 | $94FD | ($33,$14), ($34,$14), ($10,$28), ($53,$28) |
| 1 | $9505 | ($33,$14), ($34,$14), ($52,$14), ($51,$64) |
| 2 | $950D | ($33,$3C), ($34,$3C), ($52,$3C), ($51,$64) |
| 3 | $9515 | ($52,$14), ($10,$28), ($53,$28), ($11,$28) |
| 4 | $951D | ($33,$14), ($34,$14), ($52,$14), ($58,$28) |
| 5 | $9525 | ($33,$14), ($34,$14), ($52,$14), ($51,$64) |
| 6 | $952D | ($33,$3C), ($34,$3C), ($52,$3C), ($51,$64) |
| 7 | $9535 | ($52,$14), ($10,$28), ($53,$28), ($11,$28) |

Command types (hi4 of first byte): $10=base stat ($0300+), $30=extended stat ($0303+), $50=special address ($030F+). Second byte = display weight. Within each group, the inner loop at $87FA processes 2-3 iterations per row (limits at $8813: 2, 3, 2 indexed by $92).

Unique position indices: $10, $11, $33, $34, $51, $52, $53, $58 -- 8 distinct grid positions, each encoded across multiple groups to produce the full symbol-grid password. The $86EA checksum (BCD multiply by $049B weight) ensures password integrity across all positions.

**Password Decoding ($947B):**

Each byte in $0570 buffer encodes a command + value:
- High nibble $40: Update $030E (max level) if value > current
- High nibble $60: Update $0322 (stat) if value > current
- High nibble $20: Unlock feature ($0302)
- High nibble $C0/$D0: Extended game state commands
- Other: End of data

**Core Math Functions:**
- $8B89: 16-bit multiply: A * Y -> $0A:$0B (shift-and-add algorithm, $0C:$0D * $0E:$0F)
- $8BBC: 16-bit to BCD: $0C:$0D -> 5 digits at $07-$0B (subtract 10000/1000/100/10 loops)
- $870F: BCD subtract: $89:$8A:$8B -= $09:$0A:$0B (mod 10 per digit, underflow clamps to 000)
- $872B: BCD add: $89:$8A:$8B += $09:$0A:$0B (mod 10 per digit, overflow clamps to 999)
- $86EA: Checksum: multiply by $049B weight, convert to BCD, compare 3-digit accumulator
- $8819: Display update: set $04E3 bit 7, call $8AC4 twice (NMI sync with nametable write)

**Password Data Templates ($93D0+):**

Base template (16 bytes): `$00 $D0 $D6 $D7 $C0 $C1 $C2 $C3 $C0 $00 $1E $00 $1A $00 $00 $00`

Each byte is a game state command: hi4=type ($C0=stat, $D0=extended, $1x/$0x=value), lo4=index. The template defines the default decode sequence for the $0570 buffer.

Chapter-specific data at $9430 (4 bytes per chapter, overrides first 4 bytes of $0570):

| Chapter | Bytes | Meaning |
|---------|-------|---------|
| 0 (1W) | $62 $01 $0A $00 | Stat#2=1, level $0A, base |
| 1 (2W) | $42 $02 $0B $0C | Level#2=2, max $0B, stat $0C |
| 2 (3W) | $43 $02 $0E $0C | Level#3=2, max $0E, stat $0C |
| 3 (4W) | $20 $02 $0F $0C | Unlock feature, max $0F, stat $0C |
| 4 (5W) | $45 $02 $10 $0C | Level#5=2, max $10, stat $0C |

**Password Display Data ($94FD+):**
Grid position/tile data for the password entry screen. Entries contain screen coordinates and tile indices for the selectable symbol grid.

#### Unified Bank Dispatch Architecture

Bank 7 contains dispatch entry points for ALL 7 switchable banks at regular intervals. Each loads the bank number and jumps to the common dispatch at $E11E, which switches PRG, reads a function pointer from the target bank's jump table at $8000+($3A*2), and calls it:

**Complete INC sled layout ($E011-$E11A):**

| Sled Range | Dispatch | Bank | Entries | Notes |
|------------|----------|------|---------|-------|
| $E011-$E03D | $E03F | 1 | 23 | Text/UI engine |
| $E046-$E056 | $E058 | 2 | 9 | Music + text decode |
| $E05F-$E06B | $E06D | 3 | 7 | RPG battle engine |
| $E074-$E0A3 | $E0A4 | 4 | 24 | Screen/tile/entity data |
| $E0AB-$E0D3 | $E0D5 | 5 | 21 | Entity behavior |
| $E0DC-$E118 | $E11A | 6 | 31 | Game logic |

Each INC $3A instruction is 2 bytes. Entering at address A gives $3A = (dispatch_addr - A) / 2 increments. The dispatch at $E11E reads bank jump table at $8000 + ($3A * 2).

**Common dispatch ($E11E):** Save current bank, switch PRG to target bank, ASL $3A (word offset), read ptr from $8000+$3A, zero $3A, JSR through pointer, restore bank.

#### CHR Bank Helpers

- `$EF73` (sub_EF73): Sets CHR0=A, CHR1=A+1 (consecutive 4KB banks)
- `$E495` (in NMI): Uses $38 index into $ED43 table for per-mode CHR selection
- `$E87D` (init_mmc1): Sets initial CHR0=$00

#### CHR ROM as Data Storage ($EF7E)

The game uses CHR ROM for **both tile graphics and data storage**. The VRAM read system at $EF7E has two paths controlled by $EA bit 5:

**CHR data path** (bit 5 set):
1. Calculate 4KB CHR bank from $E9/$EA: `($E9 >> 4) & 3 + $EA`, then `& $1F` = bank 0-31
2. Call $EF73 to set CHR0/CHR1 to consecutive banks
3. Read data from PPU via $2006/$2007 into CPU RAM

**PRG data path** (bit 5 clear):
1. Bank = `$EA & 7` (PRG bank 0-7)
2. Call mmc1_write_prg to switch PRG bank
3. Read data from CPU address space ($8000-$BFFF)

This explains why CHR 4KB banks 21-31 contain high-entropy non-tile data. All 32 4KB CHR banks can be addressed for data reads.

#### CHR Data Bank Contents (4KB banks 21-31)

| 4KB Bank | File Offset | Content Type | Details |
|----------|-------------|--------------|---------|
| 21 | 0x35010 | Screen pointer table | 4-byte entries: 16-bit LE pointer + 2 param bytes. Points into other CHR data banks. |
| 22 | 0x36010 | NPC dialogue text | Token-compressed text. $FA=newline, $FE=message separator, $7F=end, $80-$FF=dictionary tokens. Money lender, mosque, class change dialogues. |
| 23 | 0x37010 | Mixed: pointers + text | First 32 bytes are 16-bit pointers, then dialogue text. Spell names ("ABCABRA!"), hint text. |
| 24 | 0x38010 | NPC dialogue text | More dialogue: "WORLD", "REMEMBER THE MESSAGE", "TAKE A ROD", "SHOOT ME", chapter/quest hints. |
| 25 | 0x39010 | Nametable commands | PPU address + tile data packets for screen layouts (HUD, menus, status). Addresses in $20xx-$23xx range. |
| 26-27 | 0x3A010 | Level/entity data | Structured records with parameters. Entity placement, level config. |
| 28 | 0x3C010 | Level/entity data | Similar structured format to 26-27. |
| 29 | 0x3D010 | Tilemap data | Raw tile indices ($03, $0F, $16, etc.) for background rendering. Overworld/dungeon map tiles. |
| 30 | 0x3E010 | Tilemap data | Tile indices with heavy repetition ($23=blank, $41, $43). Screen/area maps. |
| 31 | 0x3F010 | Tilemap data | Tile indices ($54, $5F, $53). More area map data. |

#### Text Token Compression ($80-$FF in dialogue)

Bytes $80-$FF in dialogue text are dictionary tokens, not literal characters:

| Token | Meaning | Evidence |
|-------|---------|---------|
| $D2 | "YOU" | "DO [D2] NEED?" "CAN [D2] REPAY" "[D2]R LOAN" = "YOUR LOAN" |
| $C4 | "THE" | "BEFORE [C4] INTEREST" = "BEFORE THE INTEREST" |
| $A3 | "ING" | "ANYTH[A3]" = "ANYTHING", "BR[A3]S" = "BRINGS" |
| $9E | "I'M" / "WE'RE" | "[9E] SORRY" = "I'M SORRY" |
| $AD | "MAN" | "HOW [AD]Y" = "HOW MANY" |
| $8F | (TBD) | In "[D2] [8F] HAVE" |
| $90 | "ENOUGH"? | In "HAVE [90] MONEY" |
| $FA | newline | Line break within message |
| $FE | msg separator | Separates messages in a sequence |
| $7F | end passage | End of text block |
| $2F | section end | Message/section delimiter |

The token dictionary table location is TBD -- likely referenced by the text engine at $E0CD.

#### $E97D Indexed Dispatch (Two-Level)

Used for sub-dispatching within a bank: reads A as table index, pulls return address from stack, indexes into inline address table following the JSR, and JMPs through ($3E). Used at $8041 (entry 0 of bank 6 table) with $19 as the mode selector.

#### Key Zero Page Variables

| Addr | Name | Notes |
|------|------|-------|
| $10 | ppu_ctrl_shadow | Mirror of $2000; NMI merges nametable bits from $13/$15 |
| $11 | ppu_mask_val | Written to $2001 during NMI; init=$06 (show bg+sprites) |
| $12 | scroll_x | Fine X scroll, written to $2005 in NMI |
| $13 | scroll_x_nt | X nametable select (bit 0 -> $2000 bit 0) |
| $14 | scroll_y | Fine Y scroll, written to $2005 in NMI |
| $15 | scroll_y_nt | Y nametable select (bit 0 -> $2000 bit 1) |
| $16-$17 | scroll_limits | Set to $14 during init |
| $18 | game_mode | Mode/state flag; negative=special, checked in main loop |
| $19 | level_transition | Negative = exit loop, $FF = restart to $E243 |
| $1C | nmi_flags | Bit 7=NMI occurred, 0=skip OAM, 2=palette update, 3=VRAM read, 4=? |
| $1D | warm_start | Nonzero = skip RAM clear on restart |
| $1E-$1F | frame_counter | 16-bit frame counter, incremented every NMI |
| $20-$2F | timers | Decremented by NMI (every 8 or 16 frames depending on index) |
| $30-$35 | game_vars | Cleared per-level by $E2C6 |
| $36-$37 | pointer | Set to $28E0 during sprite init |
| $38 | chr_bank_index | Index into CHR bank table at $ED43 |
| $39 | current_prg_bank | PRG bank saved/restored during NMI bank 0 trampoline |
| $57 | sound_enable | Nonzero = call sound engine ($CFE0) in NMI |
| $60 | sub_state | Game sub-state |
| $67 | flags_67 | Bit 7 cleared every NMI |
| $72 | cleared | Cleared during init |
| $80 | game_state | Main state machine variable, 0=idle/transition |
| $88-$8B | state_counters | Various state counters |
| $93, $95 | cleared | Cleared in clear_game_state |
| $AD | vram_update_ctrl | Bit 7 = VRAM update pending (cleared after use) |
| $AE-$AF | vram_ptr | VRAM source pointer for $EEEE PPU update |
| $C0 | joy_current | Current controller state (8 buttons) |
| $C1 | joy_previous | Previous frame controller state |
| $C2 | joy_pressed | New button presses (rising edges) |
| $C4-$C6 | cleared | Cleared during init |
| $D0-$D3 | joy_temp | Controller read temporaries |
| $E0 | input_flags | Init=$A5; bits rotated during NMI input processing |
| $E7 | prev_input | Previous $E0 value for edge detection |
| $E8-$E9 | vram_dest_ptr | VRAM-to-RAM copy destination pointer |
| $EA | vram_read_count | Bytes remaining in VRAM read operation |
| $EB-$EC | vram_src_addr | PPU VRAM source address for reads |
| $ED | vram_src_hi_adj | High byte adjustment for VRAM reads |

### Text Encoding System

#### Character Map (CHR bank 0, pattern table 0)

| Tile Index | Character | Notes |
|------------|-----------|-------|
| $00-$09 | '0'-'9' | Digits |
| $28 | '>' | Right arrow |
| $29 | ' ' | Blank tile (alternate space) |
| $2C | ' ' | Space (primary, used between words) |
| $30-$49 | 'A'-'Z' | Uppercase letters ($30=A, $31=B, ..., $49=Z) |
| $4C | left quote | |
| $4D | right quote | Apostrophe |
| $4E | ':' | Colon |
| $4F | '.' | Period |
| $7B | '-' | Dash |
| $7C | '?' | Question mark |
| $7D | '!' | Exclamation |
| $7E | '...' | Ellipsis |

#### Text Format

- **Dictionary mode**: Bit 7 ($80) on the last byte of each word marks end-of-token
- **Dialogue text** (bank 1): Mixes raw tile indices with control codes ($80+) for formatting, line breaks, dictionary references
- **Control codes**: $8C, $8D, $8F, $9A, $A3, $A4, $A7 etc. appear to be text engine commands (positioning, newlines, pauses)

#### Dictionary Tables

**Bank 6 $A130** (game items/terms):
DRAGOON, KASHIM, ROSTAM, LEGEND, SPEAK, CARPET, R.SEED, HAMMER, HORN, RING, FIGHTER, SAINT, MAGICIAN, MAGIC, ITEM, THE, MAXIMUM, HAS BECOME, OFFENSE POWER OF THE, HAS INCREASED, LEVEL

**Bank 2 $9B44** (characters/enemies/units):
FARUK, HASSAN, FIGHTER, SAINT, MAGICIAN, CYGNUS, LIBRA, ARIES, SIRIUS, KAITOS, DRAGON, ALALART, MONECOM, RAINCOM, SPRICOM, MOSCOM, LIBCOM, BASIDO SQUAD, AIR SQUAD, FIRE SQUAD, GILAS REGIMENT, MAGMA REGIMENT, ZODOR DIVISION, AMARIES, CORSA, PANDARM, CYTRON, PHARYAD, ROMSARB, WAZARN, GAZEIL, RAZALEO, MEGARL

**Bank 4 $BD34** (119 entries -- NPC names + common words + game terms):
CORONYA, SUPICA, GUN MECA, PUKIN, GUBIBI, MUSTAFA, EPIN, RAINY, KEBABU, FARUK, HASSAN, AND, ARE, AIROSCHE, APPEARED, BE, BUT, BEEN, CAN, CURLY, CIMARON, COUNTRY, COME, COLOR, DESERT, DID, DO, DEFEAT, DEMON, DAMAGE, ESCAPE, FLY, FOR, FORM, FOREST, FROM, FIRE, FRUIT, GO, GREAT, GILGA, GORAGORA, HERO, HERE, HAVE, HAS, HIM, ISFA, IS, IT, ING, IF, IN, KNOW, LIKE, LAKE, MAGIC, MEET, MOV, NO, OF, OUT, ONLY, PALACE, PLACE, POWER, SABARON, SOON, SOME, SCHEHERAZADE, SIDE, SALAMANDER, STONE, THE, THAT, TOWN, THERE, THIS, TO, TRANSLATION:, TIME, TAKEN, TER, TROLL, USE, WITH, WELCOME, WILL, WAIT, WHAT, YOUR, YOU, ZAINAB, 'S, BIG, BY, CAME, CURSE, DODGED, FROZE, GAVE, GOT, HAD, ON, H.P, RECOVERED, RUPIAS, M.P, WAS, WERE, WORK, PASSWORD, PLEASE, WRONG, STILL, CHECK, ENTER, AGAIN, LET

Format: bit-7-terminated tile indices ($30-$49 = A-Z, $2C = space). Pointer table at $8040 (28 entries: 7 code ptrs + 21 string ptrs). All 119 strings are contiguous $BD34-$BF52.

**Bank 1**: Contains formatted dialogue text with control codes (e.g., "MANY FEARFUL ENEMIES", "HEY! LET'S...")

### Data Structures

#### WorldScreen (16 bytes, 739 total across 5 chapters)

ROM location: CHR 4KB bank 25+ (file offset $039695). Read via PPU data read mechanism ($EF7E).
RAM mirror: $00B0-$00BF (copied when screen loads).

| Offset | ZP | Name | Bits | Description | Verified |
|--------|-----|------|------|-------------|----------|
| 0 | $B0 | ParentWorld | 8 | Music/section ID ($20=town, $40=overworld) | Bank 4 reads at 4+ sites |
| 1 | $B1 | AmbientSound | 8 | Ambient sound effect ID | Bank 4 loads/stores at $81C0-$81CB |
| 2 | $B2 | Content | 8 | Building type (shop, mosque, battle, boss) | Most referenced field (6+ bank 4 sites) |
| 3 | $B3 | ObjectSet | 8 | Enemy spawn config and doors | Bank 4 LDY/INC at $866C/$8909 |
| 4 | $B4 | ScreenIndexRight | 8 | Screen index walking right ($FF=blocked, $FE=building) | Navigation group loaded at bank 4 $9693 |
| 5 | $B5 | ScreenIndexLeft | 8 | Screen index walking left | |
| 6 | $B6 | ScreenIndexDown | 8 | Screen index walking down | |
| 7 | $B7 | ScreenIndexUp | 8 | Screen index walking up | |
| 8 | $B8 | DataPointer | 7:6=bank sel, 5:0=CHR | Tile bank + CHR bank selection | Bank 2: 15+ bit ops at $B806-$B8AF |
| 9 | $B9 | ExitPosition | 8 | Player spawn position when entering | Bank 4 reads at $986C, $A1A1, $A26B |
| 10 | $BA | TopTiles | 8 | TileSection index for top 4 rows | Bank 4 reads at $8441 |
| 11 | $BB | BottomTiles | 8 | TileSection index for bottom 2 rows | Bank 4 reads at $844A |
| 12 | $BC | WorldScreenColor | 8 | Background color palette | Bank 4 reads at $8362 |
| 13 | $BD | SpritesColor | 8 | Sprite color palette ($12=town) | Bank 4 reads at $836D |
| 14 | $BE | EntityFlags | 7=spawn mod, 6=entity mod, 5:4=spawn cfg, 3:0=type(0-3) | Entity/spawn behavior bitfield | Bank 5 reads 7x, BIT 2x |
| 15 | $BF | Event | 6=content-FF flag, 4:3=event type, 7=secondary | Dialog/event trigger bitfield | Bank 4 BIT/AND at $8110-$8310 |

**EntityFlags ($BE) bit layout:**

| Bits | Mask | Usage | Evidence |
|------|------|-------|----------|
| 7 | $80 | Spawn behavior modifier | BPL/BIT tests in bank 5 $8F30/$9D22; changes Y param 2 vs 3 |
| 6 | $40 | Entity behavior modifier | BIT/BVS in bank 5 $8F38 |
| 5:4 | $30 | Spawn configuration | Extracted to $0334, then cleared (AND #$CF) during setup |
| 3:0 | $0F | Entity type selector | Bank 4 $83F8: AND #$0F; CMP #$04; values 0-3 used, 4+ clamped |

**Chapter data locations (file offsets):**

| Chapter | Start | Screens | End |
|---------|-------|---------|-----|
| 1 | $039695 | 131 | $039EC4 |
| 2 | $039EC5 | 137 | $03A754 |
| 3 | $03A755 | 153 | $03B0E4 |
| 4 | $03B0E5 | 164 | $03BB24 |
| 5 | $03BB25 | 154 | $03C4C6 |

Navigation is graph-based (not grid): screen pointers are one-directional, enabling mazes and non-euclidean layouts.

#### Tile Rendering Pipeline (code-verified)

**DataPointer ($B8) bit layout** -- verified at bank 4 $8432-$8449:

```
DataPointer: [7][6][5][4][3][2][1][0]
              |  |  |______________|
              |  |         |
              |  |         +-- Bits 0-5: CHR bank index -> $38 (via AND #$3F at $8434)
              |  +-- Bit 6: Bottom tiles bank select (ASL x2 at $8448-$8449, carry -> ROL $EC)
              +-- Bit 7: Top tiles bank select (ASL x1 at $8440, carry -> ROL $EC)
```

Bank select: 0 = Bank 0 (base), 1 = Bank 1 (base + $2000)

**TileSection ROM layout:**

| Property | Value | Code Evidence |
|----------|-------|---------------|
| Bank 0 base | file $03C4C7 | Computed from $A8/$A9 via $EE93 NMI read |
| Bank 1 base | file $03E4C7 | Bank 0 + $2000 (bit set via ROL $EC at $8451) |
| **Stride** | **32 bytes** | 5x ASL at $8453-$845F = tile_index << 5 = * 32 |
| Section size | 32 bytes | 8 tiles x 4 rows |
| Bytes per tile | 1 | Direct NES tile index (NOT a meta-tile ID) |

**Address formula (code-verified):**
```
file_offset = 0x03C4C7 + (tile_index * 32) + (bank_bit ? 0x2000 : 0)
```

**Verified example** -- Screen 0 (Chapter 1 start):
- DataPointer = $D1 (bit7=1, bit6=1, CHR=$11)
- TopTiles = $0D -> $03C4C7 + $2000 + $0D*32 = $03E667
- BottomTiles = $11 -> $03C4C7 + $2000 + $11*32 = $03E6E7
- Both produce exact tile matches against known screen layout

**Screen composition** (8 tiles wide x 6 tiles tall):
- Rows 0-3: TopTiles section (all 4 rows rendered)
- Rows 4-5: BottomTiles section (only rows 0-1 rendered, rows 2-3 ignored)

**CHR bank selection** -- bits 0-5 of DataPointer stored to $38, used by NMI at $E48E:
```asm
LDA $38        ; CHR bank index (from DataPointer bits 0-5)
ASL A          ; * 2 for table index
TAY
LDA $ED43,Y   ; CHR bank 0 value
JSR $E56E      ; -> mmc1_write_chr0
LDA $ED44,Y   ; CHR bank 1 value
JSR $E582      ; -> mmc1_write_chr1
```

**CHR bank address calculation** (bank 4 $846C-$8479):
After computing the 16-bit section address in $EC:$EB:
```asm
LSR A          ; $EC >> 4 = which 4KB CHR bank
LSR A
LSR A
LSR A
ADC #$17       ; + 23 = absolute 4KB bank number
STA $ED        ; CHR bank for PPU read
AND #$0F       ; keep offset within bank
STA $EC        ; address high byte within bank
```
Data is then read from CHR ROM via PPU $2006/$2007 using the VRAM read system at $E8D1.

**Dual representation in CHR ROM:**

There are TWO tile data tables sharing the same base address but in different CHR banks:

| CHR Region | Base | Stride | Content | Purpose |
|------------|------|--------|---------|---------|
| Bank 0 area | $03C4C7 | **8 (overlapping)** | Tile IDs (small: $01, $03, $14...) | Compressed TileSection data |
| Bank 1 area | $03E4C7 | **32** | NES tile indices ($47, $86, $D0...) | Pre-expanded nametable data |

The game code at bank 4 $8432 reads from the pre-expanded (stride=32) representation via DataPointer bank bits. The compressed (stride=8) representation uses a 3-level lookup chain:

1. **TileSection** (stride=8, overlapping): 8x4 grid of Tile IDs
2. **Tile table** at $011B0B (bank 4 $9AFB): 4 bytes per entry -> 2x2 MiniTile IDs
3. **MiniTile table** at $01160B (bank 4 $95FB): 4 bytes per entry -> 2x2 CHR tile indices

Each game "tile" = 2x2 MiniTiles = 4x4 CHR tiles = 32x32 pixels.
Screen = 8 game tiles wide (256px) x 6 tall (192px, HUD fills remaining 32px to 224px total).

The compressed representation allows 940 TileSections in ~7,500 bytes (vs 30,000 without overlap). The pre-expanded data is what the PPU nametable update system writes directly.

### State Machine

The game state is driven by $80 (game_state). The main loop at $E290 runs while $80 != 0, calling per-frame processing. When $80 reaches 0, the game transitions to the next mode via $19 (level_transition):
- $19 = $FF: jump to $E243 (restart/title?)
- $19 = other: jump to $E20B (next level/mode)

#### Game Modes ($19 dispatch at bank 6 $8041)

| $19 | Address | Mode | Sub-states ($1A) | Description |
|-----|---------|------|-------------------|-------------|
| 0 | $8068 | Overworld Action | None (linear) | Main gameplay: entity processing, collision, input. Select opens menu (transition $56). |
| 1 | $80B6 | Screen Scroll-Out | 3 ($80C1, $80D5, $80FE) | Transition leaving current screen, sets scroll params. |
| 2 | $812A | Screen Scroll-In | 3 ($80C1, $8135, $8178) | Transition entering new screen, 60-frame delay, scroll direction via $030A. |
| 3 | $818A | NPC/Town Interaction | 3 ($8195, $819B, $80FE) | Dialogue/shop entry, checks $03CC (shop flag), sets up screen. |
| 4 | $81FD | Battle Encounter | 3 ($8195, $8208, $8178) | Random encounter transition, validates area ($33) and encounter type ($030A). |
| 5 | $8252 | RPG Battle | 2 ($825B, $827B) | Turn-based combat. Layout $2B (normal) or $2C (boss via $03C6). |
| 6 | $82BF | Battle Victory Exit | 3 ($80C4, $82CA, $8178) | Post-battle return to overworld, sets $030B=$40 (victory flag). |
| 7 | $82F4 | Dialogue/Text Box | 2 ($82FD, $8311) | Text display with 5-frame advance. Layout $35 (simple) or $46 (portrait). |
| 8 | $8338 | Chapter Intro | 4 ($8345, $8311, $83FD, $8178) | Cinematic sequences, shares text advance with Mode 7. |
| 9 | $845E | Warp/Area Load | 3 ($80C1, $8469, $8384) | Special area transitions (dungeons, town gates). Waits on $030B bit 7. |
| 10 | $8494 | Game Over/Death | 4+ ($849F, $84DE, $8538, $85A2) | Death entity $3A spawn, animate, full reinit ($FF), fade ($7F). |
| 11 | $85DE | Title/Chapter Init | None (linear) | Title screen + chapter intro. Multi-phase init, CHR setup, sprite flip. |

#### Shared Sub-State Blocks

Several sub-state addresses are reused across modes:
- **$80C1** (common setup): Modes 1,2,5,7,9 sub-state 0. Calls $8A3E, $87BE, $E09C, $E8EF, $EACA.
- **$8195** (interaction init): Modes 3,4 sub-state 0. Calls $E0B1 then $80C1.
- **$8178** (screen entry finalize): Modes 2,4,6,8 final sub-state.
- **$80FE** (scroll-out finalize): Modes 1,3 final sub-state.
- **$8311** (text advance loop): Modes 7,8. 5-frame delay, calls $E0CD/$E0D5.
- **$880F** (game-active check): Called by nearly every mode.

#### Key RAM Addresses for State Machine

| Address | Name | Usage |
|---------|------|-------|
| $030A | transition_dir | Screen transition direction / encounter type |
| $030B | transition_flag | Bit 7=warp ready, $40=battle victory |
| $031C | render_flag | Bit 7=rendering active |
| $033B | sub_event | NPC sub-event flag |
| $033C | dialogue_flag | Dialogue type (bit 7=cinematic, nonzero=portrait) |
| $0338 | boss_flag | Nonzero=boss battle layout |
| $03C6 | battle_type | Nonzero=special/boss battle |
| $03CC | shop_flag | Nonzero=shop interaction |
| $0600+ | entity_table | Entity data, 8 bytes per slot |
| $0601 | entities_active | Nonzero when entities are loaded |

---

## Intermediate Output Files

| File | Contents |
|------|----------|

---

## Verification Checklist

- [ ] Ph3: 3+ functions traced and cross-checked against emulator trace
- [ ] Ph4: 5+ sprites/tiles extracted and visually compared to emulator
- [ ] Ph5: key data struct confirmed in emulator memory dump, all fields match
- [ ] Ph6: full game session played, no major logic gaps found
- [ ] Ph7: web port pixel-compared against emulator screenshots

---

## Reference Resources

- **Game**: The Magic of Scheherazade (Culture Brain, 1989)
  - Action-RPG mixing overhead Zelda-like action with turn-based Dragon Quest-style battles
  - Multiple chapters / time periods, party recruitment, magic system
- [NES Dev Wiki - CPU](https://www.nesdev.org/wiki/CPU)
- [NES Dev Wiki - PPU](https://www.nesdev.org/wiki/PPU)
- [NES Dev Wiki - MMC1](https://www.nesdev.org/wiki/MMC1)
- [6502 Instruction Set Reference](https://www.masswerk.at/6502/6502_instruction_set.html)

---

## Next Tasks

### RE Investigation

- [x] Disassemble RESET handler at bank 7 $E19B -- trace initialization sequence
- [x] Disassemble NMI handler at bank 7 $E3C9 -- understand frame update loop
- [x] Identify MMC1 bank-switching routine (writes to $8000-$FFFF control regs)
- [x] Trace NMI palette/scroll update path (from $E3F5 onward)
- [x] Disassemble game frame handler $F73D -- core gameplay logic (frame sync + bank 6 dispatch)
- [x] Trace $E5AA (set_prg_bank) callers to map which bank is loaded when
- [x] Identify game title -- The Magic of Scheherazade (Culture Brain, 1989)
- [x] Extract and render CHR ROM tiles from all 16 banks (4KB banks 0-20 are active graphics)
- [x] Locate and decode text/character encoding table (tile $00-$09=digits, $30-$49=A-Z, $2C=space)
- [x] Map PRG bank contents -- identify banks 1, 3, 5 roles
- [x] Investigate CHR 4KB banks 21-31 -- classified: 21=pointer table, 22-24=dialogue, 25=nametable cmds, 26-28=level data, 29-31=tilemaps
- [x] Decode 4KB bank pairing per game mode (action vs RPG battle vs menu vs overworld)
- [x] Disassemble $E110 and $E11A -- per-frame dispatch system (bank 6 jump table)
- [x] Decode mode_dispatch sub-table at $8041+$46 -- all 12 game modes identified
- [x] Trace bank 2 $B000 music driver entry point
- [x] Map bank 4 data table structures -- full 16KB mapped: 25 jump table entries identified, 5 parallel entity pointer tables (sprite/OAM/seq/anim/proc), tile rendering pipeline (MiniTile->Tile->TileSection), entity slot structure at $0600
- [x] Identify banks 1, 3, 5 roles (trace remaining bank switch patterns)
- [x] Map OAM buffer structure at $0200-$02FF -- 64 sprites x 4B, sprite 0 = hit detect, 1-4 = player, 5-63 = dynamic with $84 wrap. ZP $16/$17 = write ptr/limit
- [x] Trace entity behavior routines at bank 4 $AC00+ -- CORRECTED: $AC00-$BD33 is sprite composition DATA not behavior code. Per-frame OAM records: count + N*(Y-off, attr, tile, X-off). Written to $0200 shadow OAM by entry 2 ($89A7). Sub-tables at $A0BB indexed by animation frame via $9FBB seq data. Handles mirror/flip via bit 7
- [x] Decode bank 4 $A07B-$A0BA transition data -- $A07B is 6th parallel entity table: hitbox/collision data (32 entries ptr16 -> $A32F-$A425). Format: count + N*4B (Y-off, X-off, W, H). Types share hitbox data in groups of 3. Total 7 entity tables now mapped ($9EFB-$A0BA)
- [x] Map bank 5 entity/sprite behavior engine -- 20-entry jtable, two-level AI dispatch (64 entity types x 16 sub-states), player type 5 traced, entity slot stride=8 with $0700 extended array
- [x] Trace bank 5 player sub-states in detail -- 16 sub-states mapped: 0-4,6,9=idle/walk ($873D), 5=screen scroll (4-phase $875E), 7=NPC interact ($87CB), 8=event interact ($87F6), 10=position sync ($8802), 11=hurt/knockback ($881F), 12-13=stunned ($8836), 14=slide/attack ($883B), 15=death 120-frame sequence ($88F6). Activity flags at $89BC, damage calc at $A43E, attack init at $A482
- [x] Map bank 5 entity types 6-31 behavior -- ALL 64 types mapped: 5 categories (simple enemies, player system, NPC/interaction, extended enemies, visual/scripted). Key shared handlers: $893F (standard AI), $8EB8/$8ECB (hit blink/move step), $990D (aggro pursuit), $9A81 (boss timer), $9C7F (NPC companion). Extended flag $71 blocks actions during boss sequences. Types 40-51 share NPC handler, types 36-39 are bosses with 90-frame phase timers
- [x] Trace $E0EC and $E06B -- these are bank dispatch sled entries (bank 6 entry 22, bank 3 entry 1), not frame sync. Real frame sync: $F24A spin-wait on $1C bit 7, $E95B wait_nmi, $F73D game_frame_proc, $E2B8 VRAM drain loop
- [x] Decode text engine code -- bank 1 $8044 (command parser) + bank 2 $A61C/$A91A (text entry lookup/init) + $A3D8 (char decode loop) + $A40B (dictionary lookup via $99B7 table)
- [x] Scan all PRG banks for dictionary tables -- bank 2 $99B7 has 16-group dict ptr table ($99D7-$9C37), plus banks 2/4/6 dicts from prior sessions
- [x] Decode bank 1 dialogue format -- command byte hi3=mode lo5=subindex, text entry table at $9C3A (6B records), bit 7 = word boundary, dict ref = hi4:group lo4:word
- [x] Decode $4A-$4F tile glyphs -- $4F confirmed as '-' (hyphen). $4A-$4E not found in dictionary data, likely dialogue-only punctuation
- [x] Dump and decode all 16 dictionary groups from $99D7-$9C37 -- 97 words: items, equipment, spells (BOLTTOR1-3, FLAMOL1-3), party members, classes, enemy armies, bosses
- [x] Trace CHR bank 22-24 dialogue data format -- 12KB text database in CHR ROM read via PPU $2007. Bank 22 = ~77 NPC/shop entries, bank 23 = RPG battle + story (mixed with tile data), bank 24 = ~11 quest entries. Same tile encoding as dictionary ($30-$49=A-Z). Control: $7A=newline, $7E=paragraph, $7F=end. $52={HERO} player name. Inline params $50-$6F for game values
- [x] Map bank 2 $A000-$AFFF text rendering code -- $A000-$A0DA nametable layout data, $A0DB-$AF06 text rendering pipeline (~3.8KB code): NMI sync ($A0DB), BCD conversion ($A101), multiply ($A1BC), char write ($A377), char decode loop ($A3D8), dictionary lookup ($A40B), text stream loop ($A55C), background fill ($A573), entry lookup ($A61C), data init ($A91A), password check ($AC08). $AF07-$AFFF = zero padding
- [x] Map password symbol grid layout (tile IDs to digit mapping for encode/decode) -- name entry grid at $B9A6: A-Z=$30-$49, 0-9=$00-$09; password entry (bank 2) uses same tile encoding
- [x] Trace full password encode path -- $8250 main loop -> $8680 command processing -> $8746 state encode (3 types: $10=base stats, $30=extended stats, $50=special). BCD accumulator at $89-$8B, checksum via $86EA (multiply by position weight $049B, convert 16-bit to 5 BCD digits). Character output: grid char = 10 - $02D3[X]
- [x] Decode password template data -- $93D0: 16-byte base template (command bytes $00/$D0/$D6/$D7/$C0-$C3/$1E/$1A). $9430: 5 chapter overrides (4B each): ch0=$62/$01/$0A/$00 through ch4=$45/$02/$10/$0C. Templates define the decode sequence for $0570 buffer
- [x] Find secret name detection logic and list all secret codes -- 7 character name codes (1W-5W chapter warp, END credits, SOUND test) at bank 6 $B78C/$B7CC + 2 continuation passwords (CHOCOLA, CORONYA) at bank 2 $AC08/$AC27
- [x] Trace ending/credits state machine at bank 6 $BCA6 -- 11 states: credits music ($63) -> scene transitions -> character animation -> story music ($68) -> credits scroll loop (state 11 at $BE53: 1px/4frames scroll, text from ($0E), $FF-terminated). Sounds: $63, $49, $64, $68. Helpers: $BDE6 transitions, $BFE5 screen setup, $BD8E character sprites
- [x] Map bank 6 $BB1F chapter warp data -- 50 seven-byte records ($BB1F-$BC7C, $FF sentinel at $BC7D). Format: addr_lo, addr_hi, ch0_val, ch1_val, ch2_val, ch3_val, ch4_val. Sets 50 game state addresses ($0084, $0087, $0089, $0300-$03E4) per chapter. Complete "new game at chapter N" initialization
- [x] Map bank 0 SFX data format -- 57-entry pointer table at $8B90, 4-channel sequence engine at $81FE, sequence commands parsed at $82CF (4 types), note freq table (64 notes at $889C), IDs 1-35 = multi-channel jingles, IDs 36-56 = single-channel effects
- [x] Trace bank 0 $85A7 audio_process SFX channel overlay system -- Pulse1 overlay ($0340-$0348) + Noise overlay ($0349-$0351), channel data from $8D17+$FB*4, $0395 bitmask tracks active overlay
- [x] Map bank 0 $B000-$BF8D display rendering module -- screen/nametable building code, screen index table at $BBA2, data at $B3A0-$BAFF, uses fixed-bank PPU helpers
- [x] Identify song IDs by game context -- 199 queue_sound call sites traced, 85 unique IDs mapped: 41 SFX jingles (channel 0), 40 songs (channel 1), 33 noise (channel 2), 14 overlay (channel 3), 23 silent. Key: $62=RPG battle music, $05=overworld, $5F=dungeon, $60=town, $65=victory, $4F=chapter fanfare, $77=no-op sync marker (30 calls in bank 3)
- [x] Map bank 3 RPG battle engine -- 5-entry jtable, $8000-$8FFF data (encounters/palettes), $90AD-$BFEF code (~12KB). Battle flow: init ($90B3) -> screen setup ($940A) -> main loop (enemy turn $9658 -> round exec $B826 -> result check). State $0506 (0=running 1=ending 2=over), round counter $05CE, turn limit $05DA. $77 confirmed no-op sync, $62 is battle music
- [x] Trace bank 3 encounter data format -- 5-level structure: index groups at $8019 (per chapter, navigated by $B56D/$B593), formation table at $8460 (12 x 10B: count + enemy IDs), battle grids at $84E5 (~29 x 3x3 cells), enemy stats at $8606 (HP/ATK/DEF/SPD), sparse placement at $865C-$8BFF ($FF-heavy with $F3/$F4 markers)
- [x] Map bank 3 spell/attack system -- Formation-based tactical combat (not HP subtraction). Attack params at $046E-$0472 (flag/anim/display/target/crit). Hit check $CC43 with RNG $CE8D. Effectiveness tables at $8A26/$8A43 (29 entries: palette group + tile for damage display). Spell setup $A553 (MP check + target resolve). Commands: $02=attack, $0C-$0E=LIBCOM/MONECOM/MOSCOM formations, $10=enhanced, $15/$17=shields
- [x] Trace bank 7 $CA04 battle command system -- 6 functions: $CA04 find alive party member (scan $054D != $FF), $CA16 find targetable enemy ($054D in $19-$1B), $CA30 command menu (formation bitmask from $8C50/$8C56 tables), $CA62/$CA9A HP/MP lookup from 30-level stat table at $8C10 (HP 20-255, MP 10-255), $CAE1 reward accumulator ($05C0/$05C1 gold/XP). Difficulty modifier at $8CA1 (8 entries per enemy type)
- [x] Identify bank 0 $B000 display callers -- 9 call sites via dispatch sled $E006 (bank 0 entry 2). A parameter = sound/screen mode: $4F=chapter title, $5F=dungeon entry, $60=town entry, $65=victory, $66/$67=game clear, $0F=status. Called from bank 7 $CFA6 (battle), $D170 (chapter), $D1E4 (clear), $D26E (victory), $D4D0/$D4F9 (area entry), $D590 (generic), $D5A2 (follow-up)
- [x] Map bank 0 $B3A0-$BAFF screen data -- 32 text-layout command streams (status/results/info screen templates) indexed by 2-byte table at $BBA1. Interpreter at $B0D9: $2F=end, $2E=row advance, $30-$49=A-Z, $00-$09=digits, $0A-$2B=PPU positioning, $80-$8F=dynamic value insert (HP/MP/item counts via $B241 jump table), $8B-$FF=raw border/icon tiles. Content: item names, EXPERIENCE POINTS, enemy army names (GIGADA/CYTRO/MEDUSA/GORGON), spell result text. Tool: dump_screendata.py
- [x] Decode "shop tables" at file offset 0xD534/0xD544 -- NOT shops. Bank 3 $9534 is the inventory-pickup max-cap table (8 entries x 4B: addr_lo, $03, max, slot_idx) read by `inv_pickup_handler` at $94B0. Bank 3 $9524 is a 16-byte indexer for randomized reward groups. Verified: slot 0 cap=15 matches STARDUST max, slots 5/6/7 caps match $0300/$0306/$0307 documented maxes. External editor tools mislabel this as "shop inventory."
- [x] Find and decode bank 2 shop bytecode interpreter -- it's a general-purpose 14-opcode **script VM** (main loop $AA1D, jump table $AC9D, script ptr $CE/$CF) driving dialogue + shops + password screen + events. Opcodes: 0=block list, 1=sound, 2=CHR, 3=jump, 4=call, 5=store-byte, 6=text box, 7=text init, 8=load text entry, 9=compare&3-way-branch (+write-back), 10=window type, 11=numeric input (buy quantity), 12=pwd check, 13=return. Operand addressing via $ACF8 base table ($0300=item/game state). **Shop scripts are bytecode in the CHR-ROM text database** (banks 22-24), not a flat table -- explains why editors couldn't find them. Item counts (CARPET/R.SEED/HORN/HAMMER/RING) manipulated by op5/op9 at $0300+. Entry via bank 6 $818A (entity $36).
- [x] Decode VM script storage + driver -- scripts are byte-streams in bank 2 PRG $B800-$BFFF; bank 1 $810D driver selects via $82 (master table $8B32 -> sub-tables $9046/$9058/$9066/$9078/$9088) + sub-index $04E1; 37 scripts total. Built dis_script.py + scan_scripts.py. FINDING: all 37 are story/cutscene event scripts (IF on progress flags $03E0-$03E4), NO NUMINPUT and NO item-count STOREs -- the shop BUY transaction is NOT in this set.
- [x] Find the actual shop buy-loop -- RESOLVED: shops are flat tables in **bank 1**, NOT bytecode. Shop-pointer table $94ED (8 shops x ptr16, indexed by $04E1) -> shop data $94FD (4 slots x [code, price]). Pipeline: $8680 read -> $A5A0 price*qty -> $A33B haggle (BCD) -> $8A71 magic-shop chapter scaling -> $A736 animated gold spend ($EBDD chokepoint). Verified shop 0 = codes 33/34/10/53 @ 20/20/40/40. See "Shop Inventory & Pricing (bank 1)" section. Corrects both the $D544 and bank-2 claims.

### RE vs GameFAQ Guide Comparison

Cross-referenced RE findings against `docs/gamefaq guide/gamefaqguide.txt`. Status: MATCH = confirmed, CONTRADICTION = conflict, NEW = info not found in RE, NEEDS REVIEW = uncertain.

**1. Level-Up / EP Thresholds: MATCH**
All 24 EP thresholds match exactly (ROM = EP-1). Stat table offset confirmed (player starts at index 5).

**2. BREAD Item: RESOLVED (was CONTRADICTION)**
- Guide: "Automatically restores 50 HP when you lose all HP." Max 10.
- RE: **$0306** is the BREAD counter. Auto-decremented on death at $F1FA (overworld) and $8AB5 (RPG battle), restoring HP to 50. Warp max = 10. MATCH.
- RE correction: $0300 was originally mislabeled as "bread_count." It's actually the **Bread of Gortrat** event counter -- a map heal event (walk onto specific spots), limited uses (max 9), NOT the carried Bread item.
- $8BD2 (20 HP restore) is the Gortrat bread effect, not shop Bread.

**3. MASHROOB Item: RESOLVED (was NEEDS REVIEW)**
- Guide: "Automatically restores 50 MP when you lose all MP." Max 10.
- RE: **$0307** is the MASHROOB counter. Auto-decremented at bank 6 $8BFB on MP depletion. Warp max = 10. MATCH.
- $0301 is the MP equivalent of the Gortrat event counter, not carried Mashroob.

**4. Item Max Counts: PARTIAL MATCH**
- Guide: BREAD=10, MASHROOB=10, CARPET=15, R.SEED=5, MAP=1, KEY=9, HORN=5, HAMMER=5, RING=1, AMULET=9
- RE: Password max for $0300=9, $0301=9. Warp data for $0306=10, $0307=10.
- BREAD max 10 matches $0306. CARPET max 15 is not yet verified against ROM.

**5. Spell Effects and MP Costs: NEW INFO**
- Guide provides MP costs: OPRIN=5, PAMPOO=2, BOLTTOR1=4, DEFENEE=2, FLAMOL1=20, CORBOCK=2, SHRINK=2, CARABA=20, RAMIPAS=10, MARITA=4, BOLTTOR2=15, BOLTTOR3=20, FLAMOL2=25, FLAMOL3=30
- RE: MP costs not traced (stored in spell data tables, not yet decoded)
- PAMPOO restores 10 HP (guide). MARITA restores 50 HP (guide). Not yet verified in ROM.

**6. Secret Codes: RESOLVED (was PARTIAL MATCH)**
- Guide lists W1-W5 (min items, enter 4 times) AND 1W-5W (max items). **Both confirmed in ROM.**
- 1W-5W: Direct name match at $B7CC -> $BAD1 chapter warp with full items.
- W1-W5: Separate mechanism at $B239. Entering "W1" fails name check, passes password prefix check (W + valid digit, returns A=$01). Retry counter $0C counts to 3 (4th attempt triggers). Calls SAME $BAD1 warp handler BUT clears $87=0 (minimum world flags/items). **Guide "four times" matches code CMP #$03.**
- Guide does NOT mention CHOCOLA/CORONYA passwords (RE found at $AC27). These are continuation code secrets on a different input screen.

**7. Sound Test Controls: GUIDE IS WRONG**
- Guide: "Use up and down to choose a sound and press Start to listen."
- ROM ($BA3C): **Up** (new press $C2 & $08) = PLAY sound. **B or Start** (held $C0 & $50, rate-limited every 8 frames) = NEXT sound. **A or Select** (held $C0 & $A0) = PREVIOUS sound.
- Guide errors: (1) No Down button used at all. (2) Start advances to next, doesn't play. (3) Up plays, not Start.

**8. Party Member Attacks: NEW INFO (not in RE)**
- Guide lists attacks per character: Coronya (Rod, Defenee, Mymy), Faruk (Fight, Gilzade), Kebabu (Arrow, Bolttor1, Seal), etc.
- RE: Party attack names NOT in dictionary group 7 or any decoded group. Names like Gilzade, Seal, Silleit, Whistle, Mymy, Perius, Matato are likely stored as CHR tile graphics, not dictionary text.
- These are RPG battle party abilities, separate from the player's spell system.

**9. Formation Magic Names: NEW INFO (not in RE)**
- Guide: GYGATORN, MONIBURN, TORNADOR, STARDON, THUNDERN, FIREBOLT
- RE: Formation names (CYGNUS, LIBRA, etc.) in dict group 12, but magic attack names not found.
- These magic names are likely CHR tile graphics rendered during RPG battles.

**10. Formation Pairs: NEW INFO**
- Guide: CYGNUS=Coronya+Faruk, LIBRA=Gun Meca+Kebabu, ARIES=Epin+Supica, SIRIUS=Pukin+Mustafa, KAITOS=Gubibi+Rainy, DRAGON=Faruk+Hassan
- RE: Formation system identified in bank 3 but pair assignments not decoded.

**11. Enemy Stats: MATCH (verified)**
- Enemy stat table at bank 3 **$8341** (NOT $8606 as previously thought). 29 entries, 10 bytes each, IDs $0D-$29.
- Format: byte 0=EP reward, byte 1=Rupia reward, byte 7=HP. Bytes 2-6=combat stats. **Direct lookup, no formula.**
- All guide values verified against ROM:

| ID | Enemy | HP | EP | Rupia | Match |
|----|-------|----|----|-------|-------|
| $0D | Pandarm | 16 | 7 | 5 | YES |
| $0E | Wazarn | 54 | 16 | 10 | YES |
| $10 | Miniyad | 12 | 10 | 1 | YES |
| $11 | Amaries | 12 | 4 | 21 | YES |
| $12 | Pharyad | 54 | 16 | 10 | YES |
| $13 | Gigadan | 72 | 24 | 8 | YES |
| $14 | Cytron | 24 | 8 | 10 | YES |
| $15 | Gazeil | 36 | 12 | 16 | YES |
| $17 | Gangar | 54 | 16 | 40 | YES |
| $19 | Medusa | 24 | 20 | 4 | YES |
| $1A | Gorgon | 88 | 34 | 34 | YES |
| $1B | GorgonX | 122 | 174 | 1 | HP match |
| $1C | Romsarb | 54 | 18 | 22 | YES |
| $1D | Razaleo | 111 | 30 | 34 | YES |
| $1E | Corsa | 16 | 10 | 10 | YES |
| $1F | Megarl | 42 | 15 | 15 | YES |
| $20 | Zahhark | 76 | 20 | 29 | YES |
| $24 | Blimro | 3 | 2 | 1 | YES |
| $26 | Meldo | 4 | 3 | 10 | YES |
| $28 | Samrima | 3 | 2 | 5 | YES |

**NEW: Item Counter Addresses (fully verified):**
- $0306 = BREAD (max 10, auto-restore 50 HP on death) -- CONFIRMED
- $0307 = MASHROOB (max 10, auto-restore 50 MP) -- CONFIRMED
- $0308 = KEY (auto-used on locked doors, DEC at $F2CB + sound $03) -- CONFIRMED
- $0309 = AMULET (max 9, auto-reverses transformation spells) -- CONFIRMED via bank 6 $87F4/$87FA
- $030A = MAP or navigation flag (checked extensively in banks 4/5/6 for map display access)
- $0300 = Bread of Gortrat event counter (NOT carried Bread item)

HUD bottom-right displays: $0306(BREAD), $0307(MASHROOB), $0308(KEY), $0309(AMULET) -- sequential addresses.

**Item max counts (guide values, ROM-verified where noted):**

| Item | Max | Address | ROM Verified |
|------|-----|---------|-------------|
| BREAD | 10 | $0306 | YES (warp data max=10) |
| MASHROOB | 10 | $0307 | YES (warp data max=10) |
| KEY | 9 | $0308 | YES (guide), auto-DEC at $F2CB |
| AMULET | 9 | $0309 | YES (guide), auto-use at $87F4 |
| CARPET | 15 | $0300+ (via pickup) | Guide value |
| R.SEED | 5 | $0300+ (via pickup) | Guide value |
| HORN | 5 | $0300+ (via pickup) | Guide value |
| HAMMER | 5 | $0300+ (via pickup) | Guide value |
| MAP | 1 | $030A (flag) | YES (checked extensively in banks 4/5/6) |
| RING | 1 | $0300+ (via pickup) | Guide value |

CARPET, R.SEED, HORN, HAMMER, RING are bought from the **bank 1 shop tables** ($94ED/$94FD, see "Shop Inventory & Pricing"), not a bank 2 bytecode interpreter (that earlier claim was wrong -- the bank 2 VM only drives cutscenes/dialogue). Item delivery on purchase/pickup goes through `inv_pickup_handler` (bank 3 $94B0) with per-item max caps in the $9534 table; max counts for these five come from the guide.

**Inventory-increment / max-cap table (bank 3 $9534, file offset 0xD544):**

8 records x 4 bytes. Read by `inv_pickup_handler` at bank 3 $94B0. Format: `addr_lo, $03, max_value, slot_idx`. The first two bytes form a pointer to the RAM inventory variable in the $03xx page. Routine: copy 4B to $00-$03, then `LDA ($00),Y` to read current value; if `< $02` (max), `STA ($00),Y` writes incremented value; if `slot_idx >= 6` also `INC $0515,X` to mirror into party slot.

| Slot | Bytes | Pointer | Max | Variable |
|------|-------|---------|-----|----------|
| 0 | `11 03 0F 00` | $0311 | 15 | STARDUST charges (matches REVERSE max=15) |
| 1 | `0F 03 01 01` | $030F | 1 | ROD charges (cap=1 here vs warp max=5; pickup gives +1 only) |
| 2 | `10 03 01 02` | $0310 | 1 | FLAME charges |
| 3 | `01 03 01 03` | $0301 | 1 | Gortrat mashroob counter |
| 4 | `12 03 05 04` | $0312 | 5 | Max MP/power |
| 5 | `00 03 09 05` | $0300 | 9 | Gortrat bread counter (matches max=9) |
| 6 | `06 03 0A 06` | $0306 | 10 | BREAD (matches max=10, mirrors to $0515) |
| 7 | `07 03 0A 07` | $0307 | 10 | MASHROOB (matches max=10, mirrors to $0516) |

**16-byte indexer at bank 3 $9524 (file offset 0xD534):** maps a `(group * 4) + (RNG AND $03)` selector to a slot 0-7. 4 groups of 4 entries: `{0,1,6,7}, {0,1,5,2}, {0,1,3,4}, {0,1,3,2}`. Used by the same handler to randomize which item drops within a reward group.

**Critical note:** This table is NOT the shop slot table. Real shop transactions are handled by the bank 2 bytecode interpreter (see Next Tasks). External editor tools labeling 0xD544 as "shop inventory" are misinterpreting it -- byte 0 is a RAM pointer low-byte, not an item ID, and byte 2 is a max-cap, not a price.

**12. Spell MP Costs: UNVERIFIED (embedded in handlers)**
- Guide costs: OPRIN=5, PAMPOO=2, BOLTTOR1=4, DEFENEE=2, FLAMOL1=20, BOLTTOR2=15, BOLTTOR3=20, FLAMOL2=25, FLAMOL3=30, CORBOCK=2, SHRINK=2, CARABA=20, RAMIPAS=10, MARITA=4
- RE: No single cost lookup table found. Costs are embedded as immediate values (SBC #$xx) in individual spell casting code. Guide values accepted as reference pending per-spell verification.

**13. Party Member Attacks: NEW INFO (CHR tile graphics)**
- Guide: Character-specific RPG battle attacks (Gilzade, Seal, Mymy, Silleit, Whistle, Perius, Matato)
- RE: NOT in any PRG dictionary group. Stored as CHR tile graphics rendered during RPG battle menus.

**14. Formation Magic Names: NEW INFO (CHR tile graphics)**
- Guide: GYGATORN, MONIBURN, TORNADOR, STARDON, THUNDERN, FIREBOLT
- RE: Not in PRG dictionary. CHR tile graphics for battle display.

**12. Class System: MATCH**
- Guide: Fighter (strong sword), Saint (weak, gets Pukin), Magician (strong rod)
- RE: FIGHTER/SAINT/MAGICIAN in dict group 10. Class change at mosques via bank 6 secret codes and game menus.

**13. MONECOM Effect: NEW INFO**
- Guide: "Gives you 999 Rupias and maximum amount of each item. Can only be used once."
- RE: MONECOM is battle command $0D. The "full restore" mechanism may relate to item 25 handler ($966A) which maxes resources and zeros gold -- though we found item 25 is unreachable via normal gameplay.

**14. Weapon Upgrade Levels: PARTIALLY MATCHED**
- Guide: SWORD upgrades at levels 3,5,8,12,14,22. ROD upgrades at levels 4,7,11,15. SWORD/ROD at levels 9,13,17,19,21,23.
- RE: Reward byte hi4=$80 = HP/stat upgrade (no flag set). These correspond to "no spell" levels. Weapon type ($80 vs $C0) may encode sword-vs-rod-vs-both. Not yet decoded.

**15. Chapter Boundaries: MATCH**
- Guide: Ch1=Lv1-5, Ch2=Lv6-10, Ch3=Lv11-15, Ch4=Lv16-20, Ch5=Lv21-25 (with auto-level at chapter boss)
- RE: Warp data $84 values (4,9,14,19,24) confirm 5-level spans per chapter.

### Web Port Fixes

### Documentation
