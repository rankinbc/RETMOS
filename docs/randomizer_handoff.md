# RETMOS -> TMOS_Randomizer_V2 Handoff

RE findings answering the randomizer-support questions (REVERSE.md "Randomizer Support" tasks, all closed).
Source of truth: RETMOS/REVERSE.md. Addresses are `bank $cpu-addr`; file offsets given where write-relevant.
Corrections to TMOS_AI/knowledge marked **CORRECTS**.

## 1. Screen-Transition Model (connectivity validator)

The current screen index lives in ZP `$AB`. **Exhaustive sweep: only 8 code sites in the entire ROM write it.**
A world-graph edge exists iff created by mechanisms 1-3; players are injected by 4-5; 6-8 never create links.

| # | Mechanism | Code | Destination source | Randomizer action |
|---|-----------|------|--------------------|-------------------|
| 1 | Edge walk | bank5 $AE4E | WorldScreen nav bytes 4-7 ($FF=wall, $FE=building door) | rewrite nav bytes (already supported) |
| 2 | Stairway / ledge jump | bank5 $AE0B | **Event byte bit6 set -> Content byte = destination screen index**. North Cape "jump" (Event $47) is the same mechanism -- bit6 | rewrite Content when re-indexing screens |
| 3 | Warp / time door | bank6 $8D65 | table `$98C0[$82*8 + door]`, bank6, **file 0x198D0**, 5 chapter-groups x 8 screen indices | patch table entries |
| 4 | Chapter start / respawn | bank4 $8133 | table `$8136[chapter]` = `63 09 01 26 20`, **file 0x10146** -- loaded at EVERY level-start setup ($E282) | patch if these screens move (breaks respawn otherwise) |
| 5 | Password-continue entry | bank1 $8E8A path | see 6; the same routine seeds gameplay after intro | patch |
| 6 | Chapter-intro display screens | bank1 $8E8A | table `$8E92`, **file 0x04EA2**: set A `40 4F 4B 38 68` then set B `1A 01 32 02 34` (toggle $049F); display-only during intro mode $19=8 | keep renderable; patch if moved |
| 7 | Return/restore | bank6 $8127, bank3 $9178 | saved screen `$94` (building exit, post-battle) | automatic, no data |
| 8 | Debug screen browser | bank6 $8B91 | d-pad (up/down +/-16, left/right +/-1) | ignore |

**Zero** immediate `LDA #imm; STA $AB` writes exist. No `$84 <-> $AB` coupling ($84 is chapter progression, independent).

### Present <-> Past
Pure data: destination = `$98C0` lookup. No computed pairing, no ParentWorld derivation.
**CAVEAT**: bank4 $8335 selects past-area music when ParentWorld hi4 >= $E0 -- keep ParentWorld consistent with time period even though it does not drive the pairing.

### Hardcoded screen indices (complete list)
- `$98C0` warp destinations (40B, file 0x198D0)
- `$8136` chapter start/respawn (5B, file 0x10146)
- `$8E92` intro screens (10B, file 0x04EA2)
- bank6 `$90D1`: `CMP #$1A` -- secret event needs screen $1A + player gridpos $68/$69 + magic level 6 (immediate at file 0x190E2)
- chapter-warp data `$BB1F` ($0084 progression values 4,9,14,19,24)

## 2. Content Byte = UI Command (relocation safety)

Building doors (nav byte $FE) reach bank5 $AD34 which passes **Content verbatim** to the bank1 UI engine:
hi3 = mode, lo5 = sub-index (`$04E1`). Handlers key on (chapter group `$82`, Content) -- never on screen index.

