# find LDA #imm ; STA $AB  (immediate screen index writes)
rom = open('roms/TMOS_ORIGINAL.nes','rb').read()
for i in range(0x10, 0x20010-4):
    if rom[i]==0xA9 and rom[i+2]==0x85 and rom[i+3]==0xAB:
        bank=(i-0x10)//0x4000; addr=0x8000+((i-0x10)%0x4000) if bank<7 else 0xC000+((i-0x10)%0x4000)
        if bank==7: addr=0xC000+(i-0x10-7*0x4000)
        print(f"bank {bank} ${addr:04X}: LDA #${rom[i+1]:02X}; STA $AB")
