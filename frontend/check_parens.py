import re

with open('components/society-main.tsx') as f:
    lines = f.readlines()

# Parse the return section (lines 188-304, 0-indexed 187-303)
section = ''.join(lines[187:304])

# Remove template literals
section = re.sub(r'`[^`]*`', '`STR`', section)
# Remove string literals
section = re.sub(r'"[^"]*"', '"STR"', section)
section = re.sub(r"'[^']*'", "'STR'", section)

open_parens = section.count('(')
close_parens = section.count(')')
open_braces = section.count('{')
close_braces = section.count('}')

print(f"In return section:")
print(f"  Parens: {open_parens} open, {close_parens} close, diff: {open_parens - close_parens}")
print(f"  Braces: {open_braces} open, {close_braces} close, diff: {open_braces - close_braces}")

# Also check the whole file but with template literals removed
content = ''.join(lines)
content2 = re.sub(r'`[^`]*`', '`STR`', content)
content2 = re.sub(r'"[^"]*"', '"STR"', content2)
content2 = re.sub(r"'[^']*'", "'STR'", content2)

print(f"\nIn whole file (strings/templates removed):")
print(f"  Parens: {content2.count('(')} open, {content2.count(')')} close, diff: {content2.count('(') - content2.count(')')}")
print(f"  Braces: {content2.count('{')} open, {content2.count('}')} close, diff: {content2.count('{') - content2.count('}')}")
