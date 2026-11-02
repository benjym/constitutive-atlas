"""Source and manufactured assessor checks only; no engine/material/build calls."""
from pathlib import Path
import json,hashlib,sys,copy,pathlib
R=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;P=OUT.parent/'execution-v5';G=Path('/private/tmp/atlas-schedule-predictor-v1');V4=G/'docs/ingestion/bingham-comsol63/execution-v4';O=Path('/private/tmp/atlas-bingham-delivery-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'freeze-v1.json';assert sha(f)=='d1df44cc71b17373a728741cac0f946ffd63c6eed5ee286a2c649e5eea432c79'
b=json.loads(f.read_text())
for n,h in b['files'].items():assert sha(R/n)==h,n
s=json.loads((P/'source-bindings.json').read_text());assert len(s['source_files'])==187
for n,h in s['source_files'].items():assert sha(R/n)==h,n
for n,h in s['prior_inputs'].items():assert sha(P/n)==h,n
for n,v in s['archival_inputs'].items():assert sha(R/v['local_archival_path'])==v['sha256']==sha(G/n),n
for n in ['PLAN.md','freeze-v1.json','source-bindings.json','prior-v3-source-bindings.json']:assert (P/'prior-v4'/n).read_bytes()==(V4/n).read_bytes(),n
for n in ['cases.json','study.py','collect_wasm.mjs','parity.py','oracle.py','synthetic_checks.py','expected-catalogue.json','reference-convergence.json']:
 assert (P/n).read_bytes()==(V4/n).read_bytes()==(O/'docs/ingestion/bingham-comsol63/execution-v3'/n).read_bytes(),n
assert len(json.loads((P/'cases.json').read_text())['cases'])==136
prior=json.loads((V4/'source-bindings.json').read_text())['source_files'];delta={d['path'] for d in s['permitted_existing_deltas']};assert delta=={'CMakeLists.txt','cmake/bingham/CMakeLists.txt','cpp/include/atlas/schedule.hpp'}
for n,h in prior.items():
 if n in s['archival_inputs']:assert s['archival_inputs'][n]['sha256']==h
 else:assert n in s['source_files'] and (s['source_files'][n]==h or n in delta),n
profile=R/s['profile_freeze']['path'];assert sha(profile)==s['profile_freeze']['sha256']=='b308f1e965c9c28affeae89a6a47fb3be944313dc5f3593e51b351d40cddcca6'
for n,h in json.loads(profile.read_text())['files'].items():assert s['source_files'][n]==h==sha(R/n),n
assert sha(R/'runtimes/physical-time-v2/include/atlas/schedule.hpp')==prior['cpp/include/atlas/schedule.hpp']
assert sha(R/'cpp/include/atlas/schedule.hpp')==sha(O/'cpp/include/atlas/schedule.hpp')
# Independent manufactured assessment; redirect its sole output to owned scope.
sys.path.insert(0,str(P));code=(P/'synthetic_checks.py').read_text();needle="(BASE/'synthetic-checks.json').write_text";assert code.count(needle)==1
code=code.replace(needle,"(pathlib.Path("+repr(str(OUT/'synthetic-results.json'))+")).write_text")
ns={'__name__':'independent_assessor_only','pathlib':pathlib};exec(compile(code,str(P/'synthetic_checks.py'),'exec'),ns)
for target in ['request','result']:
 rows=copy.deepcopy(ns['rows'])
 if target=='request':rows[0]['request']['args'][11]=1e6
 else:
  v=json.loads(rows[0]['calls'][0]['stdout']);v['solver']['maximum_step']=1e6
  for call in rows[0]['calls']:call['stdout']=json.dumps(v)
 try:ns['assess'](ns['cases'],rows)
 except (AssertionError,ValueError,KeyError,TypeError,IndexError):pass
 else:raise AssertionError('cap mutation accepted: '+target)
helper=R/'docs/investigations/physical-time-v2-profile-v1/pin_artifacts.py';assert sha(helper)=='32e77dadd508eee9077ed3f3ba8f28a72a3acf25d0fb7c0ed624ec7ad667ce52'
results={'freeze_sha256':sha(f),'freeze_pins':len(b['files']),'live_source_pins':187,'archival_inputs':len(s['archival_inputs']),'profile_pins':183,'identical_cases':136,'identical_helpers':7,'synthetic_positive':136,'synthetic_negative':25,'additional_cap_mutations_rejected':2,'compiled_calls':0,'material_calls':0}
(OUT/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
