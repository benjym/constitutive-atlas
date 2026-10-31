"""Re-audit exact retained study evidence, including subnormal material rejection."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools import research_rate_observations_v3 as rates
from tools.research_rate_parity_v3 import assess
HERE=Path(__file__).resolve().parent
PACKET=ROOT/'docs/ingestion/hypoplastic-clay-2005/compiled-plan-v3'
def verify():
 freeze=rates.read(HERE/'prospective-freeze.json');assert freeze['compiled_observations_at_freeze']is False
 for name,pin in freeze['files'].items():assert rates.sha(HERE/name)==pin,name
 protocol,model,_=rates.checked_protocol(HERE/'protocol.json');corpus=rates.read(PACKET/'corpus.json')
 assert protocol['cases']==corpus['cases'] and len(protocol['cases'])==109
 assert (HERE/'model.json').read_bytes()==(PACKET/'model.json').read_bytes()
 assert protocol['policy']['source']==corpus['source_policy'] and protocol['finite_only_parity']['budget']==1e-10
 for name,pin in protocol['files'].items():
  assert rates.sha(HERE/'frozen-sources'/name)==pin,name
 paths=lambda backend:tuple(HERE/(backend+s)for s in ('-build.json','-observation.json','-observation.transport.json'))
 result=assess(HERE/'protocol.json',paths('native'),paths('wasm'));assert result==rates.read(HERE/'comparison.json')
 for backend in ('native','wasm'):
  build=rates.read(HERE/(backend+'-build.json'));assert build['all_commands_succeeded']
  for entry in build['commands']:
   p=ROOT/entry['path'];assert rates.sha(p)==entry['sha256'];assert rates.read(p)['returncode']==0
  assert rates.sha(HERE/'run_build.py')==build['build_script_sha256']
  assert rates.sha(HERE/'protocol.json')==build['protocol_sha256']
  for name,pin in build['generated'].items():assert rates.sha(HERE/name)==pin
  for name in ('models.hpp','models.json'):
   assert (HERE/(backend+'-generated-'+name)).read_bytes()==(HERE/'expected-generated'/name).read_bytes()
  assert result[backend]['row_counts']=={'accuracy':70,'finite_only':10,'reject':29} and result[backend]['recovery_rows']==29
  rows={row['id']:row['response']for row in result[backend]['cases']}
  for name in ('positive-subnormal','negative-subnormal'):
   ident='support-reject/'+name;case=next(c for c in protocol['cases']if c['id']==ident);response=rows[ident]
   assert response['ok']is False and response['message']=='unsupported research rate request' and response['values']is None
   for key,arg in zip(('parameters','state','increment'),case['args'][1:]):assert response[key]==[float(v)for v in arg.split(',')]
 for role in ('native','wasm'):
  rates.build_receipt(HERE/(role+'-build.json'),HERE/'protocol.json',role,True)
 return {'outcome':result['outcome'],'calls_per_backend':109,'independent_accuracy_cases':41,'accuracy_rows_including_recovery':70,'finite_only_rows':10,'material_rejection_recovery_pairs':29,'subnormal_echo_and_material_rejection':True,'original_cases_and_budgets_unchanged':True,'maximum_parity_budget_fraction':result['parity']['maximum_parity_budget_fraction'],'finite_integration':False,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2,allow_nan=False))
