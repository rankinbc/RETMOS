# The Magic of Scheherazade (NES) -- Binary Architecture Reference

## Binary Layout

| Component | File Offset | Size | Description |
|-----------|-------------|------|-------------|
| iNES Header | $00000-$0000F | 16B | Format: `4E 45 53 1A`, Mapper 1 (MMC1) |
| PRG ROM | $00010-$2000F | 128KB | 8 x 16KB banks (banks 0-7) |
| CHR ROM | $20010-$4000F | 128KB | 32 x 4KB banks (banks 0-31) |

**CPU**: Ricoh 2A03 (6502 variant, no BCD). **Mapper**: MMC1/SxROM (serial register writes to $8000-$FFFF).

**Vectors**: RESET=$E19B, NMI=$E3C9, IRQ=$E19B (bank 7, fixed at $C000-$FFFF).

---

## PRG Bank Architecture

Bank 7 ($C000-$FFFF) is permanently mapped. Banks 0-6 are switched into $8000-$BFFF via MMC1 PRG register at $E596.

| Bank | Role | Key Functions |
|------|------|---------------|
| 0 | Sound engine + display | NMI sound ($809E), SFX engine ($80F9-$883E), note tables ($889C), SFX data ($8B90-$AFFF), display module ($B000-$BF8D) |
| 1 | Screen/UI + password | Text command parser ($8044, 7 modes), password encode ($8250/$8680/$8746), password decode ($947B), BCD math ($870F/$872B/$8BBC) |
| 2 | Music + text render | Music sequencer ($B000/$BE81), text rendering ($A0DB-$AF06), dictionary ($99B7, 97 words), text entry table ($9C3A), password secrets ($AC08) |
| 3 | RPG battle engine | Battle init ($90B3), round execution ($B826), encounter data ($8019/$8341/$8460), spell/attack system ($A000+), stat table ($8C10) |
| 4 | World data + entities | Screen load ($813B), tile pipeline ($841B/$8500), 7 entity tables ($9EFB-$A0BA), sprite composition ($AC00-$BD33), WorldScreen reader ($82A1) |
| 5 | Entity behavior | 64 entity types ($80E5), 16 player sub-states ($81A3), entity AI ($893F/$990D/$9A81/$9C7F), XP triggers ($89CC) |
| 6 | Game logic | Secret codes ($B78C/$B7CC), item system ($98E8, 30 items), chapter warp ($BAD1/$BB1F), ending credits ($BC7F/$BCA6), shop/event handlers |
| 7 | Core engine (fixed) | NMI ($E3C9), RESET ($E19B), bank switching ($E596), dispatch sleds ($E000-$E11A), frame sync ($F24A), queue_sound ($E992), data read ($EFA8) |

---

## Bank Dispatch Architecture

Game logic is dispatched via INC $3A sleds that accumulate an entry index, then switch to the target bank and read from its $8000 jump table:

```
Sled entry -> INC $3A (N times) -> STA $3B -> LDA #bank -> JMP $E11E
$E11E: switch PRG to bank -> Y = $3A*2 -> read ptr from $8000+Y -> JMP (ptr)
```

| Sled Range | Bank | Entries |
|------------|------|---------|
| $E000-$E00A | 0 | 6 (entry 2 = $B000 display) |
| $E011-$E03D | 1 | 24 (text/UI modes) |
| $E05F-$E06D | 3 | 8 (RPG battle) |
| $E074-$E0A4 | 4 | 25 (screen/entity data) |
| $E0AB-$E0D3 | 5 | 20 (entity behavior) |
| $E0DB-$E10F | 6 | 26 (game logic) |

---

## Per-Frame Execution Flow

```
NMI ($E3C9):
  -> PPU sprite DMA ($0200 -> OAM)
  -> VRAM transfer ($0163 buffer -> PPU nametable)
  -> Palette update ($04A0 shadow -> $3F00)
  -> CHR bank update (from $AD/$AE/$AF)
  -> Scroll register update
  -> Sound: $E548 switch to bank 0, JSR $8000:
     1. Drain sound queue ($03E7) via play_sound ($883F)
     2. Enable APU ($4015=$0F)
     3. Audio process ($85A7, SFX overlay)
     4. Bank 2 music driver ($B000 via $E9DD)
     5. Process SFX request ($80F9)
     6. Clear $F8-$FB

Game Loop ($F73D):
  -> Wait NMI ($F24A spin on $1C bit 7)
  -> Bank 6 dispatch (game mode processing)
  -> Bank 5 dispatch (entity tick all, slots 1-31)
  -> Bank 4 dispatch (screen/sprite updates)
  -> Frame counter increment
```

---

## Sound System

**Two-engine architecture spanning banks 0 + 2:**

