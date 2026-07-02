"""
Minimal scriptable NES emulator for TMOS RE verification (Ph5.5).
CPU: Ricoh 2A03 official opcodes (no BCD in ADC/SBC).
Mapper: MMC1 (PRG mode 3 fix-last assumed; serial writes honored).
PPU/APU: register stubs sufficient to boot ($2002 vblank, OAM DMA, no rendering).

Usage:
  python tools/emu.py --dump-regs
  python tools/emu.py --boot-test [N]          # run N instr (default 200000), report state
  python tools/emu.py --trace N                # trace N instructions from RESET
  python tools/emu.py --break ADDR [--max N]   # run until PC==ADDR (hex, e.g. E290)
  python tools/emu.py --frames N               # run N frames (NMI-driven) then dump state
  python tools/emu.py --watch ADDR             # with --frames/--boot-test: log writes to RAM addr (hex)
  python tools/emu.py --poke ADDR=VAL [...]    # set RAM before run
  python tools/emu.py --buttons MASK           # controller byte (A=01 B=02 Sel=04 St=08 U=10 D=20 L=40 R=80)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from instruction_set import OPCODES

ROM_PATH = os.path.join(os.path.dirname(__file__), '..', 'roms', 'TMOS_ORIGINAL.nes')

N_FLAG, V_FLAG, U_FLAG, B_FLAG, D_FLAG, I_FLAG, Z_FLAG, C_FLAG = 0x80,0x40,0x20,0x10,0x08,0x04,0x02,0x01

class MMC1:
    def __init__(self):
        self.shift = 0; self.count = 0
        self.control = 0x0C  # PRG mode 3
        self.chr0 = 0; self.chr1 = 1; self.prg = 0
    def write(self, addr, val):
        if val & 0x80:
            self.shift = 0; self.count = 0; self.control |= 0x0C; return
        self.shift |= (val & 1) << self.count
        self.count += 1
        if self.count == 5:
            reg = (addr >> 13) & 3
            if reg == 0: self.control = self.shift
            elif reg == 1: self.chr0 = self.shift
            elif reg == 2: self.chr1 = self.shift
            else: self.prg = self.shift & 0x0F
            self.shift = 0; self.count = 0

class NES:
    def __init__(self, rom_path=ROM_PATH):
        data = open(rom_path, 'rb').read()
        assert data[:4] == b'NES\x1a'
        prg_units = data[4]
        self.prg = data[16:16 + prg_units*16384]
        self.chr = data[16 + prg_units*16384:]
        self.nbanks = prg_units
        self.ram = bytearray(0x800)
        self.prgram = bytearray(0x2000)
        self.mmc1 = MMC1()
        self.ppu_status_reads = 0
        self.ppu_addr = 0; self.ppu_addr_latch = 0; self.ppu_read_buf = 0
        self.ppu_ctrl = 0; self.ppu_mask = 0
        self.vram = bytearray(0x4000)
        self.oam = bytearray(256)
        self.buttons = 0; self.ctrl_shift = 0; self.ctrl_strobe = 0
        self.in_vblank = False
        self.watch = None; self.watch_log = []
        self.pc_of_write = 0
        # CPU
        self.a = self.x = self.y = 0
        self.sp = 0xFD
        self.p = 0x24
        self.pc = self.read16(0xFFFC)
        self.instr_count = 0
        self.frame = 0
        self.nmi_pending = False
        self.history = [None]*32
        self.press_schedule = []  # (frame, mask, duration)
        self.poke_schedule = []   # (frame, addr, val)

    # ---------- memory ----------
    def prg_bank_base(self, cpu_addr):
        # PRG mode assumed 3 (fix last bank at $C000) -- matches game's init $1F ctrl
        mode = (self.mmc1.control >> 2) & 3
        if cpu_addr >= 0xC000:
            if mode >= 2:
                return (self.nbanks - 1) * 0x4000 if mode == 3 or True else 0
        if mode == 3:
            return (self.mmc1.prg % self.nbanks) * 0x4000 if cpu_addr < 0xC000 else (self.nbanks-1)*0x4000
        if mode == 2:
            return 0 if cpu_addr < 0xC000 else (self.mmc1.prg % self.nbanks)*0x4000
        # 32KB modes
        base = ((self.mmc1.prg >> 1) % (self.nbanks//2)) * 0x8000
        return base + (0 if cpu_addr < 0xC000 else 0x4000)

    def read(self, addr):
        addr &= 0xFFFF
        if addr < 0x2000: return self.ram[addr & 0x7FF]
        if addr < 0x4000:
            reg = 0x2000 + (addr & 7)
            if reg == 0x2002:
                self.ppu_status_reads += 1
                # report vblank periodically so warmup loops exit
                val = 0x80 if (self.in_vblank or self.ppu_status_reads % 3 == 0) else 0x00
                self.ppu_addr_latch = 0
                return val
            if reg == 0x2007:
                off = self.ppu_addr & 0x3FFF
                if off < 0x2000:
                    cur = self.chr[((self.mmc1.chr0 if off < 0x1000 else self.mmc1.chr1)*0x1000 + (off & 0xFFF)) % len(self.chr)]
                else:
                    cur = self.vram[off]
                # real PPU: reads below $3F00 return the internal buffer, then refill
                val = self.ppu_read_buf
                self.ppu_read_buf = cur
                self.ppu_addr = (self.ppu_addr + 1) & 0x3FFF
                return val
            return 0
        if addr == 0x4016:
            val = self.ctrl_shift & 1
            self.ctrl_shift = (self.ctrl_shift >> 1) | 0x80000000  # pad 1s after 8 reads (open bus)
            return val
        if addr == 0x4017: return 0
        if addr < 0x6000: return 0
        if addr < 0x8000: return self.prgram[addr - 0x6000]
        base = self.prg_bank_base(addr)
        return self.prg[base + (addr & 0x3FFF)]

    def read16(self, addr):
        return self.read(addr) | (self.read(addr+1) << 8)

    def write(self, addr, val):
        addr &= 0xFFFF; val &= 0xFF
        if addr < 0x2000:
            if self.watch is not None and (addr & 0x7FF) == self.watch:
                self.watch_log.append((self.instr_count, self.pc_of_write, val))
            self.ram[addr & 0x7FF] = val; return
        if addr < 0x4000:
            reg = 0x2000 + (addr & 7)
            if reg == 0x2000: self.ppu_ctrl = val
            elif reg == 0x2001: self.ppu_mask = val
            if reg == 0x2006:
                if self.ppu_addr_latch == 0:
                    self.ppu_addr = (val << 8) | (self.ppu_addr & 0xFF); self.ppu_addr_latch = 1
                else:
                    self.ppu_addr = (self.ppu_addr & 0xFF00) | val; self.ppu_addr_latch = 0
            elif reg == 0x2007:
                off = self.ppu_addr & 0x3FFF
                if off >= 0x2000: self.vram[off] = val
                self.ppu_addr = (self.ppu_addr + 1) & 0x3FFF
            return
        if addr == 0x4014:
            base = val << 8
            for i in range(256): self.oam[i] = self.read(base + i)
            return
        if addr == 0x4016:
            if self.ctrl_strobe and not (val & 1):
                self.ctrl_shift = self.buttons
            self.ctrl_strobe = val & 1
            if val & 1: self.ctrl_shift = self.buttons
            return
        if addr < 0x6000: return
        if addr < 0x8000: self.prgram[addr - 0x6000] = val; return
        self.mmc1.write(addr, val)

    # ---------- flags ----------
    def setnz(self, v):
        v &= 0xFF
        self.p = (self.p & ~(N_FLAG|Z_FLAG)) | (v & 0x80) | (Z_FLAG if v == 0 else 0)
        return v

    def push(self, v): self.write(0x100 + self.sp, v); self.sp = (self.sp - 1) & 0xFF
    def pop(self):
        self.sp = (self.sp + 1) & 0xFF
        return self.read(0x100 + self.sp)

    # ---------- addressing ----------
    def operand_addr(self, mode):
        pc = self.pc
        if mode == 'IMM': self.pc += 1; return pc
        if mode == 'ZP':  self.pc += 1; return self.read(pc)
        if mode == 'ZPX': self.pc += 1; return (self.read(pc) + self.x) & 0xFF
        if mode == 'ZPY': self.pc += 1; return (self.read(pc) + self.y) & 0xFF
        if mode == 'ABS': self.pc += 2; return self.read16(pc)
        if mode == 'ABX': self.pc += 2; return (self.read16(pc) + self.x) & 0xFFFF
        if mode == 'ABY': self.pc += 2; return (self.read16(pc) + self.y) & 0xFFFF
        if mode == 'IZX':
            self.pc += 1; z = (self.read(pc) + self.x) & 0xFF
            return self.read(z) | (self.read((z+1) & 0xFF) << 8)
        if mode == 'IZY':
            self.pc += 1; z = self.read(pc)
            return ((self.read(z) | (self.read((z+1) & 0xFF) << 8)) + self.y) & 0xFFFF
        if mode == 'IND':
            self.pc += 2; a = self.read16(pc)
            # 6502 page-wrap bug
            lo = self.read(a); hi = self.read((a & 0xFF00) | ((a+1) & 0xFF))
            return lo | (hi << 8)
        if mode == 'REL': self.pc += 1; return pc
        return None

    # ---------- execute ----------
    def step(self):
        op = self.read(self.pc)
        self.pc_of_write = self.pc
        self.history[self.instr_count % 32] = (self.pc, op, self.mmc1.prg, self.a, self.x, self.y)
        info = OPCODES.get(op)
        if info is None:
            print("--- last 32 instructions ---")
            for i in range(32):
                h = self.history[(self.instr_count + 1 + i) % 32]
                if h: print(f"  ${h[0]:04X} op={h[1]:02X} bank={h[2]} A={h[3]:02X} X={h[4]:02X} Y={h[5]:02X}")
            raise RuntimeError(f"illegal opcode ${op:02X} at ${self.pc:04X} bank={self.mmc1.prg} (#{self.instr_count})")
        mn, mode, _, _ = info
        self.pc = (self.pc + 1) & 0xFFFF
        m = mode
        if mn in ('BPL','BMI','BVC','BVS','BCC','BCS','BNE','BEQ'):
            off = self.read(self.pc); self.pc = (self.pc + 1) & 0xFFFF
            if off >= 0x80: off -= 0x100
            take = {
                'BPL': not self.p & N_FLAG, 'BMI': bool(self.p & N_FLAG),
                'BVC': not self.p & V_FLAG, 'BVS': bool(self.p & V_FLAG),
                'BCC': not self.p & C_FLAG, 'BCS': bool(self.p & C_FLAG),
                'BNE': not self.p & Z_FLAG, 'BEQ': bool(self.p & Z_FLAG)}[mn]
            if take: self.pc = (self.pc + off) & 0xFFFF
        elif mn == 'JMP':
            self.pc = self.operand_addr(m) if m == 'IND' else self.read16(self.pc)
        elif mn == 'JSR':
            target = self.read16(self.pc); ret = (self.pc + 1) & 0xFFFF
            self.push(ret >> 8); self.push(ret & 0xFF); self.pc = target
        elif mn == 'RTS':
            lo = self.pop(); hi = self.pop(); self.pc = ((hi << 8) | lo) + 1 & 0xFFFF
        elif mn == 'RTI':
            self.p = (self.pop() | U_FLAG) & ~B_FLAG
            lo = self.pop(); hi = self.pop(); self.pc = (hi << 8) | lo
        elif mn == 'BRK':
            ret = (self.pc + 1) & 0xFFFF
            self.push(ret >> 8); self.push(ret & 0xFF); self.push(self.p | B_FLAG | U_FLAG)
            self.p |= I_FLAG; self.pc = self.read16(0xFFFE)
        elif mn in ('LDA','LDX','LDY'):
            v = self.read(self.operand_addr(m))
            v = self.setnz(v)
            if mn == 'LDA': self.a = v
            elif mn == 'LDX': self.x = v
            else: self.y = v
        elif mn in ('STA','STX','STY'):
            a = self.operand_addr(m)
            self.write(a, {'STA': self.a, 'STX': self.x, 'STY': self.y}[mn])
        elif mn in ('TAX','TAY','TXA','TYA','TSX','TXS'):
            if mn == 'TAX': self.x = self.setnz(self.a)
            elif mn == 'TAY': self.y = self.setnz(self.a)
            elif mn == 'TXA': self.a = self.setnz(self.x)
            elif mn == 'TYA': self.a = self.setnz(self.y)
            elif mn == 'TSX': self.x = self.setnz(self.sp)
            else: self.sp = self.x
        elif mn in ('AND','ORA','EOR'):
            v = self.read(self.operand_addr(m))
            if mn == 'AND': self.a &= v
            elif mn == 'ORA': self.a |= v
            else: self.a ^= v
            self.setnz(self.a)
        elif mn in ('ADC','SBC'):
            v = self.read(self.operand_addr(m))
            if mn == 'SBC': v ^= 0xFF
            r = self.a + v + (self.p & C_FLAG)
            self.p = (self.p & ~(C_FLAG|V_FLAG)) | (C_FLAG if r > 0xFF else 0)
            if (~(self.a ^ v) & (self.a ^ r)) & 0x80: self.p |= V_FLAG
            self.a = self.setnz(r & 0xFF)
        elif mn in ('CMP','CPX','CPY'):
            reg = {'CMP': self.a, 'CPX': self.x, 'CPY': self.y}[mn]
            v = self.read(self.operand_addr(m))
            r = (reg - v) & 0x1FF
            self.p = (self.p & ~C_FLAG) | (C_FLAG if reg >= v else 0)
            self.setnz((reg - v) & 0xFF)
        elif mn in ('ASL','LSR','ROL','ROR'):
            if m == 'ACC':
                v = self.a
            else:
                a = self.operand_addr(m); v = self.read(a)
            c = self.p & C_FLAG
            if mn == 'ASL': nc = v >> 7; v = (v << 1) & 0xFF
            elif mn == 'LSR': nc = v & 1; v >>= 1
            elif mn == 'ROL': nc = v >> 7; v = ((v << 1) | c) & 0xFF
            else: nc = v & 1; v = (v >> 1) | (0x80 if c else 0)
            self.p = (self.p & ~C_FLAG) | (C_FLAG if nc else 0)
            v = self.setnz(v)
            if m == 'ACC': self.a = v
            else: self.write(a, v)
        elif mn in ('INC','DEC'):
            a = self.operand_addr(m); v = self.read(a)
            v = (v + (1 if mn == 'INC' else -1)) & 0xFF
            self.write(a, self.setnz(v))
        elif mn in ('INX','DEX','INY','DEY'):
            if mn == 'INX': self.x = self.setnz((self.x+1) & 0xFF)
            elif mn == 'DEX': self.x = self.setnz((self.x-1) & 0xFF)
            elif mn == 'INY': self.y = self.setnz((self.y+1) & 0xFF)
            else: self.y = self.setnz((self.y-1) & 0xFF)
        elif mn == 'BIT':
            v = self.read(self.operand_addr(m))
            self.p = (self.p & ~(N_FLAG|V_FLAG|Z_FLAG)) | (v & 0xC0) | (Z_FLAG if (v & self.a) == 0 else 0)
        elif mn in ('CLC','SEC','CLI','SEI','CLV','CLD','SED'):
            fl = {'CLC': C_FLAG, 'SEC': C_FLAG, 'CLI': I_FLAG, 'SEI': I_FLAG,
                  'CLV': V_FLAG, 'CLD': D_FLAG, 'SED': D_FLAG}[mn]
            if mn.startswith('CL'): self.p &= ~fl
            else: self.p |= fl
        elif mn == 'PHA': self.push(self.a)
        elif mn == 'PLA': self.a = self.setnz(self.pop())
        elif mn == 'PHP': self.push(self.p | B_FLAG | U_FLAG)
        elif mn == 'PLP': self.p = (self.pop() | U_FLAG) & ~B_FLAG
        elif mn == 'NOP': pass
        else:
            raise RuntimeError(f"unhandled mnemonic {mn} at ${self.pc-1:04X}")
        self.instr_count += 1

    def nmi(self):
        self.push(self.pc >> 8); self.push(self.pc & 0xFF); self.push(self.p | U_FLAG)
        self.p |= I_FLAG
        self.pc = self.read16(0xFFFA)
        self.frame += 1
        if self.press_schedule:
            self.buttons = 0
            for fr, mask, dur in self.press_schedule:
                if fr <= self.frame < fr + dur:
                    self.buttons |= mask
        for fr, addr, val in self.poke_schedule:
            if fr == self.frame:
                self.ram[addr & 0x7FF] = val

    def run(self, max_instr=200000, break_at=None, trace=0, nmi_every=6000, labels=None):
        """NMI fires only while the CPU sits in a frame-sync spin loop, mirroring real
        vblank timing (game logic is never interrupted mid-dispatch). Spin loops:
        $F24C-$F250 (nmi_spin_wait LDA $1C/BPL) and PPU $2002 warmup polls."""
        next_nmi = nmi_every
        starved = 0
        while self.instr_count < max_instr:
            if break_at is not None and self.pc == break_at:
                return 'break'
            if trace and self.instr_count < trace:
                nm = labels.get(self.pc, '') if labels else ''
                print(f"#{self.instr_count:6d} ${self.pc:04X} A={self.a:02X} X={self.x:02X} Y={self.y:02X} P={self.p:02X} SP={self.sp:02X} bank={self.mmc1.prg} {nm}")
            self.step()
            if self.instr_count >= next_nmi:
                in_spin = 0xF24C <= self.pc <= 0xF252
                starved += 1
                # NMI at frame budget, but never mid MMC1 serial write (count!=0) --
                # an interrupt there corrupts the shift sequence. Prefer the spin loop;
                # fall back to any safe point after a short grace period.
                if (in_spin or starved > 50) and self.mmc1.count == 0:
                    self.in_vblank = True
                    self.nmi()
                    self.in_vblank = False
                    next_nmi = self.instr_count + nmi_every
                    starved = 0
        return 'max'

# NES master palette (Nestopia NTSC)
NES_PAL = [
    (0x66,0x66,0x66),(0x00,0x2A,0x88),(0x14,0x12,0xA7),(0x3B,0x00,0xA4),(0x5C,0x00,0x7E),(0x6E,0x00,0x40),(0x6C,0x06,0x00),(0x56,0x1D,0x00),
    (0x33,0x35,0x00),(0x0B,0x48,0x00),(0x00,0x52,0x00),(0x00,0x4F,0x08),(0x00,0x40,0x4D),(0x00,0x00,0x00),(0x00,0x00,0x00),(0x00,0x00,0x00),
    (0xAD,0xAD,0xAD),(0x15,0x5F,0xD9),(0x42,0x40,0xFF),(0x75,0x27,0xFE),(0xA0,0x1A,0xCC),(0xB7,0x1E,0x7B),(0xB5,0x31,0x20),(0x99,0x4E,0x00),
    (0x6B,0x6D,0x00),(0x38,0x87,0x00),(0x0C,0x93,0x00),(0x00,0x8F,0x32),(0x00,0x7C,0x8D),(0x00,0x00,0x00),(0x00,0x00,0x00),(0x00,0x00,0x00),
    (0xFF,0xFE,0xFF),(0x64,0xB0,0xFF),(0x92,0x90,0xFF),(0xC6,0x76,0xFF),(0xF3,0x6A,0xFF),(0xFE,0x6E,0xCC),(0xFE,0x81,0x70),(0xEA,0x9E,0x22),
    (0xBC,0xBE,0x00),(0x88,0xD8,0x00),(0x5C,0xE4,0x30),(0x45,0xE0,0x82),(0x48,0xCD,0xDE),(0x4F,0x4F,0x4F),(0x00,0x00,0x00),(0x00,0x00,0x00),
    (0xFF,0xFE,0xFF),(0xC0,0xDF,0xFF),(0xD3,0xD2,0xFF),(0xE8,0xC8,0xFF),(0xFB,0xC2,0xFF),(0xFE,0xC4,0xEA),(0xFE,0xCC,0xC5),(0xF7,0xD8,0xA5),
    (0xE4,0xE5,0x94),(0xCF,0xEF,0x96),(0xBD,0xF4,0xAB),(0xB3,0xF3,0xCC),(0xB5,0xEB,0xF2),(0xB8,0xB8,0xB8),(0x00,0x00,0x00),(0x00,0x00,0x00),
]

def render_screen(n, path):
    """Composite BG (nametable 0) + sprites to a PNG using current PPU state."""
    from PIL import Image
    img = Image.new('RGB', (256, 240))
    px = img.load()
    def chr_byte(pattern_addr):
        bank = n.mmc1.chr0 if pattern_addr < 0x1000 else n.mmc1.chr1
        return n.chr[(bank*0x1000 + (pattern_addr & 0xFFF)) % len(n.chr)]
    def pal_color(idx):
        e = n.vram[0x3F00 + idx] & 0x3F
        return NES_PAL[e]
    bg_base = 0x1000 if n.ppu_ctrl & 0x10 else 0x0000
    # background
    for row in range(30):
        for col in range(32):
            tile = n.vram[0x2000 + row*32 + col]
            at = n.vram[0x23C0 + (row//4)*8 + (col//4)]
            shift = ((row % 4)//2)*4 + ((col % 4)//2)*2
            palgrp = (at >> shift) & 3
            base = bg_base + tile*16
            for y in range(8):
                p0 = chr_byte(base + y); p1 = chr_byte(base + y + 8)
                for x in range(8):
                    b = 7 - x
                    c = ((p0 >> b) & 1) | (((p1 >> b) & 1) << 1)
                    idx = 0 if c == 0 else palgrp*4 + c
                    px[col*8+x, row*8+y] = pal_color(idx)
    # sprites (front-to-back: draw 63..0 so sprite 0 wins overlaps)
    tall = bool(n.ppu_ctrl & 0x20)
    sp_base = 0x1000 if n.ppu_ctrl & 0x08 else 0x0000
    for i in range(63, -1, -1):
        sy, tile, attr, sx = n.oam[i*4:i*4+4]
        if sy >= 0xEF: continue
        sy += 1
        hflip, vflip = attr & 0x40, attr & 0x80
        palgrp = attr & 3
        height = 16 if tall else 8
        for y in range(height):
            yy = (height-1-y) if vflip else y
            if tall:
                t = (tile & 0xFE) + (1 if yy >= 8 else 0)
                base = (0x1000 if tile & 1 else 0x0000) + t*16 + (yy & 7)
            else:
                base = sp_base + tile*16 + yy
            p0 = chr_byte(base); p1 = chr_byte(base + 8)
            for x in range(8):
                b = x if hflip else 7 - x
                c = ((p0 >> b) & 1) | (((p1 >> b) & 1) << 1)
                if c == 0: continue
                X, Y = sx + x, sy + y
                if X < 256 and Y < 240:
                    px[X, Y] = pal_color(0x10 + palgrp*4 + c)
    img.save(path)
    print(f"screen -> {path} (ctrl={n.ppu_ctrl:02X} mask={n.ppu_mask:02X} chr={n.mmc1.chr0}/{n.mmc1.chr1})")

def load_labels():
    labels = {}
    path = os.path.join(os.path.dirname(__file__), '..', 'labels.csv')
    try:
        for line in open(path, encoding='utf-8'):
            parts = line.strip().split(',')
            if len(parts) >= 3 and parts[0] == '7':
                try: labels[int(parts[1], 16)] = parts[2]
                except ValueError: pass
    except OSError: pass
    return labels

def dump_state(n):
    print(f"PC=${n.pc:04X} A={n.a:02X} X={n.x:02X} Y={n.y:02X} P={n.p:02X} SP={n.sp:02X}")
    print(f"instr={n.instr_count} frames={n.frame} PRG bank={n.mmc1.prg} CHR={n.mmc1.chr0}/{n.mmc1.chr1} ctrl={n.mmc1.control:02X}")
    z = n.ram
    print(f"mode $19={z[0x19]:02X} $1A={z[0x1A]:02X} $80={z[0x80]:02X} screen $AB={z[0xAB]:02X} pos $84={z[0x84]:02X}")
    print(f"HP $81={z[0x81]:02X} maxHP $91={z[0x91]:02X} MP $8C-$8E={z[0x8C]:X}{z[0x8D]:X}{z[0x8E]:X} chapter $89={z[0x89]:02X}")
    print(f"$0300-$030F: {' '.join(f'{n.ram[0x300+i]:02X}' for i in range(16))}")

def main():
    args = sys.argv[1:]
    n = NES()
    def getflag(name, default=None):
        if name in args:
            i = args.index(name)
            if i+1 < len(args) and not args[i+1].startswith('--'):
                return args[i+1]
            return True
        return default
    for a in args:
        if a.startswith('--poke') and '=' in a: pass
    # pokes
    if '--poke' in args:
        for a in args[args.index('--poke')+1:]:
            if a.startswith('--'): break
            addr, val = a.split('=')
            n.ram[int(addr, 16) & 0x7FF] = int(val, 16)
    if '--watch' in args: n.watch = int(getflag('--watch'), 16) & 0x7FF
    if '--buttons' in args: n.buttons = int(getflag('--buttons'), 16)
    if '--pokeat' in args:
        # --pokeat 7000:030F=03,7000:0310=07
        for spec in getflag('--pokeat').split(','):
            fr_s, assign = spec.split(':', 1)
            addr, val = assign.split('=')
            n.poke_schedule.append((int(fr_s), int(addr, 16), int(val, 16)))
    if '--press' in args:
        # --press 300:08,360:08 or 300:08:10 (frame:mask[:duration])
        for spec in getflag('--press').split(','):
            parts = spec.split(':')
            fr, mask = int(parts[0]), int(parts[1], 16)
            dur = int(parts[2]) if len(parts) > 2 else 5
            n.press_schedule.append((fr, mask, dur))
    labels = load_labels()

    if '--dump-regs' in args:
        dump_state(n); return
    if '--call' in args:
        # --call BANK:ADDR [--a XX] -- run one routine to completion (unit test mode)
        bank_s, addr_s = getflag('--call').split(':')
        n.mmc1.prg = int(bank_s)
        n.mmc1.control = 0x1F
        target = int(addr_s, 16)
        SENT = 0x4020  # open-bus sentinel return address
        n.sp = 0xFD
        n.push((SENT - 1) >> 8); n.push((SENT - 1) & 0xFF)
        n.pc = target
        if '--a' in args: n.a = int(getflag('--a'), 16)
        n.ram[0x39] = n.mmc1.prg  # NMI restores PRG from $39
        mx = int(getflag('--max', '500000'))
        r = n.run(max_instr=mx, break_at=SENT)
        print(f"result={r} ({'returned' if r=='break' else 'no return'})")
        dump_state(n)
        if n.watch is not None:
            print(f"watch ${n.watch:03X} writes: {len(n.watch_log)}")
            for ic, pc, v in n.watch_log[:20]:
                print(f"  #{ic} pc=${pc:04X} val={v:02X}")
        return
    if '--trace' in args:
        cnt = int(getflag('--trace', '200'))
        n.run(max_instr=cnt, trace=cnt, labels=labels); dump_state(n); return
    if '--break' in args:
        target = int(getflag('--break'), 16)
        mx = int(getflag('--max', '2000000'))
        r = n.run(max_instr=mx, break_at=target)
        print(f"result={r}")
        dump_state(n); return
    if '--frames' in args:
        fr = int(getflag('--frames', '60'))
        n.run(max_instr=fr*6000 + 5000)
        dump_state(n)
    else:
        cnt = int(getflag('--boot-test', '200000') or '200000')
        n.run(max_instr=cnt)
        dump_state(n)
    if n.watch is not None:
        print(f"watch ${n.watch:03X} writes: {len(n.watch_log)}")
        for ic, pc, v in n.watch_log[:20]:
            print(f"  #{ic} pc=${pc:04X} val={v:02X}")
    if '--dump-screen' in args:
        render_screen(n, getflag('--dump-screen'))

if __name__ == '__main__':
    main()
