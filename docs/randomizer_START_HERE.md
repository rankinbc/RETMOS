# RETMOS reverse-engineering — latest info for TMOS_Randomizer_V2

As of 2026-07-02. Start here, in order.

## 1. randomizer_handoff.md (curated answer sheet)
Copied into the randomizer project root (also at `RETMOS/docs/randomizer_handoff.md`). Written for the randomizer, not a raw RE dump: screen-transition model, ParentWorld findings, boss/stairway/wizard rules, shop write spec, ObjectSet format, emulator-verified sections. Read this first.

## 2. tools/emu_walk.py (connectivity smoke-test)
In the RETMOS repo. Baseline-diff a shuffled ROM against vanilla:

```
python tools/emu_walk.py shuffled.nes --baseline TMOS_ORIGINAL.nes
```

PASS = no new orphans; FAIL lists screens the shuffle stranded. Static model (nav + stairway + warp table) can't follow dynamic time-door lookups, so vanilla has expected orphans — that's why you diff, not assert absolute reachability. Drop it in CI.

## 3. RETMOS repo — full detail
`github.com/rankinbc/RETMOS`, branch `master`. Source of truth is `REVERSE.md`. Randomizer-relevant sections:
- **"ParentWorld FULL reader sweep"** — biome salad is cosmetic-safe (ParentWorld drives music/palette/past-flag/RING-teleport/SFX, never spawns)
- **"Complete Screen-Transition Inventory"** — all 8 ways `$AB` (screen index) changes
- **"Boss Screens Content $21-$2A"**, **"Stairway Semantics Deep-Dive"**, **"Wizard-battle Content $01-$1F"**
- **"Shop Tables WRITE Spec"** + **"Shop-Code -> Item Mapping"** — file offsets, legal codes, `$18` = shop-sellable KEY
- **"ObjectSet Spawn-Data Format"** — corrects the old knowledge-base entry ([type, state, packed grid pos], NOT [type, X-px, Y-px])

## Headline takeaways for connectivity work
- Screen indices are **chapter-relative** (matches the reachability model).
- Only **3 hardcoded screen tables** in the whole ROM: warp/time-door `$98C0`, respawn `$8136`, continue/intro `$8E92`. Patch these when moving their target screens.
- **Stairways are freely repointable** — one-way legal, destination needs no return stair.
- **Content byte = UI command, verbatim** — shops/NPCs/bosses key on (chapter, Content), never on screen index.

## Corrections to existing knowledge/ docs (flagged inline in the handoff)
- ObjectSet entry format ([type, state, packed grid pos]).
- Shop "Key" slot naming — it's Gortrat bread; real keys are code `$18` -> `$0308`.
- The `0xD544` "shop table" claim — it's the pickup max-cap table, not shops.

## Still open (does not block current work)
- In-game HUD item names for charge slots `$0310-$0312`.
- A couple of use-table record names.
All cosmetic; none affect placement/connectivity logic.
