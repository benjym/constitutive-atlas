"""Independent saved-response transaction audit; no compiled calls."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[5]
refs=json.loads((ROOT/'docs/ingestion/orthotropic-ogs/execution-v1/references.json').read_text())['cases'];path=Path(sys.argv[1]);rows=json.loads(path.read_text());assert len(rows)==len(refs)==121
lookup={r['id']:r['response'] for r in rows};restart=holds=rollback=rejections=recovery=0
for c,r in zip(refs,rows):
 assert c['id']==r['id'];d=r['response'];assert d['ok']==c['ok']
 if not c['ok']:
  rejections+=1
  if 'state' in d:assert d['state']==c['initial'];rollback+=1
  continue
 assert len(d['state'])==6 and d['parameters']==c['parameters'] and d['strain']==c['strain']
 assert d['catalogue_hash']=='5f394a724f409f9e1cbdea9f7ff536bd1566550eb7071c39987c1cb03f528abc' and d['model']=='orthotropic-linear-elastic-ogs'
 assert d['diagnostics']['substeps']==1 and d['diagnostics']['increment_fractions']==[1]
 if c.get('previous'):assert d['initial']==lookup[c['previous']]['state'];restart+=1
 else:assert d['initial']==c['initial']
 if c['id'].startswith('zero-'):assert d['state']==d['initial'];holds+=1
 if c['id'].startswith('recovery-'):recovery+=1
replay=['recovery-'+s for s in ['nonfinite-state','nonfinite-increment','wrong-state','wrong-increment']]
assert all(lookup[n]==lookup[replay[0]] for n in replay)
assert (holds,rollback,rejections,recovery,restart)==(6,3,13,13,10)
for n in [2,4]:
 for a,b in zip(lookup[f'partition-{n}-{n-1}']['state'],lookup['partition-1-0']['state']):assert abs(a-b)<=.0012
print(json.dumps({'passed':True,'raw_file':str(path),'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':len(rows),'exact_six_state_holds':holds,'domain_failure_full_state_rollback':rollback,'all_rejections':rejections,'successful_recovery_requests':recovery,'actual_returned_full_state_restart_calls':restart,'exact_complete_response_replays':len(replay),'partitions':[1,2,4]},indent=2))
