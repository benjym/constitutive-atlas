from pathlib import Path
import json,os
from identity import verify_inputs,digest,require
s=Path(__file__).resolve().parent;o=s/'native'
verify_inputs(s);plan=json.loads((s/'PLAN.json').read_bytes())
receipt=json.loads((o/'receipt.json').read_bytes());rows=json.loads((o/'journal.json').read_bytes());requests=json.loads((s/'requests.json').read_bytes())
require(receipt['completed'] is False,'original must be incomplete')
require(len(rows)==21 and len(receipt['commands'])==21,'all calls retained')
require([x['id'] for x in rows]==['describe']+[x['id'] for x in requests],'ordered rows')
require(receipt['freeze_sha256']==digest(s/'INPUT_FREEZE.json'),'source binding')
require(receipt['artifacts']==plan['artifacts']['native'],'artifact binding')
for n,h in receipt['artifacts'].items():require(digest(n)==h,'artifact bytes')
for i,(row,c) in enumerate(zip(rows,receipt['commands'])):
 label='describe' if i==0 else 'request-'+str(i-1)
 require(c['label']==label,'command label')
 require((o/(label+'.stdout.txt')).read_bytes().decode()==row['raw'],'raw stdout')
 require((o/(label+'.stderr.txt')).read_bytes()==b'','empty stderr')
 if i==0:require(c['argv']==[plan['native'],'--describe'] and c['exit_code']==0,'descriptor')
 else:
  q=requests[i-1];require(row['request']==q,'literal request')
  args=[plan['native'],'--mode',q['mode'],'--model',q['model'],'--parameters',q['parameters'],'--initial',q['initial'],'--integration-settings',q['integration_settings']]
  for k in (['protocol','target','steps','cycles'] if q['mode']=='run' else ['strain']):args+=['--'+k,str(q[k])]
  require(c['argv']==args and c['exit_code']==(0 if q['expected_ok'] else 1),'exact command/exit')
snap=s/'finalization-recovery-v1';snap.mkdir(exist_ok=False)
(snap/'receipt.incomplete.json').write_bytes((o/'receipt.json').read_bytes())
(snap/'parent-status.incomplete.json').write_bytes((s.parent/'execution/current20-native/STATUS.json').read_bytes())
report={'status':'recovered-complete-raw-collection-after-filesystem-interruption','original_incomplete_receipt_sha256':digest(snap/'receipt.incomplete.json'),'original_parent_status_sha256':digest(snap/'parent-status.incomplete.json'),'journal_sha256':digest(o/'journal.json'),'commands_verified':21,'requests_verified':20,'source_pins_verified':len(verify_inputs(s)['files']),'material_calls_repeated':0,'collector_process_exit_code':'not recovered or inferred','parent_failure':'Observed terminal exec traceback OSError Errno28 No space left on device writing STATUS.json; original status running is stale, not proof of a live process.','scope':'Metadata recovery only; numerical assessment follows.'}
(snap/'RECOVERY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
receipt.update(completed=True,journal_sha256=digest(o/'journal.json'),completion_recovered=True,completion_recovery={'path':'finalization-recovery-v1/RECOVERY_CHECK.json','sha256':digest(snap/'RECOVERY_CHECK.json')})
tmp=o/'receipt.finalizing.json';tmp.write_text(json.dumps(receipt,indent=2)+'\n');os.replace(tmp,o/'receipt.json')
print(json.dumps(report))