| Engine | Bank | Entry | Channels | Purpose |
|--------|------|-------|----------|---------|
| SFX Jingle | 0 | $80F9 | 4 (Pulse1/2, Triangle, Noise) | Multi-channel effects via $8B90 table (57 entries) |
| SFX Overlay | 0 | $85A7 | 2 (Pulse1, Noise) | Short overlay effects on music |
| Music Seq | 2 | $B000/$BE81 | 4 (Pulse1/2, Triangle, Noise) | 33 songs + 18 noise SFX |

**Sound ID routing**: queue_sound ($E992) -> play_sound ($883F) -> $800E priority table (bits 7:6 = channel -> $F8-$FB).

85 unique sound IDs. Key: $62=battle music, $05=overworld, $5F=dungeon, $60=town, $65=victory, $4F=chapter fanfare.

---

## Entity System

**7 parallel tables at bank 4 $9EFB-$A0BA** (32 entries each, entity types 0-31):

| Table | Address | Data |
|-------|---------|------|
| OAM flags | $9EFB | 1B: sprite priority/palette |
| Size flags | $9F1B | 1B: render size |
| Sprite CHR | $9F3B | ptr16 -> $A630 (tile data per direction) |
| OAM layout | $9F7B | ptr16 -> $A98C (multi-sprite positioning) |
| Sequences | $9FBB | ptr16 -> $A429 (animation frame streams) |
| Sprite comp | $A03B | ptr16 -> $A0BB -> $AC00 (per-frame OAM records) |
| Hitboxes | $A07B | ptr16 -> $A32F (collision boxes) |

**Entity slots**: 32 x stride 8 at $0600-$06FF (primary) + $0700-$07FF (extended). Slot 0 = player.

**64 entity types** dispatched via bank 5 $80E5 two-level table (type -> sub-state -> handler).

**Player (type 5)**: 16 sub-states at $81A3 (idle, walk, screen scroll, NPC interact, event, position sync, hurt, stunned, slide/attack, death).

---

## RPG Battle System

**Formation-based tactical combat** (bank 3 + bank 7):

```
Battle Init ($90B3): silence -> music $62 -> screen setup ($940A) -> party init ($B5AB)
Main Loop ($90ED): enemy turn ($9658) -> round exec ($B826) -> result check -> round++
  Battle state $0506: 0=running, 1=ending, 2=over
```

**Enemy stats**: Direct lookup at $8341 (29 entries x 10B, IDs $0D-$29). Byte 0=EP, 1=Rupia, 7=HP.

**Encounter data** (5 levels): index groups ($8019) -> formations ($8460, 12x10B) -> 3x3 grids ($84E5) -> stat table -> placement data.

**Damage**: Hit check ($CC43) with RNG ($CE8D). Effectiveness tables at $8A26/$8A43 (palette-based visual damage). Commands: $02=attack, $0C-$0E=LIBCOM/MONECOM/MOSCOM, $10=enhanced, $15/$17=shields.

**Stat progression**: 30-level table at $8C10 (HP 20-255, MP 10-255). Player starts at index $84+5.

**Formation pairs**: pair table at bank 3 $89C0 (6 x 5B: `[00, memberA, memberB, formationID, 00]`) -- pairs (1,10)(4,6)(3,9)(10,11)(7,2)(5,8); member 10 = Faruk, 1 = Coronya, 11 = Hassan. Classifiers set $05C2 (pair index, exact-ID scan) and $05C3 (group index, type-range scan vs $899C); command menu ($CA30) enables formation iff bit set in matrices $8C50/$8C56.

---

## Text/Dialogue System

**Three-bank pipeline**: Bank 1 (command parse) -> Bank 2 (render) -> CHR 22-24 (dialogue data).

```
Command byte: bits 7:5 = mode (0-6), bits 4:0 = sub-index
  Mode 3 -> CHR dialogue: sub-index 0-7=bank 22, 8-29=bank 23, 30-31=bank 24
  -> text_entry_lookup ($A61C): ID*6 -> $9C3A table -> 6B header
  -> text_char_loop ($A3D8): per-char decode from ($00),Y
  -> dict_lookup ($A40B): hi4=group, lo4=word via $99B7 (16 groups, 97 words)
  -> text_write_char ($A377): write to $0163 nametable buffer
  -> NMI transfer to PPU VRAM
```

**CHR dialogue**: ~91 entries across 3 banks. Same tile encoding ($30-$49=A-Z, $2C=space). Control: $7A=newline, $7E=paragraph, $7F=end. $52={HERO} player name.

---

## World Map & Screen Rendering

**WorldScreen records** (16B per screen, CHR ROM via PPU):

ZP $B0-$BF loaded by `read_worldscreen` ($82A1) from screen index $AB.

**Tile rendering** (3-level hierarchy, 32x32 pixel game tiles):
```
TileSection (32B from CHR, 8x4 tile IDs, 2 sections = full screen)
  -> tile_table ($9AFB + ID*4): 2x2 MiniTile IDs
    -> minitile_table ($95FB + ID*4): 2x2 CHR tile indices
      -> PPU pattern table: 8x8 pixel tiles
```

