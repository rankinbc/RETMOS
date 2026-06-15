# Dead Ends & Investigation Notes

Read before starting a session. Append when stuck after 10+ tool calls with no progress.

Lifecycle: **Active** -> **Resolved** (prefix with RESOLVED + date once understood) -> delete after 20+ sessions.

## Entry format

## <Subsystem or Function Name>
- **Tried**: what approach was attempted
- **Failed because**: root cause of failure
- **Better approach**: what to do instead
- **Session**: NNN

## Shop buy-loop (concrete item IDs / prices)
- **Tried**: (1) Decoded the bank 2 script VM ($AA1D) fully. (2) Followed bank 1 driver $810D -> master table $8B32 -> 37 scripts in bank 2 $B800-$BFFF; disassembled all via dis_script.py/scan_scripts.py. (3) xref'd $03CC shop flag, entity $36, gold $05C0/$05C1.
- **Failed because**: The 37 bank-1-driven VM scripts are STORY/CUTSCENE events (IF on progress flags $03E0-$03E4), NOT shops -- no NUMINPUT, no item STOREs. $03CC is read only once (bank 6 $81A9) and just advances mode3 state. Gold $05C0/$05C1 writes are all battle-reward/display, no clean shop deduction found. `tools/find_callers.py` referenced in skill does not exist.
- **Better approach**: Shop transaction is likely embedded in DIALOGUE TEXT inline commands ($50-$6F) processed by the text renderer (bank 2 $A3D8 char loop), OR in entity $36 behavior (bank 5 $83BB). Next: (a) disassemble bank 5 $83BB entity $36; (b) decode text inline param handlers $50-$6F in the char-decode loop; (c) item delivery probably reuses inv_pickup_handler (bank 3 $94B0) -- find its non-pickup callers via xref on $94B0.
- **Session**: 004
