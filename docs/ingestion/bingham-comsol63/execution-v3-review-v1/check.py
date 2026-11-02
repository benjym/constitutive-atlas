"""Independent immutable-input/projection check; no backend/interpreter calls."""
from pathlib import Path
import json,hashlib,copy,sys
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
NEW=OUT.parent/'execution-v3';OLD=OUT.parent/'execution-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=NEW/'freeze-v1.json'
assert sha(freeze)=='b3f72df24459d66a15b45ef9912f6baf78d65fd869d533cb67c52290c807f0e1'
f=json.loads(freeze.read_text())
for name,h in f['files'].items():assert sha(ROOT/name)==h,name
bindings=json.loads((NEW/'source-bindings.json').read_text())
for group in ['source_files','analysis']:
 for name,h in bindings[group].items():assert sha(ROOT/name)==h,name
closure=OUT.parent/'execution-v1/build-inputs-v1.json';pins=json.loads(closure.read_text())['files']
assert len(pins)==138
for name,h in pins.items():assert sha(ROOT/name)==h,name
binary=ROOT/'build-native/atlas_bingham_solver';binary_sha=sha(binary)
assert binary_sha=='8adc81893b6f59219aa6722f2090b4b8f46a72efe061aac397b8cf9a6248ed0d'
old=json.loads((OLD/'cases.json').read_text());new=json.loads((NEW/'cases.json').read_text())
assert len(old['cases'])==len(new['cases'])==136
assert list(new)==list(old)
for k in old:
 if k not in ['identity','cases']:assert old[k]==new[k],k
M=100000/(2*10000000*.012*1024);deltas=[]
for x,y in zip(old['cases'],new['cases']):
 assert x['id']==y['id']
 cap=min(x['specification']['solver']['maximum_step'],M)
 expected=copy.deepcopy(x);expected['specification']['solver']['maximum_step']=cap;expected['args'][11]=cap
 i=expected['argv'].index('--max-time-step')+1;expected['argv'][i]=str(cap)
 assert y==expected,(x['id'],'full case record differs beyond cap')
 deltas.append({'id':x['id'],'from':x['specification']['solver']['maximum_step'],'to':cap})
helpers=['study.py','collect_wasm.mjs','parity.py','oracle.py','synthetic_checks.py','expected-catalogue.json','reference-convergence.json']
for name in helpers:assert (OLD/name).read_bytes()==(NEW/name).read_bytes(),name
# Execute assessor-only manufactured checks, redirecting its sole write into owned directory.
sys.path.insert(0,str(NEW));source=(NEW/'synthetic_checks.py').read_text()
needle="(BASE/'synthetic-checks.json').write_text";assert source.count(needle)==1
source=source.replace(needle,"(pathlib.Path("+repr(str(OUT/'synthetic-results.json'))+")).write_text")
import pathlib
scope={'__name__':'independent_synthetic_check','pathlib':pathlib}
exec(compile(source,str(NEW/'synthetic_checks.py'),'exec'),scope)
extra=[]
for target in ['request','result']:
 rows=copy.deepcopy(scope['rows'])
 if target=='request':rows[0]['request']['args'][11]=1e6
 else:
  reply=json.loads(rows[0]['calls'][0]['stdout']);reply['solver']['maximum_step']=1e6
  for call in rows[0]['calls']:call['stdout']=json.dumps(reply)
 try:scope['assess'](scope['cases'],rows)
 except (AssertionError,ValueError,KeyError,TypeError,IndexError):extra.append(target+' cap tamper rejected')
 else:raise AssertionError(target+' cap tamper accepted')
s=json.loads((OUT/'synthetic-results.json').read_text());assert s['positive_synthetic_cases']==136 and s['negative_mutations_rejected']==25
result=dict(decision='prospective accepted; no actual qualification or E5',freeze_sha256=sha(freeze),freeze_pins=len(f['files']),source_pins=len(bindings['source_files']),analysis_pins=len(bindings['analysis']),complete_original_build_pins=len(pins),native_binary_sha256=binary_sha,exact_full_case_projections=136,identical_helpers=helpers,synthetic_positive=136,synthetic_negative=25,additional_cap_mutations=extra,compiled_calls=0,material_calls=0,maximum_step_deltas=deltas)
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: frozen pins, complete 138 closure, native bytes, all 136 complete-case cap projections, seven identical helpers, 136 manufactured positives and 25 negative mutations.')