| Content | Meaning | Verdict |
|---------|---------|---------|
| $00 | empty | SAFE |
| $01-$1F | wizard battle on entry (param = lo5; uses ExitPosition) | SAFE |
| $20 | first mosque (mode-1 script) | SAFE |
| $21-$2A | boss screens -- mode-1 dialog scripts like the mosque; "phase 1/2" is data convention, **no engine mutation of Content exists** | NEEDS-CARE: keep phase pairs together + chapter progression |
| $40-$5F | universities | SAFE |
| $60-$67 | item shops: **shop id = Content & $1F** -> $94ED table | SAFE |
| $75-$79 | magic/formation shops (chapter-scaled prices) | SAFE |
| $7E/$7F | mosque / troopers | SAFE |
| $80-$9F | NPC scripts = $8B32[$82] + lo5 (chapter-keyed -- same value differs per chapter) | SAFE within chapter; preserve wiseman-before-event order |
| $A0-$BF | hotels/casino/special | SAFE |
| $C0-$DF | time doors (destination from $98C0, NOT from door screen) | NEEDS-PATCH ($98C0) |
| $E0-$FE | special/battle | SAFE |
| any + Event bit6 | stairway: Content = destination screen | rewrite on re-index |

## 3. ExitPosition (WorldScreen byte 9)

Consumer: bank4 $826B via $E086. Format: **hi nibble = X tile column (0-15), lo nibble = Y tile row (0-13)** on the 16px grid; engine adds +8px centering.
Read ONLY on: stairway arrival, entry to Content $01-$1F screens, warp arrival ($8D83), and gridpos-0 fallback. Edge walks never read it.
(**CORRECTS** old consumer list $986C/$A1A1/$A26B -- those were data false positives.)

## 4. Progress Flags $03E0-$03E4

- **Setters**: wiseman scripts via bank2 $BC35 (flag index = $BC56[$82] = `01 03 04 02 00`; special case $82=3 + $04E1=6 -> flag 3); chapter-warp init.
- **Gaters**: 5 VM script IFs ($03E1@$B878, $03E2@$BAF1, $03E3@$B95E/$BB04, $03E4@$BA5B) + world-event items 24-28 (require flag nonzero, then DECREMENT it, then run event: battle / full-restore / screen event / ceremony / magic effect).
- **No other engine readers.** Flags = chapter-story milestones keyed to script group, not screens. Screen shuffling is safe if wiseman screens stay reachable before their dependent event screens.

## 5. Shop Randomization (write spec)

| Structure | File offset | Size | Format |
|-----------|-------------|------|--------|
| Shop-pointer table | 0x054FD | 16B | 8 x u16 LE CPU addr (bank1 window $8000-$BFFF) |
| Shop data | 0x0550D | 64B | 8 shops x 4 slots x [code, price]; fixed 4 slots, no sentinel |
| Magic-shop base prices | 0x04ABC | 11B | binary; effective price = value x (chapter+1) |

- Repointing legal; bank1 free space: **$9731-$98FF (463B zero, file 0x05741)**, $9DD3-$9DFF (45B).
- **Code namespace** (**CORRECTS** any item-ID assumption): codes are bank1 state-command bytes. Legal hi4 only {1,3,5}; $Cx/$Dx are password opcodes writing arbitrary state -- never emit.
  - `$33`=BREAD($0306,cap10), `$34`=MASHROOB($0307,cap10), `$51`=R.SEED($0310,cap5), `$52`=CARPET($0311,cap15), `$53`=HORN(one-time,5 charges), `$58`=RING($030D,cap1)
  - `$10`=**Gortrat-bread heal uses** ($0300, cap9), `$11`=Gortrat mashroob ($0301, cap9). **RESOLVED** (**CORRECTS** knowledge "Key" naming): $0300 is the Gortrat heal-event counter (consumers: walk-on heal bank5 $8A87, +20HP $8BD2); KEY is $0308 only (pickup credit $8BCA, door consume $F2CB). Stock shops never sell keys.
  - **NEW legal codes (unused in stock shops)**: `$18`=KEY ($0308, cap9), `$19`=AMULET ($0309, cap9), `$1A`=MAP ($030A). A randomizer CAN stock shops with keys via code $18. **DANGER**: `$12` targets $0302 = armor level, `$1E`/`$1F` target $030E/$030F = player level / charges -- only emit codes whose target is a real inventory counter.
