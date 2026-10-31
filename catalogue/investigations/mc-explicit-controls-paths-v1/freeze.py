from pathlib import Path
import json,hashlib,datetime,subprocess
s=Path(__file__).resolve().parent;root=Path('/Users/bmar5496/code/constitutive-atlas')
if(s/'manifest.json').exists()or(s/'native').exists()or(s/'wasm').exists():raise RuntimeError('already frozen/observed')
source=(s/'frozen/cpp/include/atlas/solver.hpp').read_text();original=(root/'cpp/include/atlas/solver.hpp').read_text()
if original.replace('initial.size()!=initial_state(model).size()||!domain(model,initial,p))','initial.size()!=initial_state(model).size()||!domain(model,initial,p,true))')!=source:raise RuntimeError('unrelated header change')
for p in (root/'cpp').rglob('*'):
 if p.is_file()and p.name!='solver.hpp' and p.read_bytes()!=(s/'frozen'/p.relative_to(root)).read_bytes():raise RuntimeError('unrelated core change '+str(p))
pre=json.loads((s/'preflight-results.json').read_text())
if not pre['source_ideal']['passed']or pre['source_ideal']['points']!=834 or pre['negative_checks']!=20:raise RuntimeError('preflight incomplete')
for role,artifacts in json.loads((s/'legacy-baseline-artifacts.json').read_text()).items():
 for item in artifacts.values():
  if hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()!=item['sha256']:raise RuntimeError('legacy artifact changed')
manifest={str(p.relative_to(s)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(s.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}
(s/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
(s/'prospective-freeze.json').write_text(json.dumps({'identity':'mc-explicit-controls-finite-paths-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'files':len(manifest),'compiled_observations_at_freeze':0,'requests_per_backend':14,'points_per_backend':834,'rejection_recovery_pairs_per_backend':12,'models':10,'scope':'exact-input finite paths and upfront initial checks; no browser/producer/root-model/push/deployment admission'},indent=2)+'\n')
print('frozen',len(manifest),'files')
