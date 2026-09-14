import re

with open('components/society-main.tsx', encoding='utf-8') as f:
    lines = f.readlines()

# Get the return block (from line containing "return (" to the line with ");" before final "}")
start = None
end = None
for i, line in enumerate(lines):
    if 'return (' in line and i > 100:
        start = i
    if start is not None and line.strip() == ');':
        end = i
        break

print(f"Return block: lines {start+1} to {end+1}")
block = ''.join(lines[start:end+1])

# Remove template literals
block = re.sub(r'`[^`]*`', '`STR`', block)
# Remove string literals
block = re.sub(r'"[^"]*"', '"STR"', block)
block = re.sub(r"'[^']*'", "'STR'", block)
# Remove comments
block = re.sub(r'//.*', '', block)
block = re.sub(r'/\*.*?\*/', '', block, flags=re.DOTALL)

open_p = block.count('(')
close_p = block.count(')')
open_b = block.count('{')
close_b = block.count('}')

print(f"Parens: {open_p} open, {close_p} close, diff: {open_p - close_p}")
print(f"Braces: {open_b} open, {close_b} close, diff: {open_b - close_b}")

# Check for > and < outside strings
block2 = re.sub(r'"[^"]*"', 'STR', block)
block2 = re.sub(r"'[^']*'", 'STR', block2)
open_lt = block2.count('<')
close_gt = block2.count('>')
print(f"<: {open_lt}, >: {close_gt}, diff: {open_lt - close_gt}")
