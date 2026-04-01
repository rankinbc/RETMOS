"""
Ricoh 2A03 (MOS 6502 variant) opcode database.
No BCD mode (SED exists but ADC/SBC ignore decimal flag).

Each entry: opcode -> (mnemonic, addressing_mode, bytes, cycles)

Addressing modes:
  IMP  - Implied
  ACC  - Accumulator
  IMM  - Immediate (#$nn)
  ZP   - Zero Page ($nn)
  ZPX  - Zero Page,X ($nn,X)
  ZPY  - Zero Page,Y ($nn,Y)
  ABS  - Absolute ($nnnn)
  ABX  - Absolute,X ($nnnn,X)
  ABY  - Absolute,Y ($nnnn,Y)
  IND  - Indirect (($nnnn))
  IZX  - Indexed Indirect (($nn,X))
  IZY  - Indirect Indexed (($nn),Y)
  REL  - Relative ($nn)  -- branch offset
"""

# (mnemonic, mode, bytes, cycles)
OPCODES = {
    # BRK
    0x00: ("BRK", "IMP", 1, 7),
    # ORA
    0x01: ("ORA", "IZX", 2, 6),
    0x05: ("ORA", "ZP",  2, 3),
    0x09: ("ORA", "IMM", 2, 2),
    0x0D: ("ORA", "ABS", 3, 4),
    0x11: ("ORA", "IZY", 2, 5),
    0x15: ("ORA", "ZPX", 2, 4),
    0x19: ("ORA", "ABY", 3, 4),
    0x1D: ("ORA", "ABX", 3, 4),
    # ASL
    0x06: ("ASL", "ZP",  2, 5),
    0x0A: ("ASL", "ACC", 1, 2),
    0x0E: ("ASL", "ABS", 3, 6),
    0x16: ("ASL", "ZPX", 2, 6),
    0x1E: ("ASL", "ABX", 3, 7),
    # PHP/PLP/PHA/PLA
    0x08: ("PHP", "IMP", 1, 3),
    0x28: ("PLP", "IMP", 1, 4),
    0x48: ("PHA", "IMP", 1, 3),
    0x68: ("PLA", "IMP", 1, 4),
    # Branch instructions
    0x10: ("BPL", "REL", 2, 2),
    0x30: ("BMI", "REL", 2, 2),
    0x50: ("BVC", "REL", 2, 2),
    0x70: ("BVS", "REL", 2, 2),
    0x90: ("BCC", "REL", 2, 2),
    0xB0: ("BCS", "REL", 2, 2),
    0xD0: ("BNE", "REL", 2, 2),
    0xF0: ("BEQ", "REL", 2, 2),
    # CLC/SEC/CLI/SEI/CLV/CLD/SED
    0x18: ("CLC", "IMP", 1, 2),
    0x38: ("SEC", "IMP", 1, 2),
    0x58: ("CLI", "IMP", 1, 2),
    0x78: ("SEI", "IMP", 1, 2),
    0xB8: ("CLV", "IMP", 1, 2),
    0xD8: ("CLD", "IMP", 1, 2),
    0xF8: ("SED", "IMP", 1, 2),
    # JSR / RTS / RTI
    0x20: ("JSR", "ABS", 3, 6),
    0x60: ("RTS", "IMP", 1, 6),
    0x40: ("RTI", "IMP", 1, 6),
    # JMP
    0x4C: ("JMP", "ABS", 3, 3),
    0x6C: ("JMP", "IND", 3, 5),
    # AND
    0x21: ("AND", "IZX", 2, 6),
    0x25: ("AND", "ZP",  2, 3),
    0x29: ("AND", "IMM", 2, 2),
    0x2D: ("AND", "ABS", 3, 4),
    0x31: ("AND", "IZY", 2, 5),
    0x35: ("AND", "ZPX", 2, 4),
    0x39: ("AND", "ABY", 3, 4),
    0x3D: ("AND", "ABX", 3, 4),
    # BIT
    0x24: ("BIT", "ZP",  2, 3),
    0x2C: ("BIT", "ABS", 3, 4),
    # ROL
    0x26: ("ROL", "ZP",  2, 5),
    0x2A: ("ROL", "ACC", 1, 2),
    0x2E: ("ROL", "ABS", 3, 6),
    0x36: ("ROL", "ZPX", 2, 6),
    0x3E: ("ROL", "ABX", 3, 7),
    # EOR
    0x41: ("EOR", "IZX", 2, 6),
    0x45: ("EOR", "ZP",  2, 3),
    0x49: ("EOR", "IMM", 2, 2),
    0x4D: ("EOR", "ABS", 3, 4),
    0x51: ("EOR", "IZY", 2, 5),
    0x55: ("EOR", "ZPX", 2, 4),
    0x59: ("EOR", "ABY", 3, 4),
    0x5D: ("EOR", "ABX", 3, 4),
    # LSR
    0x46: ("LSR", "ZP",  2, 5),
    0x4A: ("LSR", "ACC", 1, 2),
    0x4E: ("LSR", "ABS", 3, 6),
    0x56: ("LSR", "ZPX", 2, 6),
    0x5E: ("LSR", "ABX", 3, 7),
    # ADC
    0x61: ("ADC", "IZX", 2, 6),
    0x65: ("ADC", "ZP",  2, 3),
    0x69: ("ADC", "IMM", 2, 2),
    0x6D: ("ADC", "ABS", 3, 4),
    0x71: ("ADC", "IZY", 2, 5),
    0x75: ("ADC", "ZPX", 2, 4),
    0x79: ("ADC", "ABY", 3, 4),
    0x7D: ("ADC", "ABX", 3, 4),
    # ROR
    0x66: ("ROR", "ZP",  2, 5),
    0x6A: ("ROR", "ACC", 1, 2),
    0x6E: ("ROR", "ABS", 3, 6),
    0x76: ("ROR", "ZPX", 2, 6),
    0x7E: ("ROR", "ABX", 3, 7),
    # STA
    0x81: ("STA", "IZX", 2, 6),
    0x85: ("STA", "ZP",  2, 3),
    0x8D: ("STA", "ABS", 3, 4),
    0x91: ("STA", "IZY", 2, 6),
    0x95: ("STA", "ZPX", 2, 4),
    0x99: ("STA", "ABY", 3, 5),
    0x9D: ("STA", "ABX", 3, 5),
    # STX
    0x86: ("STX", "ZP",  2, 3),
    0x8E: ("STX", "ABS", 3, 4),
    0x96: ("STX", "ZPY", 2, 4),
    # STY
    0x84: ("STY", "ZP",  2, 3),
    0x8C: ("STY", "ABS", 3, 4),
    0x94: ("STY", "ZPX", 2, 4),
    # LDA
    0xA1: ("LDA", "IZX", 2, 6),
    0xA5: ("LDA", "ZP",  2, 3),
    0xA9: ("LDA", "IMM", 2, 2),
    0xAD: ("LDA", "ABS", 3, 4),
    0xB1: ("LDA", "IZY", 2, 5),
    0xB5: ("LDA", "ZPX", 2, 4),
    0xB9: ("LDA", "ABY", 3, 4),
    0xBD: ("LDA", "ABX", 3, 4),
    # LDX
    0xA2: ("LDX", "IMM", 2, 2),
    0xA6: ("LDX", "ZP",  2, 3),
    0xAE: ("LDX", "ABS", 3, 4),
    0xB6: ("LDX", "ZPY", 2, 4),
    0xBE: ("LDX", "ABY", 3, 4),
    # LDY
    0xA0: ("LDY", "IMM", 2, 2),
    0xA4: ("LDY", "ZP",  2, 3),
    0xAC: ("LDY", "ABS", 3, 4),
    0xB4: ("LDY", "ZPX", 2, 4),
    0xBC: ("LDY", "ABX", 3, 4),
    # CMP
    0xC1: ("CMP", "IZX", 2, 6),
    0xC5: ("CMP", "ZP",  2, 3),
    0xC9: ("CMP", "IMM", 2, 2),
    0xCD: ("CMP", "ABS", 3, 4),
    0xD1: ("CMP", "IZY", 2, 5),
    0xD5: ("CMP", "ZPX", 2, 4),
    0xD9: ("CMP", "ABY", 3, 4),
    0xDD: ("CMP", "ABX", 3, 4),
    # CPX
    0xE0: ("CPX", "IMM", 2, 2),
    0xE4: ("CPX", "ZP",  2, 3),
    0xEC: ("CPX", "ABS", 3, 4),
    # CPY
    0xC0: ("CPY", "IMM", 2, 2),
    0xC4: ("CPY", "ZP",  2, 3),
    0xCC: ("CPY", "ABS", 3, 4),
    # DEC
    0xC6: ("DEC", "ZP",  2, 5),
    0xCE: ("DEC", "ABS", 3, 6),
    0xD6: ("DEC", "ZPX", 2, 6),
    0xDE: ("DEC", "ABX", 3, 7),
    # INC
    0xE6: ("INC", "ZP",  2, 5),
    0xEE: ("INC", "ABS", 3, 6),
    0xF6: ("INC", "ZPX", 2, 6),
    0xFE: ("INC", "ABX", 3, 7),
    # SBC
    0xE1: ("SBC", "IZX", 2, 6),
    0xE5: ("SBC", "ZP",  2, 3),
    0xE9: ("SBC", "IMM", 2, 2),
    0xED: ("SBC", "ABS", 3, 4),
    0xF1: ("SBC", "IZY", 2, 5),
    0xF5: ("SBC", "ZPX", 2, 4),
    0xF9: ("SBC", "ABY", 3, 4),
    0xFD: ("SBC", "ABX", 3, 4),
    # Transfer instructions
    0xAA: ("TAX", "IMP", 1, 2),
    0xA8: ("TAY", "IMP", 1, 2),
    0x8A: ("TXA", "IMP", 1, 2),
    0x98: ("TYA", "IMP", 1, 2),
    0xBA: ("TSX", "IMP", 1, 2),
    0x9A: ("TXS", "IMP", 1, 2),
    # DEX/DEY/INX/INY
    0xCA: ("DEX", "IMP", 1, 2),
    0x88: ("DEY", "IMP", 1, 2),
    0xE8: ("INX", "IMP", 1, 2),
    0xC8: ("INY", "IMP", 1, 2),
    # NOP
    0xEA: ("NOP", "IMP", 1, 2),
}

