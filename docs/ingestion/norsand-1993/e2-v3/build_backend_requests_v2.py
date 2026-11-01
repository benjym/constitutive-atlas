from pathlib import Path
import json,copy
from build_backend_requests import main as base_main
HERE=Path(__file__).resolve().parent

def main():
 base_main();data=json.loads((HERE/'backend-requests-v1.json').read_text());meta=json.loads((HERE/'backend-proposal-v5/generated/path_catalogue.json').read_text());contexts=json.loads((HERE/'restart-contexts-v1.json').read_text())
 for ctx,full in zip(contexts['rows'],data['requests'][:9]):
  assert ctx['id']==full['id'];layout=meta['models'][full['model']];left=ctx['left'];right=ctx['right']
  half=copy.deepcopy(full);half.update(id=full['id']+'-half',progress=.08,end_controls=[left['controls'][n] for n in layout['controls']],expected_state=[left['state'][f['name']] for f in layout['state']],expected_observables=[v for f in layout['observables'] for v in (left['observables'][f['name']] if f['size']==6 else [left['observables'][f['name']]])])
  restart=copy.deepcopy(full);restart.update(id=full['id']+'-restart',progress=.08,state=half['expected_state'],state_from=half['id'],coordinate=left['coordinate'],current_controls=half['end_controls'],start_controls=half['end_controls'],expected_state=[right['state'][f['name']] for f in layout['state']],expected_observables=[v for f in layout['observables'] for v in (right['observables'][f['name']] if f['size']==6 else [right['observables'][f['name']]])])
  cold=copy.deepcopy(restart);cold['id']=full['id']+'-cold-restart';cold.pop('state_from')
  data['requests'].extend([half,restart,cold])
 # Explicit successful replay after prior rejected calls; no hidden runtime state may survive failure.
 rejected=copy.deepcopy(next(r for r in data['requests'] if r['id']=='material-control-start-mismatch'));rejected['id']='material-rejection-before-recovery';data['requests'].append(rejected)
 recovery=copy.deepcopy(data['requests'][0]);recovery['id']='material-recovery-after-rejection';data['requests'].append(recovery)
 data.update(identity='controlled-path-native-wasm-v2',additions='9half-path+9backend-state chained restart+9cold restart requests; explicit success after rejection; strict finite/length artifact checks. Original gates unchanged.')
 (HERE/'backend-requests-v2.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
