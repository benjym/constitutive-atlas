from pathlib import Path
import json,hashlib,datetime
s=Path(__file__).resolve().parent
assert not(s/'manifest.json').exists()and not(s/'native').exists()and not(s/'wasm').exists()
assert json.loads((s/'preflight-results.json').read_text())['passed']is True
pins={str(p.relative_to(s)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(s.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}
(s/'manifest.json').write_text(json.dumps(pins,indent=2,sort_keys=True)+'\n');(s/'prospective-freeze.json').write_text(json.dumps({'identity':'mc-control-trace-freeze-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':len(pins),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'trace_compiled_observations_at_freeze':0,'numerical_bounds_changed':False},indent=2)+'\n');print('frozen',len(pins))
