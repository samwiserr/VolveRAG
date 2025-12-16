import json
from pathlib import Path
p = Path('data/vectorstore/petro_params_cache.json')
if not p.exists():
    print('MISSING', p)
    raise SystemExit(1)
obj = json.loads(p.read_text(encoding='utf-8'))
rows = obj.get('rows', [])
found = [r for r in rows if '15/9-F-5' in (r.get('well') or '') and r.get('formation','').lower()=='hugin']
print('Found', len(found), 'records')
for r in found:
    print('---')
    print('well:', r.get('well'))
    print('formation:', r.get('formation'))
    print('sw:', r.get('sw'))
    print('phif:', r.get('phif'))
    print('source:', r.get('source'))
