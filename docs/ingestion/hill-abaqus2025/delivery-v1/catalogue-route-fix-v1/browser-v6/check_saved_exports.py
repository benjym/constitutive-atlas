"""Verify saved browser outputs against independent source-derived Decimal oracle."""
from pathlib import Path
import argparse,importlib.util,json
ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);ap.add_argument('--prefix',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
root=Path(__file__).resolve().parents[6]
spec=importlib.util.spec_from_file_location('hill_independent_oracle',root/'docs/ingestion/hill-abaqus2025/source-v1/check_algebra.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
keys=['p_ref','K','Gmod','sigma_y','F','Gh','Hh','L','M','N'];worst=[0.,0.];comparisons=0;exports={}
for kind in ['preset','changed','initial','reset','replay','shear']:
 doc=json.loads((a.directory/(a.prefix+kind+'.json')).read_text());exports[kind]=doc;r=doc['request'];state=r['initial'][:6];assert doc['ok'];assert len(doc['points'])==len(r['increments'])+1
 for de,pt,rec in zip(r['increments'],doc['points'][1:],doc['records']):
  reference=oracle.endpoint(dict(zip(keys,r['parameters'])),state,de,precision=100);assert pt['state']==rec['response']['state']
  for i,(v,e) in enumerate(zip(pt['state'],reference)):
   error=abs(v-float(e));assert error<=(.01+1e-10*abs(float(e)) if i<6 else 1e-9);comparisons+=1;worst[int(i==6)]=max(worst[int(i==6)],error)
  state=reference[:6]
assert exports['preset']==exports['reset'];assert exports['changed']==exports['replay']
result=dict(passed=True,state_comparisons=comparisons,max_stress_error_Pa=worst[0],max_gamma_error=worst[1],exact_reset=True,exact_replay=True,compiled_calls=0)
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
