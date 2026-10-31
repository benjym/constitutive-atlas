if not __debug__:raise RuntimeError('Required preservation checks cannot be optimized away')
from pathlib import Path
import json,hashlib,datetime,subprocess
s=Path(__file__).parent;r=Path('/Users/bmar5496/code/constitutive-atlas')
assert not(s/'manifest.json').exists()
expected=(r/'cpp/main.cpp').read_text().replace('#include "atlas/recorded.hpp"','#include "atlas/recorded.hpp"\n#include "atlas/stress_observables.hpp"').replace('std::sqrt(1.5*atlas::dot(atlas::dev(sigma),atlas::dev(sigma)))','atlas::deviatoric_stress_magnitude(sigma)')
assert expected==(s/'frozen/cpp/main.cpp').read_text()
for p in (r/'cpp').rglob('*'):
 if p.is_file()and p.name!='main.cpp':assert p.read_bytes()==(s/'frozen'/p.relative_to(r)).read_bytes(),str(p)
for p,h in json.loads((s/'baseline/artifacts.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
assert json.loads((s/'preflight-results.json').read_text())['negative_checks']==22
files={str(p.relative_to(s)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(s.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}
(s/'manifest.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
(s/'prospective-freeze.json').write_text(json.dumps({'identity':'laboratory-q-cancellation-fix-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'compiled_calls_at_freeze':0,'reference_cases':35,'browser_pairs':101,'files':len(files)},indent=2)+'\n');print('frozen',len(files),'files')
