from pathlib import Path
import json,hashlib,datetime,subprocess
s=Path(__file__).parent
assert not(s/'manifest.json').exists()
files={str(p.relative_to(s)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(s.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}
(s/'manifest.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
(s/'prospective-freeze.json').write_text(json.dumps({'identity':'browser-loading-provenance-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd='/Users/bmar5496/code/constitutive-atlas',text=True).strip(),'production_producer_calls_at_freeze':0,'compiled_calls_at_freeze':0,'files':len(files)},indent=2)+'\n')
print('frozen',len(files),'files')
