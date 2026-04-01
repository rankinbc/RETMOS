# RETMOS - The Magic of Scheherazade (NES) Reverse Engineering Project

## Platform
- **Target**: NES (Nintendo Entertainment System)
- **CPU**: Ricoh 2A03 (MOS 6502 variant, no BCD mode)
- **Mapper**: MMC1 (iNES mapper 1)
- **ROM**: `roms/TMOS_ORIGINAL.nes` (256KB: 128KB PRG + 128KB CHR)

## Address Notation
- NES banked ROM: `bank,addr` where addr is hex without prefix
- labels.csv format: `bank,addr,name,comment`
- WRAM/HRAM labels use `bank='*'`
- CPU addresses: `$XXXX` notation in documentation
- File offsets: `0xXXXXX` notation

## Tool Rules
- All RE tools live in `tools/` -- invoke as `python3 tools/<tool>.py`
- Use Read (not cat), Grep (not grep), Glob (not ls/find)
- Write .py files first, never inline `python3 -c`
- No third-party disassemblers (no radare2, Ghidra, ndisasm)
- All tools auto-load labels.csv for annotation

## Key Files
- `REVERSE.md` -- main findings, data-range map, task list
- `labels.csv` -- accumulated address labels (grows across sessions)
- `dead_ends.md` -- stuck log to avoid repeating failed approaches
- `tools/` -- all RE tooling
- `gfx/` -- extracted graphics
- `web/` -- web port (plain HTML+JS, no build tools)
- `docs/` -- architecture documentation

## Session Protocol
- Pick top unchecked task from REVERSE.md ## Next Tasks
- Write findings immediately after every 2-3 tool calls (don't batch)
- Mark tasks [x] when done, add new [ ] discoveries
- End with SESSION_SUMMARY: one-liner
