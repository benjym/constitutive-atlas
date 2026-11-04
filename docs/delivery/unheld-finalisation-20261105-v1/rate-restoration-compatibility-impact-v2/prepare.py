"""Source-only exact C successor. No generation, subprocess or shared writes."""
from pathlib import Path
import json,hashlib,difflib
P=Path(__file__).resolve().parent;B=P.parent/'rate-restoration-compatibility-impact-v1';S=P.parent/'current17-runtime-source-v1/source';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,b):p=P/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);return p
oldsolver='05e6cc0c9dd6b6774597e07de0abe2beb7d9128383423d22b34c2e1d0a4d9218';newsolver='3278b22140ca2057a9a2e415654f5213b8183f398df79a7f5c56628756e8dc99'
changes=[('rate-restoration-compatibility-impact-v1/','rate-restoration-compatibility-impact-v2/'),('rate-restoration-compatibility-impact-review-v1/','rate-restoration-compatibility-impact-review-v2/'),('0292c075b7a81ce946adf3199e8f729102815ce427c71a16aea4db20932c99fc',newsolver),('tools/rate_restoration_source_view_v1.py','tools/rate_restoration_source_view_v2.py'),('rate-restoration-special-profile-source-view-review-v1','rate-restoration-special-profile-source-view-review-v2'),('rate-restoration-special-profile-source-view-proof-v1','rate-restoration-special-profile-source-view-proof-v2')]
helper=(B/'reviewed_source_view.py.txt').read_text()
for before,after in changes:helper=helper.replace(before,after)
put('reviewed_source_view.py.txt',helper.encode());put('proposed/tools/rate_restoration_source_view_v2.py',helper.encode())
proof=json.loads((B/'proof.json').read_text());proof['identity']='rate-restoration-special-profile-source-view-proof-v2';proof['source_delta']['current_sha256']=newsolver;proof['aliases']['cpp/include/atlas/solver.hpp']['current_sha256']=newsolver;proof['implementation'].pop('tools/rate_restoration_source_view_v1.py');proof['implementation']['tools/rate_restoration_source_view_v2.py']=sha(helper.encode());proof['source_only_claims']['maxwell']='solver.hpp included; C changes only drained incremental controller dispatch; physical-time public run contract rejects before controller. No numerical or rebuilt-binary equivalence claim.'
deltas=[]
for row in json.loads((B/'implementation-delta.json').read_text())['files']:
 name=row['path']
 if name.endswith('proof.json'):continue
 if name=='tools/rate_restoration_source_view_v1.py':name='tools/rate_restoration_source_view_v2.py';data=helper.encode()
 else:
  data=(B/row['proposal']).read_bytes()
  if name in ['tools/profile_source_compatibility.py','tools/profile_source_compatibility_baseline.py','tools/build_controlled_time_web.py']:
   data=data.replace(b'from tools.rate_restoration_source_view_v1 import',b'from tools.rate_restoration_source_view_v2 import');proof['implementation'][name]=sha(data);proof['aliases'][name]['current_sha256']=sha(data)
 put('proposed/'+name,data)
 target=W/name;pre=sha(target.read_bytes()) if target.is_file() else None
 if row['preimage_sha256'] is not None:assert pre==row['preimage_sha256'],(name,pre,row['preimage_sha256'])
 elif pre is not None:assert pre==sha(data),('unexpected preexisting additive path',name)
 deltas.append({'path':name,'preimage_sha256':pre,'sha256':sha(data),'bytes':len(data),'proposal':'proposed/'+name})
 if name in proof['implementation'] and name!='tools/rate_restoration_source_view_v2.py':
  before=(S/name).read_text();diff=''.join(difflib.unified_diff(before.splitlines(True),data.decode().splitlines(True),fromfile='current640/'+name,tofile='candidateC-compat/'+name));put('diffs/'+name+'.diff',diff.encode())
