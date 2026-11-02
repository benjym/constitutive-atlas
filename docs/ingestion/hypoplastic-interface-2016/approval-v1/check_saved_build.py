"""Read-only independent saved-build review; no compiled/material calls."""
from pathlib import Path
import json,hashlib,importlib.util,math
R=Path(__file__).resolve().parents[4]; P=R/'docs/ingestion/hypoplastic-interface-2016'; E=P/'execution-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
q=json.loads((E/'qualification.json').read_text()); b=q['binding']; assert q['status']=='passed'
counts={}
for group in ['artifacts','source_closure','cases','results']:
 for name,digest in b[group].items():
  p=Path(name); p=p if p.is_absolute() else R/p
  assert sha(p)==digest,(group,name)
 counts[group]=len(b[group])
for name,digest in q['toolchain'].items():assert sha(R/name)==digest
snapshot=Path('/private/tmp/atlas-interface2016-delivery-v1/source')
for name,digest in b['source_closure'].items():assert sha(snapshot/name)==digest
retention=json.loads((E/'artifact-retention.json').read_text());assert retention['originals']==b['artifacts']
for name,digest in b['artifacts'].items():
 rel=Path(name).relative_to('/private/tmp/atlas-interface2016-delivery-v1')
 assert sha(Path(retention['retention'])/rel)==digest
for stage in ['native-build','native-calls','wasm-build','wasm-calls']:
 receipt=json.loads((E/stage/'receipt.json').read_text()); assert receipt['status']=='passed'
 assert receipt['source_freeze_sha256']==sha(E/'source-freeze-v2.json')
 for cmd in receipt['commands']:
  assert cmd in q['commands'] and cmd['exit']==0 and sha(R/cmd['log'])==cmd['log_sha256']
  if '--build' in cmd['argv']:assert cmd['argv'][-5:]==['--target','atlas_path_capability','--parallel','1','--verbose']
for mode in ['native','wasm']:
 log=(E/(mode+'-build/2.log')).read_text()
 assert '-fno-fast-math -ffp-contract=off' in log and 'Built target atlas_path_capability' in log
 assert '-std=gnu++20' in log
 for name in ['path_api.cpp','path_models.hpp','path_catalogue.json']:
  assert sha(snapshot.parent/mode/'generated'/name)==sha(snapshot.parent/'wasm/generated'/name)
model=json.loads((R/'models/research/interface2016/hvwe2016-reconciled-fixed-local.json').read_text())
cat=json.loads((snapshot.parent/'wasm/generated/path_catalogue.json').read_text());assert len(cat['models'])==1
m=cat['models'][0];assert m['id']==model['id'] and m['model_sha256']==hashlib.sha256(json.dumps(model,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert m['formulation']==model['formulation'] and m['controls']==['gamma_x','gamma_z','normal_strain']
spec=importlib.util.spec_from_file_location('finite_v2',P/'implementation-v1/check_backend_results_v2.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
reports={mode:json.loads((E/(mode+'-results.json')).read_text()) for mode in ['native','wasm']}
assessments={mode:mod.assess(rep) for mode,rep in reports.items()}
assert reports['native']['library_sha256']==b['artifacts'][str(snapshot.parent/'native/libatlas_path_capability.dylib')]
for field,name in [('module_sha256','atlas_path_capability.mjs'),('wasm_sha256','atlas_path_capability.wasm')]:assert reports['wasm'][field]==b['artifacts'][str(snapshot.parent/'wasm'/name)]
maximum=0.;components=0
for x,y in zip(reports['native']['rows'],reports['wasm']['rows']):
 assert x['id']==y['id'] and x['status']==y['status'] and x['coordinate']==y['coordinate']
 for key,scales in [('state',[100000.]*4+[1.]),('observables',[100000.]*7+[1.])]:
  assert len(x[key])==len(y[key])==len(scales)
  for a,c,s in zip(x[key],y[key],scales):
   assert type(a) in (int,float) and type(c) in (int,float) and math.isfinite(a) and math.isfinite(c)
   error=abs(a-c)/s;assert error<=1e-10;maximum=max(maximum,error);components+=1
reg=json.loads((E/'python-regression.json').read_text());assert reg['exit']==0 and reg['tests']==25 and reg['skipped']==3
assert 'OK (skipped=3)' in (E/'python-regression.log').read_text()
out={'passed':True,'reviewer_run':'/root/hill_scientific_review','qualification_sha256':sha(E/'qualification.json'),'verified_binding_counts':counts,'toolchain_files':len(q['toolchain']),'source_snapshot_files':len(b['source_closure']),'original_and_durable_artifacts':6,'native_assessment':assessments['native'],'wasm_assessment':assessments['wasm'],'parity':{'rows':59,'components':components,'maximum_scaled_error':maximum,'bound':1e-10},'regression':reg,'method':'Read/hash/assess saved outputs only; no material/compiled calls or builds.'}
(Path(__file__).parent/'build-check-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('Saved build review passed:',counts,'parity',maximum)
