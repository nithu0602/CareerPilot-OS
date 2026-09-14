with open('components/society-main.tsx', encoding='utf-8') as f:
    content = f.read()

# Check for BOM
if content.startswith('\ufeff'):
    print("BOM found at start")
else:
    print("No BOM")

# Check for zero-width characters
zero_width = ['\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\u202a', '\u202b', '\u202c', '\u202d', '\u202e', '\u2060', '\u2061', '\u2062', '\u2063', '\u2064', '\ufeff']
for zw in zero_width:
    if zw in content:
        print(f"Zero-width character found: {repr(zw)} at {content.index(zw)}")

# Check for any other unusual characters
for ch in content:
    if ord(ch) in range(0x200, 0x210):  # Various formatting chars
        print(f"Formatting char: U+{ord(ch):04X} at {content.index(ch)}")

# Check for \r\n or \r
if '\r' in content:
    print("CR found")
else:
    print("No CR")

# Check last 3 bytes
print(f"Last 3 chars: {repr(content[-3:])}")
