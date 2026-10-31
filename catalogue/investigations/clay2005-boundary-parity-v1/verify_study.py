"""Re-audit both studies; report contraction-sensitive changes without source claims."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools import research_rate_observations_v3 as rates
from tools.research_rate_parity_v3 import assess
HERE=Path(__file__).resolve().parent;PRIOR=HERE.parent/'clay2005-rates-v3'
def bundles(folder,role):return tuple(folder/(role+s)for s in ('-build.json','-observation.json','-observation.transport.json'))
def verify():
 freeze=rates.read(HERE/'prospective-freeze.json');assert freeze['compiled_observations_at_freeze']is False
 for name,pin in freeze['files'].items():assert rates.sha(HERE/name)==pin,name
 p,_,_=rates.checked_protocol(HERE/'protocol.json');prior,_,_=rates.checked_protocol(PRIOR/'protocol.json')
 assert p['cases']==prior['cases'] and len(p['cases'])==109
 assert p['model_definition']==prior['model_definition'] and p['policy']==prior['policy'] and p['finite_only_parity']==prior['finite_only_parity']
 old=assess(PRIOR/'protocol.json',bundles(PRIOR,'native'),bundles(PRIOR,'wasm'));assert old==rates.read(PRIOR/'comparison.json') and old['outcome']=='failed'
 current=assess(HERE/'protocol.json',bundles(HERE,'native'),bundles(HERE,'wasm'));assert current==rates.read(HERE/'comparison.json')
 changes={}
 for role in ('native','wasm'):
  build=rates.read(HERE/(role+'-build.json'));assert build['build_script_sha256']==rates.sha(HERE/'run_build.py')
  for entry in build['commands']:
   command=rates.read(ROOT/entry['path']);assert rates.sha(ROOT/entry['path'])==entry['sha256'] and command['returncode']==0
  configure=rates.read(ROOT/build['commands'][2]['path']);assert '-DCMAKE_CXX_FLAGS=-ffp-contract=off'in configure['argv']
  buildcommand=rates.read(ROOT/build['commands'][3]['path']);assert buildcommand['argv'][-4:]==['--target','atlas_isolated','--parallel','1'] and buildcommand['environment']['EMCC_CORES']=='1'
  for name in ('models.hpp','models.json'):assert (HERE/(role+'-generated-'+name)).read_bytes()==(HERE/'expected-generated'/name).read_bytes()==(PRIOR/(role+'-generated-'+name)).read_bytes()
  rates.build_receipt(HERE/(role+'-build.json'),HERE/'protocol.json',role,True)
  changed=[];maximum=0.
  for a,b in zip(current[role]['cases'],old[role]['cases']):
   assert a['id']==b['id'];x=a['response'];y=b['response']
   for key in x:
    if key!='values':assert x[key]==y[key],(a['id'],key)
   if x['values']!=y['values']:
    assert x['ok'] and y['ok'];errors=[abs(u-v)/max(1,abs(u),abs(v))for u,v in zip(x['values'],y['values'])]
    changed.append({'case':a['id'],'maximum_scaled_change':max(errors),'current':x['values'],'prior':y['values']});maximum=max(maximum,max(errors))
  changes[role]={'changed_response_count':len(changed),'maximum_scaled_change':maximum,'changed':changed}
 return {'outcome':current['outcome'],'original_outcome':old['outcome'],'all109cases_and_gates_unchanged':True,'maximum_parity_budget_fraction':current['parity']['maximum_parity_budget_fraction'],'changes_vs_same_backend_original':changes,'boundary_source_accuracy_established':False,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2,allow_nan=False))