**Screen load** (bank 4 entry 12, $813B): read WorldScreen -> load TileSections from CHR -> build nametable -> load palette -> spawn entities from ObjectSet.

**Navigation**: screen adjacency links in WorldScreen record bytes 4-7 ($FF=wall, $FE=building door). Chapter boundaries at $D386. $84 = linear level progression.

**Building entry**: nav byte $FE -> bank 5 $AD34 passes the Content byte verbatim as the bank 1 UI command (hi3=mode, lo5=sub-index): $6x=shops (id = Content & $1F), $8x-$9x=chapter-keyed NPC scripts, $Ax=hotels, $Cx=time doors.

**ExitPosition** ($B9): hi4=X column, lo4=Y row (16px grid, +8 center) via bank 4 $826B. Used for stairways (Event bit6: Content=destination screen), Content $01-$1F entry, and warp arrivals.

**Warps/time doors**: destination = table at bank 6 $98C0 (5 chapter-groups x 8 screen indices), looked up at $8D5A as $98C0[$82*8+door]; present<->past pairing is pure data. Only 3 hardcoded screen references exist in the entire ROM: $98C0 table, bank 6 $90D1 (CMP #$1A secret event), chapter-start values in warp data $BB1F.

---

## Game State ($0300-$03E4)

### Consumable Items (HUD display)

| Address | Item | Max | Mechanism |
|---------|------|-----|-----------|
| $0306 | BREAD | 10 | Auto-restore 50 HP on death ($F1FA/$8AB5) |
| $0307 | MASHROOB | 10 | Auto-restore 50 MP on depletion ($8BFB) |
| $0308 | KEY | 9 | Auto-use on locked doors ($F2CB) |
| $0309 | AMULET | 9 | Auto-reverse transformation ($87F4) |
| $030A | MAP | 1 | Gates map-overlay render (bank 4 $8C1E) |

### Equipment & Progression

| Address | Name | Values | Notes |
|---------|------|--------|-------|
| $0302 | Armor | 0/1/2 | 0=none, 1=R-ARMOR (half dmg), 2=L-ARMOR (quarter) |
| $030E | Player level | 2-6 | Entity spawn scaling |
| $0322 | Magic level | 2-6 | Spell power scaling |
| $0332 | Equipped sword | dynamic | Written by sword pickup ($8E3D) |
| $030F-$0313 | Charge slots | caps 1/5/15/5/5 | Shop $5x purchase targets; one-time buys init from $87F2 = [1,1,1,5,5]. Caps match guide RING/HORN-HAMMER-R.SEED/CARPET maxes -- labels (ROD/FLAME/STARDUST) pending re-verification |

**Player MP**: 3 BCD digits at ZP $8C/$8D/$8E (hundreds/tens/ones); generic BCD sub/add at $EBFF/$EC21 (bank 7). Current HP binary at ZP $81, max HP $91.

### Spells (13 XP-unlocked at $97EC)

| Flag | Spell | Level | EP |
|------|-------|-------|----|
| $0329 | PAMPOO (2 MP, heal 10 HP) | 2 | 20 |
| $0323 | BOLTTOR1 (4 MP, lightning) | 3 | 80 |
| $0330 | DEFENEE (2 MP, temp defense) | 4 | 240 |
| $0326 | FLAMOL1 (20 MP, fire all) | 7 | 780 |
| $032D | CORBOCK (2 MP, shrink enemies) | 9 | 1280 |
| $0324 | BOLTTOR2 (15 MP) | 11 | 2000 |
| $032E | SHRINK (2 MP, replaces CORBOCK) | 13 | 3000 |
| $0327 | FLAMOL2 (25 MP) | 14 | 3800 |
| $0331 | RAMIPAS (10 MP, no encounters) | 15 | 4800 |
| $0325 | BOLTTOR3 (20 MP) | 17 | 6000 |
| $032F | CARABA (20 MP, replaces SHRINK) | 20 | 10800 |
| $032A | MARITA (4 MP, heal 50 HP) | 21 | 11300 |
| $0328 | FLAMOL3 (30 MP) | 23 | 14550 |

All MP costs ROM-verified from the use-record table (bank 6 $98E8, bytes +5..+7, BCD). Two additional castables not XP-gated: RESEALO (1 MP), VELVER (2 MP). Cost deduct path: $8A9C -> $8BE5 -> $EBFF against MP at $8C-$8E, with MASHROOB auto-refill (+50).

**Level-up reward byte** ($97EC records, byte 2): bit7 = marker, **bit6 = SWORD upgrade, bit5 = ROD upgrade**, lo4 = spell progression index (0 = stat-only). Drives level-up announcement via $A702 (msg types 3/4); damage itself scales from level/equip tier in bank 5 $A43E.

### Combat Gates ($0336-$033F)

Progressive unlock flags (set by chapter warp only): $0336=sword, $0337=rod, $0338=magic, $0339=adv magic, $033A=formation, $033B=party, $033D/$033E=base melee/defense (always), $033F=ultimate (ch4).

### Currency & Chapter

| Address | Name | Notes |
|---------|------|-------|
| $03D6 | Chapter (BCD) | 1-5 |
| $03D9-$03DB | Gold (BCD) | 3 digits (hundreds/tens/ones) |

---

## Secret Codes

**Name entry** (7 codes at $B7CC): 1W-5W = chapter warp with max items. END = credits. SOUND = sound test (Up=play, B/Start=next, A/Select=prev).

**W1-W5 retry** ($B239): Enter W+digit as name 4 times -> chapter warp with MIN items ($87=0).

**Continuation passwords** ($AC27): CHOCOLA ($04D0=0), CORONYA ($04D0=1).

---

## Password System

**Encode** ($8250): 8 display groups x 4 command positions. BCD accumulator $89-$8B with position weight $049B. Template at $93D0 (16B), chapter overrides at $9430.

**Decode** ($947B): command bytes hi4=$40(level)/$60(stat)/$20(armor)/$C0/$D0(extended).

**Format**: Passwords start with W + chapter digit + 6 encoded characters.

---

## Shop System (bank 1)

Flat tables, not bytecode. Shop-pointer table `$94ED` (8 shops x ptr16, indexed by shop id $04E1) -> shop data `$94FD+` (4 slots x `[code, price]`). Read at $8680 -> $04D5/$04D6.

**Pricing pipeline**: $A5A0 (price x qty) -> $A33B (haggle, BCD) -> $8A71 (magic-shop chapter scaling via $8AAC base table x $8B89) -> $A736 (animated gold spend, $EBDD chokepoint).

**Delivery + caps** (state-command processor $8746, shared with password decode): code hi4 `$1x` -> $0300+lo4 (cap 9), `$3x` -> $0303+lo4 (cap 10; $33/$34 = BREAD/MASHROOB, +qty $049B), `$5x` -> charge/one-time slots at $030F+ (caps 1/5/15; one-time buys reject if owned, init charges from $87F2). At-cap purchase aborts with error $0E -- gold not spent.

**Ownership**: $03C0 array (11 entries stride 2), set by item_acquire ($8AB7), checked by $8A9A so spells/key items can't be rebought.

---

## Script VM (bank 2 $AA1D)

General-purpose 14-opcode bytecode interpreter driving dialogue, cutscenes, and the password screen (NOT shops). Main loop $AA1D, opcode jump table $AC9D, script pointer $CE/$CF. Key ops: 5=store-byte, 6=text box, 9=compare + 3-way branch with write-back, 11=numeric input, 12=password check. Operand addressing via $ACF8 base table.

37 story/cutscene scripts live in bank 2 PRG $B800-$BFFF, selected by the bank 1 driver $810D (master table $8B32, sub-index $04E1); all gate on progress flags $03E0-$03E4. Tools: dis_script.py, scan_scripts.py.

---

## Item/Spell Use-Record Table (bank 6 $98E8, 30 entries x 8B)

Record: `[ID, flags1, flags2, handler_lo, handler_hi, cost_h, cost_t, cost_o]`. flags2 bit4: 1 = HP cost (binary byte at +5, BREAD auto-refill), 0 = MP cost (3 BCD digits, MASHROOB auto-refill). Use path: $8A9C charges cost then `JMP (handler)`.

Record groups: 1-6 weapons/actives (ROD/FLAME/STARDUST/CIMARON/CRYSTAL/ISFA), 7-8 quest keys (KEY/AMULET), 9-16 named SWORD tiers + quest items in the old item-name mapping **but carrying BOLTTOR1-3/FLAMOL1-3/PAMPOO/MARITA costs in dict-7 order with handler triplets ($8E3D x3, $8ECE x3) -- name mapping for 9-16 flagged for re-verification**, 17-23 spells (RESEALO/VELVER/CORBOCK/SHRINK/CARABA/DEFENEE/RAMIPAS), 24-29 event triggers (20 MP each).

---

## Ending/Credits ($BC7F)

11-state machine at $BCA6: credits music ($63) -> scene transitions -> character animations -> story music ($68) -> credits scroll (state 11, 1px/4frames, text from ($0E), $FF-terminated).

---

## Known Dead Code / Cut Content

- **Item 25** ($966A): Full resource restore + zero gold handler. $03E1 flag set by warp but no entity carries item ID 25. Handler unreachable.
- **$A886 entries 14-15** ($2B/$2C): Placeholder spell display entries never indexed (max progression = 13).
