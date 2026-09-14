with open('components/society-main.tsx') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    for j, ch in enumerate(line):
        code = ord(ch)
        if code > 127 and ch not in ['\u2019', '\u2014', '\u2013', '\u2018', '\u201c', '\u201d', '\u00b7', '\u2192', '\u26a1', '\u2026', '\u00e2', '\u0080', '\u00a6', '\u00c2', '\u00b5', '\u00e9']:
            print(f"Line {i}, col {j+1}: U+{code:04X} '{ch}' (context: ...{line[max(0,j-10):j+10]}...)")
