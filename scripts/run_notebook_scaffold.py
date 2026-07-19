import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
nb_path = root / 'milestone1-foundation.ipynb'
nb = json.loads(nb_path.read_text(encoding='utf-8'))
code = ''.join(''.join(cell.get('source', [])) for cell in nb['cells'] if cell.get('cell_type') == 'code')
ns = {'__name__': '__main__'}
exec(code, ns)
print('Scaffold execution completed.')
