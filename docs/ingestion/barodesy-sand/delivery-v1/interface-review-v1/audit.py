"""Independent read-only integration/preservation audit; no compiled calls."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path('/private/tmp/atlas-barodesysand-delivery-v1')
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review,approval_entry
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def head(p):
 r=subprocess.run(['git','show','HEAD:'+p],cwd=ROOT,capture_output=True)
 return r.stdout if r.returncode==0 else None
report=json.loads((ROOT/'docs/ingestion/barodesy-sand/delivery-v1/preservation.json').read_text())
for item in report['archived_paths']:
 p=item['path']; raw=(ROOT/'catalogue/source-snapshots'/item['sha256']/p).read_bytes()
 assert sha(raw)==item['sha256']
 assert head(p)==raw,('archived bytes differ from baseline',p)
for b in report['old_bindings_verified']:
 checked_receipt(ROOT,b['document'],b['original_path'],b['sha256'])
map_checks=[]
for p in report['changed_maps']:
 raw=head(p); new=json.loads((ROOT/p).read_text())
 assert new['version']=='immutable-source-archive-map-0.1'
 if raw:
  old=json.loads(raw)
  assert all(new['documents'].get(k)==v for k,v in old['documents'].items()),p
  assert all(e in new['entries'] for e in old['entries']),p
 assert len({(e['original_path'],e['sha256']) for e in new['entries']})==len(new['entries'])
 for doc,pin in new['documents'].items():assert sha((ROOT/doc).read_bytes())==pin,(p,doc)
 map_checks.append(p)
reviewpath=ROOT/'catalogue/agent-reviews/barodesy-sand-agent-v1.json'
review=validate_review(reviewpath,root=ROOT,for_approval=True)
assert sha(reviewpath.read_bytes())=='df0e95028f38e4af94665ea8689d58b37a92d8c84b33f6aec4c503cbbd84efc6'
registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())
assert registry['models']==json.loads(head('catalogue/approved-models.json'))['models']+[approval_entry(reviewpath,root=ROOT)]
old=json.loads(head('catalogue/manifest.json'));new=json.loads((ROOT/'catalogue/manifest.json').read_text())
assert {k:v for k,v in old.items() if k!='models'}=={k:v for k,v in new.items() if k!='models'}
assert [m for m in old['models'] if m['id']!='barodesy-sand']==[m for m in new['models'] if m['id']!='barodesy-sand']
assert [m['id'] for m in old['models']]==[m['id'] for m in new['models']]
assert head('models/barodesy-sand.json')==(ROOT/'models/barodesy-sand.json').read_bytes()
# No model/runtime/schema source changed from qualified baseline.
changed=subprocess.check_output(['git','diff','--name-only','HEAD','--','models','cpp','atlas','schemas','web','CMakeLists.txt'],cwd=ROOT,text=True).splitlines()
assert not changed,changed
result={'status':'pass','reviewer':'/root/barodesy_sand_interface_review','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'canonical_review_sha256':sha(reviewpath.read_bytes()),'canonical_originals_verified':len(report['archived_paths']),'historical_bindings_verified':len(report['old_bindings_verified']),'maps_verified':len(map_checks),'prior_approvals_preserved':len(registry['models'])-1,'prior_discovery_entries_semantically_unchanged':len(new['models'])-1,'no_changed_model_runtime_schema_web_sources':True,'package_and_browser':'pending coordinator handoff'}
print(json.dumps(result,indent=2))
