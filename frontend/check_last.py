with open('components/society-main.tsx', encoding='utf-8') as f:
    lines = f.readlines()
for i in range(len(lines)-5, len(lines)):
    line = lines[i]
    print(f'Line {i+1}:')
    print(f'  text: {repr(line)}')
    print(f'  hex:  {line.encode("utf-8").hex()}')
