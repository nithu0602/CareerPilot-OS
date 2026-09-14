import re

with open('components/society-main.tsx', encoding='utf-8') as f:
    content = f.read()

# State machine to track if we're in string, template, comment, or code
state = 'code'  # code, single_quote, double_quote, template, line_comment, block_comment
paren_stack = []
i = 0
line = 1
col = 1
while i < len(content):
    ch = content[i]
    if ch == '\n':
        line += 1
        col = 1
        i += 1
        continue
    
    if state == 'code':
        if ch == '/' and i+1 < len(content) and content[i+1] == '/':
            state = 'line_comment'
        elif ch == '/' and i+1 < len(content) and content[i+1] == '*':
            state = 'block_comment'
        elif ch == '`':
            state = 'template'
        elif ch == '"':
            state = 'double_quote'
        elif ch == "'":
            state = 'single_quote'
        elif ch == '(':
            paren_stack.append((line, col))
        elif ch == ')':
            if paren_stack:
                paren_stack.pop()
            else:
                print(f"Extra ) at {line}:{col}")
        elif ch == '<' and i+1 < len(content) and content[i+1] == ' ':
            # Could be JSX - <div >
            pass
    
    elif state == 'line_comment':
        if ch == '\n':
            state = 'code'
    
    elif state == 'block_comment':
        if ch == '*' and i+1 < len(content) and content[i+1] == '/':
            state = 'code'
            i += 1
    
    elif state == 'single_quote':
        if ch == '\\':
            i += 1
        elif ch == "'":
            state = 'code'
    
    elif state == 'double_quote':
        if ch == '\\':
            i += 1
        elif ch == '"':
            state = 'code'
    
    elif state == 'template':
        if ch == '\\':
            i += 1
        elif ch == '`':
            state = 'code'
        elif ch == '$' and i+1 < len(content) and content[i+1] == '{':
            paren_stack.append((line, col))  # ${ opens a paren
            i += 1  # skip {
    
    i += 1
    col += 1

print(f"Unclosed parens: {len(paren_stack)}")
for l, c in paren_stack:
    print(f"  At {l}:{c}")
