# Dead Ends & Investigation Notes

Read before starting a session. Append when stuck after 10+ tool calls with no progress.

Lifecycle: **Active** -> **Resolved** (prefix with RESOLVED + date once understood) -> delete after 20+ sessions.

## Entry format

## <Subsystem or Function Name>
- **Tried**: what approach was attempted
- **Failed because**: root cause of failure
- **Better approach**: what to do instead
- **Session**: NNN

## RESOLVED 2026-06-15: Shop buy-loop (concrete item IDs / prices)
- **Tried**: (1) Decoded the bank 2 script VM ($AA1D) fully. (2) Followed bank 1 driver $810D -> master table $8B32 -> 37 scripts in bank 2 $B800-$BFFF; disassembled all via dis_script.py/scan_scripts.py. (3) xref'd $03CC shop flag, entity $36, gold $05C0/$05C1.
- **Why the VM was a red herring**: The 37 bank-1-driven VM scripts are STORY/CUTSCENE events (IF on progress flags $03E0-$03E4), not shops. The bank 2 VM is real but only drives cutscene/dialogue/password.
- **RESOLUTION**: Shops are **flat tables in bank 1**, not bytecode. Shop-pointer table $94ED (8 shops x ptr16, indexed by $04E1) -> shop data $94FD (4 slots x [code, price]). Read at $8680 -> $04D5/$04D6. Pipeline: $A5A0 (price*qty) -> $A33B (haggle BCD) -> $8A71 (magic-shop chapter scaling) -> $A736 (gold spend -> $EBDD). Verified vs ROM. Documented in REVERSE.md "Shop Inventory & Pricing (bank 1)". Also corrects the old $D544 claim.
- **Note**: `tools/find_callers.py` referenced in skill does not exist (use xref.py).
- **Session**: 004
