import re
with open('components/society-main.tsx', encoding='utf-8') as f:
    content = f.read()
for m in re.finditer(r'\}>', content):
    start = max(0, m.start()-30)
    end = min(len(content), m.end()+10)
    print("GREATER at pos " + str(m.start()) + ": " + content[start:end])
