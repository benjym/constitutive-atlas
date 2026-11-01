"""Compare exported SQLite rows with exact declared public source records."""
import argparse,hashlib,json,sqlite3,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('package',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=sqlite3.connect('file:'+str((a.package/'atlas.sqlite').resolve())+'?mode=ro',uri=True)
registry=json.loads((a.source/'catalogue/approved-models.json').read_text())['models'];manifest=json.loads((a.source/'catalogue/manifest.json').read_text())['models']
assert c.execute('pragma integrity_check').fetchall()==[('ok',)]
assert not c.execute('pragma foreign_key_check').fetchall()
for record in registry:
 row=c.execute('select record_json,definition_sha256 from model_approvals where id=?',(record['id'],)).fetchone();assert row and json.loads(row[0])==record,record['id'];assert row[1]==record['definition']['sha256']
for mid,path,digest,record in c.execute('select model_id,path,sha256,record_json from agent_reviews'):
 q=a.source/path;assert sha(q)==digest,path;assert json.loads(q.read_text())==json.loads(record)
mid='kelvin-voigt-comsol63-deviatoric-zero-spin-ode';approval=next(x for x in registry if x['model_id']==mid);model=a.source/approval['definition']['path']
assert sha(model)=='080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da'
assert json.loads(c.execute('select definition_json from models where id=?',(mid,)).fetchone()[0])==json.loads(model.read_text())
sources=c.execute('select url,locator,role from sources where model_id=?',(mid,)).fetchall();assert len(sources)==3 and all('doc.comsol.com/6.3/' in x[0] for x in sources)
ordinary=json.loads((a.package/'models.json').read_text())['models'];assert len(ordinary)==15 and mid not in {x['id'] for x in ordinary};assert 'ramberg-osgood-ansys242' in {x['id'] for x in ordinary}
assert json.loads((a.package/'catalogue.json').read_text())==json.loads((a.source/'catalogue/manifest.json').read_text())
sys.path.insert(0,str(a.source.resolve()))
from atlas.research import approved_definitions
approved,expected_approvals=approved_definitions()
expected_ids={x['id'] for x in manifest}|set(approved)
assert {x[0] for x in c.execute('select id from models')}==expected_ids
assert {x[0] for x in c.execute('select id from model_approvals')}=={x['id'] for x in expected_approvals}
for item in expected_approvals:
 assert json.loads(c.execute('select record_json from model_approvals where id=?',(item['id'],)).fetchone()[0])==item
counts={t:c.execute('select count(*) from '+t).fetchone()[0] for t in ['models','model_approvals','agent_reviews']}
assert len(manifest)==47 and len(registry)==24
result={'passed':True,'model':mid,'model_sha256':sha(model),'counts':counts,'ordinary_models':len(ordinary),'all_registry_records_exact':len(registry),'all_exported_agent_reviews_exact':counts['agent_reviews'],'source_rows':sources,'integrity':'ok','foreign_key_violations':0,'database_sha256':sha(a.package/'atlas.sqlite'),'database_manifest_sha256':sha(a.package/'atlas-database.json')}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
