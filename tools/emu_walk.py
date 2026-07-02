"""
Randomizer smoke-test: WorldScreen connectivity checker for an arbitrary TMOS .nes.

Reads the WorldScreen nav bytes (edges) directly from the ROM's CHR-ROM screen
tables and reports, per chapter:
  - each screen's 4 directional links (right/left/down/up) with $FF=wall, $FE=building
  - reachability from the chapter start screen (BFS over walkable edges)
  - orphan screens (unreachable) and dangling links (point outside the chapter range)

This validates a randomized ROM's graph without needing full emulation. For dynamic
in-engine confirmation, pair with tools/emu.py --poke $AB=N + --press d-pad.

Usage:
  python tools/emu_walk.py <rom.nes> [chapter 1-5 | all]

WorldScreen record = 16 bytes; bytes 4-7 = right/left/down/up screen index.
Chapter tables (file offsets) and counts are the ROM-verified values from REVERSE.md.
"""
import sys

# (file offset of chapter's WorldScreen table, screen count) -- from REVERSE.md
CHAPTERS = {
    1: (0x39695, 131),
    2: (0x39EC5, 137),
    3: (0x3A755, 153),
    4: (0x3B0E5, 164),
    5: (0x3BB25, 154),
}
# chapter start screen (relative index) from bank 4 $8136 respawn table
START = {1: 0x63, 2: 0x09, 3: 0x01, 4: 0x26, 5: 0x20}
DIRS = ['right', 'left', 'down', 'up']

def load(path):
    with open(path, 'rb') as f:
        return f.read()

WARP_TABLE = 0x198D0  # bank 6 $98C0: 5 chapter-groups x 8 destination screen indices

def screen_rec(rom, base, idx):
    o = base + idx*16
    return rom[o:o+16]

def check_chapter(rom, ch):
    base, count = CHAPTERS[ch]
    start = START[ch]
    # build adjacency: nav-byte edges + stairway (Event bit6 -> Content=dest) + warps
    adj = {}
    dangling = []
    stair_edges = 0
    for s in range(count):
        rec = screen_rec(rom, base, s)
        content, event = rec[2], rec[15]
        links = []
        for d, v in zip(DIRS, rec[4:8]):
            if v in (0xFF, 0xFE):   # wall / building door
                continue
            if v >= count:
                dangling.append((s, d, v))
                continue
            links.append(v)
        # stairway edge: Event bit6 set -> Content is destination screen index
        if event & 0x40 and content < count:
            links.append(content)
            stair_edges += 1
        adj[s] = links
    # warp destinations for this chapter (time doors) -- add as reachable anchors
    warp_dests = [rom[WARP_TABLE + (ch-1)*8 + i] for i in range(8)]
    warp_dests = [w for w in warp_dests if 0 < w < count]
    # BFS from start + warp anchors (time-door destinations are reachable roots)
    seen = set()
    stack = ([start] if start < count else []) + warp_dests
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        for nx in adj.get(n, []):
            if nx not in seen:
                stack.append(nx)
    orphans = [s for s in range(count) if s not in seen]
    return count, len(seen), orphans, dangling, start, stair_edges

def chapter_orphans(rom):
    """Return {chapter: set(orphan indices)} using static nav+stairway+warp edges."""
    out = {}
    for ch in range(1, 6):
        _, _, orphans, _, _, _ = check_chapter(rom, ch)
        out[ch] = set(orphans)
    return out

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    rom = load(sys.argv[1])
    args = sys.argv[2:]

    # Baseline-diff mode: `emu_walk.py shuffled.nes --baseline vanilla.nes`
    # Static edges (nav+stairway+warp-table) can't resolve dynamic time-door lookups,
    # so absolute connectivity has expected orphans even on vanilla. The USEFUL signal
    # for a randomizer is: does the shuffle create NEW orphans vs the vanilla baseline?
    if '--baseline' in args:
        base_rom = load(args[args.index('--baseline')+1])
        base = chapter_orphans(base_rom)
        cur = chapter_orphans(rom)
        regressions = 0
        for ch in range(1, 6):
            new = cur[ch] - base[ch]
            fixed = base[ch] - cur[ch]
            status = 'PASS' if not new else 'FAIL'
            print(f"Chapter {ch}: baseline_orphans={len(base[ch])} now={len(cur[ch])} "
                  f"new={len(new)} [{status}]")
            if new:
                regressions += len(new)
                print("  NEW orphans (regressions): " + ' '.join(f'${s:02X}' for s in sorted(new)))
            if fixed:
                print("  now-reachable: " + ' '.join(f'${s:02X}' for s in sorted(fixed)))
        print(f"\nOVERALL: {'PASS - no new orphans' if regressions == 0 else f'FAIL - {regressions} new orphans'}")
        return

    # Report mode: static reachability per chapter (baseline for later diffs)
    which = args[0] if args else 'all'
    chapters = range(1, 6) if which == 'all' else [int(which)]
    for ch in chapters:
        count, reached, orphans, dangling, start, stairs = check_chapter(rom, ch)
        print(f"\n=== Chapter {ch} === start=${start:02X} screens={count} reached={reached} stairs={stairs}")
        print(f"  static-orphans ({len(orphans)}): " + ' '.join(f'${s:02X}' for s in orphans[:60]))
        if dangling:
            print(f"  dangling links ({len(dangling)}): "
                  + ' '.join(f'${s:02X}:{d}->${v:02X}' for s, d, v in dangling[:12]))
    print("\nNote: static model omits dynamic time-door lookups, so vanilla has expected"
          "\norphans (past screens reached via in-engine door dispatch). Use --baseline"
          "\n<vanilla.nes> to flag only NEW orphans introduced by a shuffle.")

if __name__ == '__main__':
    main()
