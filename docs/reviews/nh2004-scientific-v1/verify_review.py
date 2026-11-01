"""Read-only review/input exact-byte verification; no compiled calls."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
m=json.loads((P/'input-manifest.json').read_text())
missing=[];context_drift=[]
for row in m['inputs']:
    path=Path(row['path']) if row['path'].startswith('/') else ROOT/row['path']
    if not path.exists():
        if row.get('private'):missing.append(row['path']);continue
        raise AssertionError(f'Missing input: {path}')
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if row.get('verification_policy')=='reviewed_context_only':
        if actual!=row['sha256']:context_drift.append(row['path'])
        continue
    assert actual==row['sha256'],str(path)
for name,h in m['review_files'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest()==h,name
r=json.loads((P/'check-results.json').read_text())
assert r['algebra_pass'] and len(r['algebra'])==25
assert not r['softening_negative_multiplier_witnesses']
assert len(r['finite_paths'])==6 and len(r['laboratory'])==5
print(f'PASS: {len(m["inputs"])} input identities; {len(m["review_files"])} review-file identities; 25 independent algebra checks. Private inputs absent: {len(missing)}. Mutable board/context drift: {len(context_drift)}.')
