"""Verify immutable public approval bindings without compiled execution."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((HERE/'approval.json').read_text())
assert a in json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
assert a['status']=='approved' and a['deployment_authorized']
assert sha(ROOT/a['definition']['path'])==a['definition']['sha256']
for f in a['supporting_files']:assert sha(ROOT/f['path'])==f['sha256'],f['path']
for f,h in json.loads((HERE/'website-freeze.json').read_text())['files'].items():assert sha(ROOT/f)==h,f
if '--private' in sys.argv:
 r=json.loads((HERE/'source-retention.json').read_text());assert sha(ROOT/r['path'])==r['sha256']
print('Approval, exact model, source/review/numerical evidence and website policy bindings pass')