- **Prices**: 1 byte binary 0-255; gold is 3-digit BCD (0-999) -- keep price x quantity <= 999 for $33/$34; price 0 legal (free); haggle ($A33B) only perturbs a display digit. Magic-shop screens ($75-$79) IGNORE slot price. Shops 4-7 take a different display-price path ($86CF/$86B7 halving) -- verify in-game after moving slots across the 0-3 / 4-7 boundary.
- At-cap purchases abort safely (error $0E, gold not spent).

## 6. Misc verified facts

- Spell MP costs: table at bank6 $98E8 (records +5..+7 BCD); player MP = ZP $8C-$8E BCD. All guide costs confirmed; RESEALO=1, VELVER=2.
- Level-up reward byte ($97EC): bit6=SWORD, bit5=ROD, lo4=spell index -- display only; damage scales from level/equip.
- Formation pairs: bank3 $89C0, pairs (1,10)(4,6)(3,9)(10,11)(7,2)(5,8); 10=Faruk, 1=Coronya, 11=Hassan.
- $030A = MAP flag, gates map overlay (bank4 $8C1E).
- **CORRECTS**: file 0xD544 is the bank3 pickup max-cap table, not shop inventory; shops are flat bank1 tables (0x054FD/0x0550D); bank2 VM drives only dialog/cutscenes/password.

## 7. ObjectSet Spawn Data (**CORRECTS** knowledge/structures/objectset.md)

Parser: bank4 $8686 over the $0400 buffer (block from CHR data bank $82*2+$0E, offset from per-chapter ptr tables at 0x38933+).

| Bytes | Meaning |
|-------|---------|
| `$00` | terminator (confirmed) |
| `$Fn xx` | 2-byte param record: `$05F0+n = xx+$20` (per-screen spawn config -- these are the misread "headers") |
| `tt ss pp` | 3-byte spawn: type -> $0600,X; state -> $0601,X (hi4=direction/flags, lo4=sub-state); **pp = packed grid pos: hi4 = X column, lo4 = Y row (16px grid), engine centers +8px** -- NOT pixel X,Y |

- **Type $06 = door/blocker entity** (ownership-gated visibility: spawn suppressed once the related item is owned -- $03C0 array + progression gates). Sub-state handlers ($81C1 table) are movement/blocking only. **Quest items are NOT given by type-6 entities** -- they are delivered by content-$8x scripts (chapter-keyed; the knowledge NPC tables listing "Rostam Sword"/"Legend Sword" as content codes are those scripts) and by enemy drops (bank3 reward groups $9524 -> inv_pickup $94B0, caps at $9534). Ground-item shuffling = move the content code (see section 2) and keep the matching ObjectSet type-6 sprite with it.
- **$Fn xx param records** feed the per-screen config array $05F0 (+$20): consumed by quest-item appearance/state code (bank6 $921D, rod-gated), battle placement override ($05F5, bank3), text init. Screen-local -- moves safely with the screen if ObjectSet moves too.
- **Types $10-$15 and $19+** are respawn-suppressed enemy classes (kill tracking via $87B6, flags $77/$03F7); types < $10 always spawn.
- Pickup credits: KEY +1 -> $0308 (bank5 $8BCA); Gortrat bread +1 cap 9 -> $0300 ($8C18).
- Position bytes: keep X col 0-15, Y row 0-13 (same rule as ExitPosition).

## 8. Item/Door Gating (logical edges)

- Locked doors: consume KEY $0308 at $F2CB (auto-use, sound $03).
- Oprin doors: Event byte bit5 marks the screen; door entity (type 6) blocks until OPRIN used.
- Wiseman-flag events: items 24-28 need $03E0-$03E4 set (see section 4).
- These gate traversal ORDER only -- they never create or remove graph edges.

## 9. Emulator-Verified Shop Delivery (tools/emu.py, 2026-07-02)

A scriptable emulator now exists in RETMOS (`tools/emu.py`). Unit-mode (`--call 1:8746` with poked RAM) confirmed every delivery path dynamically:

