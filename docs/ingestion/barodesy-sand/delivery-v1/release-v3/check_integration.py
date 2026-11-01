"""Read-only merged-release exact source, parents, package and SQLite gate."""
from pathlib import Path
import json,hashlib,sqlite3,sys,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review,approval_entry
from atlas.evidence import checked_receipt

def main(site):
 site=Path(site);parent=HERE.parent
 plan=json.loads((HERE/'prospective-plan.json').read_text())
 for p,pin in plan['source_inputs'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pin,p
 pins=json.loads((parent/'prospective-freeze.json').read_text())['source_inputs']
 for p,pin in pins.items():
  if p!='atlas/measurement_units.py':assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pin,p
 assert sum(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pin for p,pin in pins.items())==155
 review=ROOT/'catalogue/agent-reviews/barodesy-sand-agent-v1.json';validate_review(review,root=ROOT,for_approval=True);approval=approval_entry(review,root=ROOT)
 remote=json.loads(subprocess.check_output(['git','show',plan['parents'][1]+':catalogue/approved-models.json'],cwd=ROOT))
 registry=json.loads((ROOT/'catalogue/approved-models.json').read_text());assert registry['models']==remote['models']+[approval]
 remote_discovery=json.loads(subprocess.check_output(['git','show',plan['parents'][1]+':catalogue/manifest.json'],cwd=ROOT));discovery=json.loads((ROOT/'catalogue/manifest.json').read_text())
 assert [v for v in remote_discovery['models'] if v['id']!='barodesy-sand']==[v for v in discovery['models'] if v['id']!='barodesy-sand']
 count=0
 for name in ['preservation.json','merge-parent-preservation.json']:
  for b in json.loads((parent/name).read_text())['old_bindings_verified']:checked_receipt(ROOT,b['document'],b['original_path'],b['sha256']);count+=1
 assert json.loads((site/'catalogue.json').read_text())==discovery
 definition=json.loads((ROOT/'models/barodesy-sand.json').read_text());models=json.loads((site/'models.json').read_text());assert next(m for m in models['models'] if m['id']=='barodesy-sand')==definition
 c=sqlite3.connect(site/'atlas.sqlite');assert json.loads(c.execute('select definition_json from models where id=?',('barodesy-sand',)).fetchone()[0])==definition
 assert json.loads(c.execute('select record_json from model_approvals where model_id=?',('barodesy-sand',)).fetchone()[0])==approval
 exported=[json.loads(r[0]) for r in c.execute('select record_json from model_approvals')];assert sorted(exported,key=lambda x:x['id'])==sorted(registry['models'],key=lambda x:x['id'])
 evidence=json.loads((site/'evidence.json').read_text());row=next(v for v in evidence['agent_reviews'] if v['catalogue_id']=='barodesy-sand');assert row['status']=='accepted' and row['definition_current'] and row['registered_approval_id']==approval['id']
 assert (site/'.nojekyll').is_file()
 return {'pass':True,'common_qualification_source_pins':len(pins),'literal_original_and_parent_bindings':count,'preserved_remote_approvals':len(remote['models']),'total_approvals':len(registry['models']),'discovery_rows':len(discovery['models']),'ordinary_definitions':len(models['models']),'sqlite_models':c.execute('select count(*) from models').fetchone()[0],'sqlite_sources':c.execute('select count(*) from sources').fetchone()[0],'accepted_exact_model':definition['id'],'catalogue_hash':models['sha256'],'parents':plan['parents'],'site':str(site.resolve())}
if __name__=='__main__':print(json.dumps(main(sys.argv[1]),indent=2))
