import re

with open('components/society-main.tsx', encoding='utf-8') as f:
    content = f.read()

# Find all template literals and check for > inside them
template_pattern = re.compile(r'`([^`]|\\.|$\{[^}]*\})*`', re.DOTALL)
for m in template_pattern.finditer(content):
    template = m.group(0)
    if '>' in template:
        start = content[:m.start()].count('\n') + 1
        print(f"Template at line {start} contains '>': {template[:80]}...")