# Addressing mode operand size (bytes after opcode)
MODE_OPERAND_SIZE = {
    "IMP": 0, "ACC": 0, "IMM": 1, "ZP": 1, "ZPX": 1, "ZPY": 1,
    "ABS": 2, "ABX": 2, "ABY": 2, "IND": 2, "IZX": 1, "IZY": 1,
    "REL": 1,
}

# Whether the mode references an absolute address (for label lookup)
MODE_IS_ABSOLUTE = {"ABS", "ABX", "ABY", "IND"}
MODE_IS_BRANCH = {"REL"}
MODE_IS_ZEROPAGE = {"ZP", "ZPX", "ZPY", "IZX", "IZY"}


def format_operand(mode, operand_bytes, pc):
    """Format operand for display. pc is the address of the instruction."""
    if mode == "IMP":
        return ""
    elif mode == "ACC":
        return "A"
    elif mode == "IMM":
        return f"#${operand_bytes[0]:02X}"
    elif mode == "ZP":
        return f"${operand_bytes[0]:02X}"
    elif mode == "ZPX":
        return f"${operand_bytes[0]:02X},X"
    elif mode == "ZPY":
        return f"${operand_bytes[0]:02X},Y"
    elif mode == "ABS":
        addr = operand_bytes[0] | (operand_bytes[1] << 8)
        return f"${addr:04X}"
    elif mode == "ABX":
        addr = operand_bytes[0] | (operand_bytes[1] << 8)
        return f"${addr:04X},X"
    elif mode == "ABY":
        addr = operand_bytes[0] | (operand_bytes[1] << 8)
        return f"${addr:04X},Y"
    elif mode == "IND":
        addr = operand_bytes[0] | (operand_bytes[1] << 8)
        return f"(${addr:04X})"
    elif mode == "IZX":
        return f"(${operand_bytes[0]:02X},X)"
    elif mode == "IZY":
        return f"(${operand_bytes[0]:02X}),Y"
    elif mode == "REL":
        offset = operand_bytes[0]
        if offset >= 0x80:
            offset -= 0x100
        target = (pc + 2 + offset) & 0xFFFF
        return f"${target:04X}"
    return "???"