| Code | Result | Verified |
|------|--------|----------|
| $10 | $0300 +1 | YES |
| **$18** | **$0308 KEY +1 -- shop-sellable keys work** | YES |
| $33 (qty=2) | $0306 +2 | YES |
| $10 at cap 9 | purchase aborts, no increment | YES |
| $53 fresh | $0312 = 5 (one-time init, write at $87ED) | YES |
| $53 owned | rejected, zero writes | YES |
| $52 | $0311 increment (write at $87D0) | YES |
| $58 | $030D = 1 | YES |

The emulator also boot-verifies: RESET/MMC1 init, frame sync, controller, title -> chapter intro on Start. Available for any further dynamic checks the randomizer needs.

## 10. ROUND 2 Answers

**ParentWorld (byte 0) is cosmetic + time-period only.** Full reader sweep: every $B0 read is a hi4/lo4 mask -- music variant, palette tint, past-area flag (hi4 >= $E0), RING-teleport lookup ($AAE7), ambient SFX. **None index enemy spawns or encounters** (those come from ObjectSet byte 3 + bank 3 tables). "Biome salad" is mechanically SAFE. Two constraints: keep hi4 >= $E0 consistent with actual PAST screens; if a screen is a RING-teleport target, keep its lo4 in the $AAE7 table.

**Screen indices are CHAPTER-RELATIVE.** read_worldscreen (bank4 $82A1): base set from chapter $82, record = base + $AB*16. The $98C0 warp table and $8136 respawn table hold chapter-relative indices. Matches your reachability model.

**Boss screens ($21-$2A): mode-1 scripts, chapter-locked.** No code range-check; each value runs a chapter-keyed dialog/battle script ($8B32[$82]) with chapter-keyed CHR ($95E8). Rule: pin each boss value to its native chapter; may relocate within the chapter; keep phase-1 screen reachable before phase-2 in progression order. Cross-chapter move loads the wrong script/CHR.

**Stairways: one-way legal, no return needed.** Arrival (bank5 $AE0B) loads the DESTINATION's WorldScreen record and drops the player at the destination's ExitPosition. Destination needs no Event bit6. Sets only $AB + player position -- no progress state. Repoint stairway Content freely; just ensure the destination's ExitPosition is an on-screen tile.

**Wizard battles ($01-$1F): param = Content & $1F** selects a bank 3 encounter (index groups $8019, formations $8460, stats $8341). Chapter-scoped; shuffle within-chapter among $01-$1F, verifying the target encounter exists for that chapter.

**Shops 4-7 price path**: $86A6 `CPY #$04` splits shops 0-3 (direct) vs 4-7. The 4-7 branch only affects quantity-buy display math for BREAD/MASHROOB ($33/$34); flat item slots read [code,price] identically. Moving flat slots across the boundary is safe; re-verify qty-buyable slots if moved to shops 4-7.

## 11. Connectivity Smoke-Test Tool

`tools/emu_walk.py` (loads any .nes) reports per-chapter screen reachability using static edges (nav bytes + stairways + warp table). Because time-door destinations resolve via a dynamic in-engine lookup the static model can't fully follow, vanilla itself has expected "orphans" (past screens). So use **baseline-diff mode**:

```
python tools/emu_walk.py shuffled.nes --baseline TMOS_ORIGINAL.nes
```

Reports only NEW orphans introduced by the shuffle (regressions) -- PASS if none. Verified: self-diff is clean; a deliberately isolated screen is correctly flagged. Drop this in CI to catch shuffles that strand screens.

## Open items (emulator verification recommended)

1. ~~$10/$11 vs KEY~~ RESOLVED + emulator-confirmed: $0300 = Gortrat bread, KEY = $0308, code $18 = shop-sellable KEY.
2. $0310-$0312 charge-slot ITEM NAMES (mechanics confirmed; which HUD/menu name each slot carries needs gameplay observation).
3. Use-table records 9-16 name mapping (costs match BOLTTOR/FLAMOL family, names say SWORD tiers).
4. Shops 4-7 price display path ($86CF).
5. ~~Type-6 lo4 -> item mapping~~ RESOLVED: type-6 = doors/blockers; items come from content-$8x scripts + enemy drops.
