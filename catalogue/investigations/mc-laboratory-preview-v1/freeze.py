"""Freeze all cache-free study inputs before the first candidate/backend run."""
from pathlib import Path
import json,hashlib,datetime
s=Path(__file__).resolve().parent
assert not(s/'manifest.json').exists()and not(s/'native').exists()and not(s/'wasm').exists()
for name,pin in json.loads((s/'input-freeze.json').read_text())['sha256'].items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==pin,name
assert json.loads((s/'assessor-preflight-results.json').read_text())['passed']is True
pins={}
for p in sorted(s.rglob('*')):
 if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc':pins[str(p.relative_to(s))]=hashlib.sha256(p.read_bytes()).hexdigest()
(s/'manifest.json').write_text(json.dumps(pins,indent=2,sort_keys=True)+'\n')
(s/'prospective-freeze.json').write_text(json.dumps({'identity':'mc-laboratory-preview-paths-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'files':len(pins),'compiled_observations_at_freeze':0,'requests_per_backend':14,'models':10,'scope':'Finite path gate only; browser integration/invalid requests and nine-model regressions separately required. No root promotion or deployment.'},indent=2)+'\n')
print('frozen',len(pins),'files')
