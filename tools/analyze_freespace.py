import sys
rom = open('roms/TMOS_ORIGINAL.nes','rb').read()
bank = int(sys.argv[1]) if len(sys.argv)>1 else 1
base = 0x10 + bank*0x4000
data = rom[base:base+0x4000]
runs=[]; start=None; val=None
for i,b in enumerate(data):
    if b in (0x00,0xFF):
        if start is None: start,val=i,b
        elif b!=val: 
            if i-start>=32: runs.append((start,i,val))
            start,val=i,b
    else:
        if start is not None and i-start>=32: runs.append((start,i,val))
        start=None
if start is not None and len(data)-start>=32: runs.append((start,len(data),val))
print(f"Bank {bank} free-ish runs (>=32B of $00 or $FF):")
for s,e,v in runs:
    print(f"  ${0x8000+s:04X}-${0x8000+e-1:04X}  file 0x{base+s:05X}-0x{base+e-1:05X}  {e-s:5d}B  fill=${v:02X}")
