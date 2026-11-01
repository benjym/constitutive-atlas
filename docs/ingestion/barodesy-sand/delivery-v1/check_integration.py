"""Read-only exact-source/approval/discovery/database and preservation checks."""
from pathlib import Path
import json,hashlib,sqlite3,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review,approval_entry
from atlas.evidence import checked_receipt

def main(site):
 site=Path(site); record=ROOT/'catalogue/agent-reviews/barodesy-sand-agent-v1.json'
 review=validate_review(record,root=ROOT,for_approval=True);approval=approval_entry(record,root=ROOT)
 report=json.loads((HERE/'preservation.json').read_text())
 for b in report['old_bindings_verified']:checked_receipt(ROOT,b['document'],b['original_path'],b['sha256'])
 def before(name):
  pin=next(v['sha256'] for v in report['archived_paths'] if v['path']==name)
  return json.loads((ROOT/'catalogue/source-snapshots'/pin/name).read_text())
 registry=json.loads((ROOT/'catalogue/approved-models.json').read_text())
 assert registry['models']==before('catalogue/approved-models.json')['models']+[approval]
 old=before('catalogue/manifest.json');new=json.loads((ROOT/'catalogue/manifest.json').read_text())
 assert len(old['models'])==len(new['models'])
 assert [m for m in old['models'] if m['id']!='barodesy-sand']==[m for m in new['models'] if m['id']!='barodesy-sand']
 definition=json.loads((ROOT/'models/barodesy-sand.json').read_text())
 catalogue=json.loads((site/'models.json').read_text())
 assert next(m for m in catalogue['models'] if m['id']=='barodesy-sand')==definition
 evidence=json.loads((site/'evidence.json').read_text())
 entry=next(v for v in evidence['agent_reviews'] if v['catalogue_id']=='barodesy-sand')
 assert entry['status']=='accepted' and entry['definition_current'] and entry['registered_approval_id']==approval['id']
 assert entry['definition_sha256']==review['model']['sha256']
 c=sqlite3.connect(site/'atlas.sqlite')
 row=c.execute('select definition_json from models where id=?',('barodesy-sand',)).fetchone();assert row and json.loads(row[0])==definition
 row=c.execute('select definition_sha256,record_json from model_approvals where model_id=?',('barodesy-sand',)).fetchone();assert row and row[0]==review['model']['sha256'] and json.loads(row[1])==approval
 row=c.execute('select sha256,record_json from agent_reviews where model_id=?',('barodesy-sand',)).fetchone();assert row and row[0]==hashlib.sha256(record.read_bytes()).hexdigest() and json.loads(row[1])==review
 assert (site/'.nojekyll').is_file(),'Standard package build must finish first'
 return {'pass':True,'prior_receipt_bindings':len(report['old_bindings_verified']),'prior_approvals_preserved':len(registry['models'])-1,'discovery_entries_preserved':len(new['models'])-1,'ordinary_models':len(catalogue['models']),'exact_approved_definition':review['model'],'registry_entry':approval['id'],'agent_review_export':entry,'sqlite':'exact definition/review/approval verified'}
if __name__=='__main__':print(json.dumps(main(sys.argv[1]),indent=2))
