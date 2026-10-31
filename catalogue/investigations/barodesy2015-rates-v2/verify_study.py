"""Re-audit retained raw evidence and prove the original corpus/gates survived."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools import research_rate_observations_v2 as rates
from tools.research_rate_parity_v2 import assess
HERE=Path(__file__).resolve().parent

def run():
 freeze=rates.read(HERE/'prospective-freeze.json')
 assert freeze['compiled_observations_at_freeze'] is False
 for name,pin in freeze['files'].items():assert rates.sha(HERE/name)==pin,name
 protocol,model,_=rates.checked_protocol(HERE/'protocol.json')
 old=HERE.parent/'barodesy2015-rates-v1'
 assert rates.sha(old/'protocol.json')==freeze['historical_protocol_sha256']
 original=rates.read(old/'protocol.json');assert len(protocol['cases'])==len(original['cases'])==70
 for current,prior in zip(protocol['cases'],original['cases']):
  current=json.loads(json.dumps(current));current['args'][0]=prior['args'][0];assert current==prior
 for key in ('parameters','state','derived','equations','domain'):
  current=model[key]
  if key=='state':current=[{k:v for k,v in field.items() if k!='semantics'} for field in current]
  assert current==original['model_definition'][key],key
 assert rates.read(old/'comparison.json')['outcome']=='failed'
 paths=lambda backend:tuple(HERE/(backend+suffix) for suffix in ('-build.json','-observation.json','-observation.transport.json'))
 result=assess(HERE/'protocol.json',paths('native'),paths('wasm'))
 assert result==rates.read(HERE/'comparison.json')
 assert result['outcome']=='passed'
 for name in ('models.hpp','models.json'):
  assert (HERE/('native-generated-'+name)).read_bytes()==(HERE/('wasm-generated-'+name)).read_bytes()
 valid=sum(c['expectation']['ok'] and 'recovery_of' not in c for c in protocol['cases'])
 rejected=sum(not c['expectation']['ok'] for c in protocol['cases'])
 assert (valid,rejected)==(38,16)
 return {'outcome':result['outcome'],'valid_cases_per_backend':valid,'rejection_recovery_pairs_per_backend':rejected,'rows_including_descriptor_per_backend':71,'original_requests_and_budgets_unchanged':True,'original_v1_failure_preserved':True,'maximum_parity_budget_fraction':result['parity']['maximum_parity_budget_fraction'],'scientific_admission':False,'finite_integration':False}
if __name__=='__main__':print(json.dumps(run(),indent=2,allow_nan=False))