def get_target_addr(mode, operand_bytes, pc):
    """Extract the target address from an operand, or None if not applicable."""
    if mode in MODE_IS_ABSOLUTE:
        return operand_bytes[0] | (operand_bytes[1] << 8)
    elif mode in MODE_IS_BRANCH:
        offset = operand_bytes[0]
        if offset >= 0x80:
            offset -= 0x100
        return (pc + 2 + offset) & 0xFFFF
    elif mode in MODE_IS_ZEROPAGE:
        return operand_bytes[0]
    return None


def decode_instruction(data, offset=0):
    """Decode one instruction from data at offset.
    Returns (mnemonic, mode, nbytes, operand_bytes) or None if invalid."""
    if offset >= len(data):
        return None
    opcode = data[offset]
    entry = OPCODES.get(opcode)
    if entry is None:
        return None
    mnemonic, mode, nbytes, cycles = entry
    if offset + nbytes > len(data):
        return None
    operand_bytes = data[offset + 1:offset + nbytes]
    return (mnemonic, mode, nbytes, operand_bytes)


if __name__ == "__main__":
    # Print opcode coverage stats
    print(f"Defined opcodes: {len(OPCODES)}/256")
    print(f"Undefined (illegal): {256 - len(OPCODES)}")
    by_mnemonic = {}
    for op, (mn, mode, nb, cy) in sorted(OPCODES.items()):
        by_mnemonic.setdefault(mn, []).append((op, mode))
    print(f"\nMnemonics ({len(by_mnemonic)}):")
    for mn in sorted(by_mnemonic):
        modes = ", ".join(f"${op:02X}:{mode}" for op, mode in by_mnemonic[mn])
        print(f"  {mn}: {modes}")
