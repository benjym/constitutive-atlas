"""Pure historical archive and approval integrity review; never evaluates a model."""
from pathlib import Path
import json,hashlib,subprocess,sys,copy
W=Path('/private/tmp/atlas-vibe2026-controlled-time-v1');O=Path(__file__).resolve().parent
sys.path.insert(0,str(W))
from atlas.agent_review import validate_review
from atlas.evidence import checked_receipt
BASE='31125e2e809dad1af8dd30805af7b8c2937197d4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
checks=[]
def check(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
P=W/'docs/ingestion/vibe-2026/integration-v1';receipt=load(P/'historical-preservation-receipt.json')
oldp=P/'preimages/8f80339c5f89f39c18f228a013300477ed4c9536ef2795e6760bc85727d5ede0-source-archive-map.json'
newp=W/'catalogue/agent-reviews/source-archive-map.json';old=load(oldp);new=load(newp)
check(sha(oldp)==receipt['old_map_sha256'],'old map exact preserved preimage')
check(sha(newp)==receipt['new_map_sha256'],'new map exact receipt hash')
check(new['version']==old['version'],'archive resolver version unchanged')
check(new['documents']==old['documents'],'every immutable document pin unchanged')
check(new['entries'][:len(old['entries'])]==old['entries'],'every prior mapping exact in original order')
added=new['entries'][len(old['entries']):];check(added==receipt['added'] and len(added)==5,'exactly five declared mappings appended')
for row in added:
 p=W/row['archived_path'];raw=subprocess.check_output(['git','show',BASE+':'+row['original_path']],cwd=W)
 check(p.read_bytes()==raw,row['original_path']+' archive byte-identical to retained Git base')
 check(sha(p)==row['sha256'],row['original_path']+' archive exact expected old hash')
 check(row['archived_path']=='catalogue/source-snapshots/'+row['sha256']+'/'+row['original_path'],row['original_path']+' canonical content-addressed location')
 check(sha(W/row['original_path'])!=row['sha256'],row['original_path']+' current source legitimately differs')
for rel in ['atlas/evidence.py','atlas/agent_review.py']:
 check((W/rel).read_bytes()==subprocess.check_output(['git','show',BASE+':'+rel],cwd=W),rel+' resolver unchanged from base')
check(load(P/'actual-historical-binding-diagnostic.json')==receipt['original_failed_receipts'],'nine original failed source receipt rows retained exactly')
check(len(receipt['original_failed_receipts'])==9,'all nine historical failures retained')
resolved=[]
for row in receipt['original_failed_receipts']:
 p=checked_receipt(W,row['document'],row['path'],row['sha256'])
 check(str(p.relative_to(W)) in [x['archived_path'] for x in added],row['document']+' resolves exact historical archive')
 resolved.append(dict(document=row['document'],original_path=row['path'],sha256=row['sha256'],resolved=str(p.relative_to(W))))
for name,pin in new['documents'].items():check(sha(W/name)==pin,'original immutable document current bytes '+name)
approvals=load(W/'catalogue/approved-models.json')['models'];records=[]
for a in approvals:
 model=W/a['definition']['path'];check(sha(model)==a['definition']['sha256'],a['id']+' current model exact')
 review=a['review'];check(sha(W/review['path'])==review['sha256'],a['id']+' review document exact')
 if review['kind']=='agent-model-review':
  r=validate_review(W/review['path'],root=W,for_approval=True)
  check(r['model']['id']==a['model_id'] and r['model']['sha256']==a['definition']['sha256'],a['id']+' accepted all-nine review matches registry')
  for f in a.get('supporting_files',[]):
   if review['path'] in new['documents']:p=checked_receipt(W,review['path'],f['path'],f['sha256'])
   else:p=W/f['path'];check(sha(p)==f['sha256'],a['id']+' live support hash '+f['path'])
 else:
  for f in a.get('supporting_files',[]):check(sha(W/f['path'])==f['sha256'],a['id']+' explicit-user support hash '+f['path'])
 records.append(dict(id=a['id'],model_id=a['model_id'],kind=review['kind'],review_sha256=review['sha256'],review_path=review['path']))
check(len(approvals)==29,'all 29 registry approvals checked')
check(sum(r['kind']=='agent-model-review' for r in records)==25,'all 25 independent agent records validated all-nine')
vibe=[r for r in records if r['model_id']=='vibe-2026'];check(len(vibe)==1 and vibe[0]['review_sha256'].startswith('17ba51ff'),'current VIBE exact new review remains live and accepted')
check(vibe[0]['review_path'] not in new['documents'],'new VIBE review receives no historical archive privilege')
(O/'results.json').write_text(json.dumps(dict(scope='source/hash/validator only; no model or compiled execution',checks=checks,count=len(checks),resolved_historical_receipts=resolved,registry_records=records,compiled_calls=0),indent=2)+'\n')
print('Historical preservation checks:',len(checks))