fields=['tests/test_recorded_api.py','tests/test_recorded_restarts.py','tests/test_solver.cpp','tests/test_ensemble.mjs','tools/test_ensemble.mjs','CMakeLists.txt','.github/workflows/full.yml','.github/workflows/qualification.yml'];bindings=json.loads((B/'observed-bindings.json').read_text());ct=json.loads((W/'docs/ingestion/manzari-dafalias-1997/delivery-v1/direct-controlled-time-compatibility-v1/proof.json').read_text());impact={}
for category,group in bindings.items():
 for name,row in group['value'].items():impact[category+'/'+name]={path:row['source_files'].get(path) for path in fields}
impact['controlled-time']={path:next((row['current'] for row in ct['source_inventory'] if row['path']==path),None) for path in fields}
assert all(v is None for profile in impact.values() for v in profile.values())
proof['tests']={path:'not a member of selected special-profile source maps or VIBE94 inventory; ordinary build/source guards still apply normally' for path in fields}
put('future-test-pin-impact.json',(json.dumps({'identity':'future-test-fixture-pin-impact-v2','observed_membership':impact,'new_delta_assumed':False,'namespace_caution':'Any new/changed atlas,cpp,schema file or selected dedicated cmake/generator input needs its own exact proof; no blanket exemption.'},indent=2)+'\n').encode())
raw=(json.dumps(proof,indent=2)+'\n').encode();put('proof.json',raw);name=str(P.relative_to(Path.cwd()))+'/proof.json' if P.is_absolute() else str(P/'proof.json');target=W/name;assert not target.exists();deltas.append({'path':name,'preimage_sha256':None,'sha256':sha(raw),'bytes':len(raw),'proposal':'proof.json'})
put('implementation-delta.json',(json.dumps({'files':deltas},indent=2)+'\n').encode())
# Preserve a reproducible diagnostic graph/binding source audit, adapted only to C.
audit=(B/'audit.py').read_text().replace("B=P.parent/'current17-igs97-regression-diagnosis-v1/original-rate-profile-v1/proposed/cpp/include/atlas/solver.hpp'","B=P.parent/'current17-igs97-regression-diagnosis-v2/proposed/cpp/include/atlas/solver.hpp'").replace('0292c075b7a81ce946adf3199e8f729102815ce427c71a16aea4db20932c99fc',newsolver)
put('audit.py',audit.encode())
check=(B/'check_source.py').read_text().replace('tools/rate_restoration_source_view_v1.py','tools/rate_restoration_source_view_v2.py').replace('from tools.rate_restoration_source_view_v1 import','from tools.rate_restoration_source_view_v2 import').replace('rate-restoration-special-profile-source-view-review-v1','rate-restoration-special-profile-source-view-review-v2').replace("P.parent/'current17-igs97-regression-diagnosis-v1/original-rate-profile-v1/proposed/cpp/include/atlas/solver.hpp'","P.parent/'current17-igs97-regression-diagnosis-v2/proposed/cpp/include/atlas/solver.hpp'")
needle=" check('unknown path never aliased',m.historical_bytes(root,'unlisted/path',b'unknown')==b'unknown')"
addition='''
 r=copy.deepcopy(review);r['identity']='rate-restoration-special-profile-source-view-review-v1';reviewpath.write_text(json.dumps(r));reject('B acceptance rejected',lambda:m.authority(root));reviewpath.write_text(json.dumps(review))
 q=root/m.SOURCE;original=q.read_bytes();q.write_bytes((P.parent/'current17-igs97-regression-diagnosis-v1/original-rate-profile-v1/proposed/cpp/include/atlas/solver.hpp').read_bytes());reject('B source rejected',lambda:m.authority(root));q.write_bytes(original)
'''
assert needle in check;check=check.replace(needle,needle+'\n'+addition);put('check_source.py',check.encode())
print(json.dumps({'paths':len(deltas),'proof':sha(raw)}))
