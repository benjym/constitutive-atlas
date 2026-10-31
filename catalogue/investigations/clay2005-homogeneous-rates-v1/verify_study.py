"""Re-audit candidate evidence without treating a negative outcome as a pass."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
from tools import research_rate_observations_v3 as rates
from tools.research_rate_parity_v3 import assess
from prepare import prepare,read,OLD

def verify():
 freeze=read(HERE/'prospective-freeze.json');assert freeze['compiled_observations_at_freeze']is False
 for name,pin in freeze['files'].items():assert rates.sha(HERE/name)==pin,name
 protocol,model,size=rates.checked_protocol(HERE/'protocol.json');assert protocol==prepare()
 assert protocol['cases']==read(OLD/'protocol.json')['cases'] and len(protocol['cases'])==120
 for name,pin in protocol['files'].items():assert rates.sha(HERE/'frozen-sources'/name)==pin,name
 paths=lambda role:tuple(HERE/(role+s)for s in ('-build.json','-observation.json','-observation.transport.json'))
 result=assess(HERE/'protocol.json',paths('native'),paths('wasm'));assert result==read(HERE/'comparison.json')
 report={'outcome':result['outcome'],'calls_per_backend':120,'original_calls_and_gates_unchanged':109,'additional_source_accuracy_calls':11,'backends':{},'parity':result['parity'],'finite_integration':False,'scientific_admission':False}
 for role in ('native','wasm'):
  build=rates.build_receipt(HERE/(role+'-build.json'),HERE/'protocol.json',role,True)
  for entry in build['commands']:
   path=ROOT/entry['path'];assert rates.sha(path)==entry['sha256'] and read(path)['returncode']==0
  assert build['build_script_sha256']==rates.sha(HERE/'run_build.py')
  for name,pin in build['generated'].items():assert rates.sha(HERE/name)==pin
  for name in ('models.hpp','models.json'):assert (HERE/(role+'-generated-'+name)).read_bytes()==(HERE/'expected-generated'/name).read_bytes()
  a=result[role];assert a['row_counts']=={'accuracy':81,'finite_only':10,'reject':29} and a['recovery_rows']==29
  rows={c['id']:c['response']for c in a['cases']};boundary=[]
  for case in protocol['cases'][109:]:
   response=rows[case['id']];e=case['expectation'];values=response['values']
   fractions=[abs(x-y)/b for x,y,b in zip(values,e['values'],e['absolute_budgets'])]if response['ok']else None
   boundary.append({'id':case['id'],'accepted':response['ok'],'max_source_budget_fraction':max(fractions)if fractions else None,'passed':fractions is not None and max(fractions)<=1})
  historical_ids={c['id']for c in protocol['cases'][:109]}
  report['backends'][role]={'outcome':a['outcome'],'row_counts':a['row_counts'],'recovery_rows':a['recovery_rows'],'failures':a['failures'],'boundary_accuracy':boundary}
  for name in ('positive-subnormal','negative-subnormal'):
   ident='support-reject/'+name;c=next(c for c in protocol['cases']if c['id']==ident);response=rows[ident]
   assert response['ok']is False and response['message']=='unsupported research rate request' and response['values']is None
   for key,arg in zip(('parameters','state','increment'),c['args'][1:]):assert response[key]==[float(v)for v in arg.split(',')]
 return report
if __name__=='__main__':print(json.dumps(verify(),indent=2,allow_nan=False))
