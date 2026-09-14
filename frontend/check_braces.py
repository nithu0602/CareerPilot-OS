import re

with open('components/society-main.tsx') as f:
    lines = f.readlines()

# Parse through and track brace depth, ignoring strings and template literals
brace_depth = 0
in_template = False
in_single_quote = False
in_double_quote = False
i = 0
while i < len(lines):
    line = lines[i]
    j = 0
    while j < len(line):
        ch = line[j]
        next_ch = line[j+1] if j+1 < len(line) else ''
        
        if in_template:
            if ch == '\\':
                j += 2
                continue
            if ch == '`':
                in_template = False
            j += 1
            continue
        
        if in_single_quote:
            if ch == '\\':
                j += 2
                continue
            if ch == "'":
                in_single_quote = False
            j += 1
            continue
        
        if in_double_quote:
            if ch == '\\':
                j += 2
                continue
            if ch == '"':
                in_double_quote = False
            j += 1
            continue
        
        # Not in string
        if ch == '`':
            in_template = True
        elif ch == "'":
            in_single_quote = True
        elif ch == '"':
            in_double_quote = True
        elif ch == '{':
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth < 0:
                print(f"Unmatched }} at line {i+1}, col {j+1}, depth went to {brace_depth}")
        
        j += 1
    i += 1

print(f"Final brace depth: {brace_depth}")
