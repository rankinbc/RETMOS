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
| 0x10010 | 0x1400F | 16KB | PRG bank 4 | Data tables (pointer reads) |
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
| 0 | Sound engine | Called every NMI via trampoline; APU $4015, $883F sound player |
| 1 | Screen/UI engine + dialogue | 24-entry jump table at $8000; dispatched via $E03F-$E011 trampoline. Code for title screen, chapter intros, menu layouts, HUD rendering, NPC dialogue display. Contains word dictionary at $B8B1 and formatted dialogue text at $BB-$BF |
| 2 | Music data/driver | 33 songs + 18 SFX sequences. Music sequencer ($BE81) drives 4 APU channels. Called from bank 0 $80D8 via $E9DD trampoline |
| 3 | RPG battle engine | 5-entry jump table at $8000 (3 route to bank 7 code). Entry 0 ($90AD) = battle init. Dispatched via $E06D-$E05F trampoline. Contains battle screen setup ($940A), palette/tile layout ($8B56+), encounter data tables ($8400+, $FF-heavy), entity/party stat processing. Called from bank 7 $C883/$C89D and bank 5 $AE8D |
| 4 | Data tables | $E776: LDA #$04, JSR mmc1_write_prg, then pointer reads via ($D1),Y |
| 5 | Entity/sprite behavior engine | 22-entry jump table at $8000; dispatched via $E0D5-$E0AB trampoline (most-called bank, 26 calls from bank 6). Entity type dispatch table at $80E5 (32+ entity types). Per-type behavior state machines with sub-state pointer tables. Handles player sprite, NPC movement, enemy AI, collision response, entity spawning. $B48C+ contains entity stat/parameter tables. $BFC0-$BFDA has additional data, $BFE0-$BFFF = $FF padding |
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

**Sound request queue** ($03E5/$03E7): Game code writes sound IDs to `$03E7+N` and increments `$03E5` (count). Bank 0 `$809E` drains this queue each frame, calling `$883F` (play_sound) for each entry.

**queue_sound ($E992)**: The main API for triggering sounds from game code. A=sound ID. Called from 84 sites (21 in bank 7, 63 in bank 6). Special values: $FF = silence all channels + reset, $00 = no-op. Normal values are enqueued (max 6 pending). The enqueued IDs are processed by `play_sound` ($883F) in bank 0, which routes them to the appropriate APU channel based on a priority table at `$800E`.

**play_sound ($883F)** routing: Each sound ID indexes into `$800E+ID` for a channel/priority byte:
- Bits 7:6 = channel (0=Pulse1, 1=Pulse2, 2=Triangle, 3=Noise)
- Bits 5:0 = priority (higher overrides current SFX on that channel)
- $00 = silent/invalid ID
- Current channel priority stored at ZP `$F8+channel` (0-3)
- SFX data pointers at `$8B90+ID*2` point to 8-byte SFX records in bank 0 $8C02-$8CF9 (62 entries, stride 8)

**NMI audio call chain:**
1. NMI -> $E548: switch to bank 0, JSR $8000 (-> JMP $809E sound_main)
2. $809E: drain $03E7 queue via play_sound, enable APU, ASL $F6, call $85A7 (audio_process)
3. $80D8: LDA #$02, JSR $E9DD -> switch to bank 2, JSR $B000 (music sequencer)
4. $80F9: process $F8 SFX request (bank 0 SFX overlay)
5. $80E2: clear $F8-$FB requests
6. Restore ZP $D9-$DF, return

#### Unified Bank Dispatch Architecture

Bank 7 contains dispatch entry points for ALL 7 switchable banks at regular intervals. Each loads the bank number and jumps to the common dispatch at $E11E, which switches PRG, reads a function pointer from the target bank's jump table at $8000+($3A*2), and calls it:

| Entry Addr | Bank | Variant Addrs (INC $3A offsets) |
|------------|------|---------------------------------|
| $E00E | 0 | $E008(+1), $E00A(+0) |
| $E043 | 1 | $E03D(+1), $E03F(+0), $E046+(+1..+3) |
| $E05C | 2 | $E056(+1), $E058(+0) |
| $E071 | 3 | $E06B(+1), $E06D(+0), $E074+(+1..+3) |
| $E0A8 | 4 | $E0A2(+1), $E0A4(+0) |
| $E0D9 | 5 | $E0D3(+1), $E0D5(+0), $E0DC+(+1..+3) |
| $E11A | 6 | $E110(+5), $E112(+4)...$E118(+1) |

Each variant adds N to $3A before dispatching, allowing callers to offset the jump table index.

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
- [ ] Map bank 4 data table structures (pointer dereferencing at $E776)
- [x] Identify banks 1, 3, 5 roles (trace remaining bank switch patterns)
- [ ] Map OAM buffer structure at $0200-$02FF
- [ ] Trace $E0EC and $E06B -- frame sync / wait routines
- [ ] Decode text engine code -- find the routine that processes $80+ control codes in dialogue
- [ ] Scan all PRG banks for dictionary tables (search for bit-7-marked word sequences)
- [ ] Decode bank 1 dialogue format -- map control codes to functions (newline, pause, dict ref)
- [ ] Map bank 0 SFX data format ($8B90 table, 62 SFX records at $8C02-$8CF9, stride 8)
- [ ] Identify song IDs by game context (trace LDA #imm; JSR $E992 patterns to map song numbers to overworld/battle/town/etc)
- [ ] Trace bank 0 $85A7 audio_process SFX channel overlay system ($0340/$0349 channel data)

### Web Port Fixes

### Documentation
