"""Independent standard-library saved-package audit; no production/engine imports."""
import json,sqlite3,hashlib
from pathlib import Path
R=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source');P=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/package-v7');B=R/'docs/ingestion/kelvin-voigt-comsol63';OUT=Path(__file__).parent/'release-v7-check-v1.json'
assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
f=read(B/'package-v7/freeze.json')
for p,h in f['source_sha256'].items():assert sha(R/p)==h,p
browser=read(B/'browser-v5/freeze.json')
for p,h in browser['assets'].items():assert sha(P/p)==h,p
assert browser['source_package_freeze_sha256']==sha(B/'package-v7/freeze.json')
reg=read(R/'catalogue/approved-models.json')['models'];manifest=read(R/'catalogue/manifest.json')['models'];assert len(reg)==24 and len(manifest)==47
c=sqlite3.connect('file:'+str(P/'atlas.sqlite')+'?mode=ro',uri=True)
assert c.execute('pragma integrity_check').fetchall()==[('ok',)] and not c.execute('pragma foreign_key_check').fetchall()
rows={x[0]:json.loads(x[1]) for x in c.execute('select id,record_json from model_approvals')};assert rows=={x['id']:x for x in reg}
expected_ids={x['id'] for x in manifest}|{x['model_id'] for x in reg};actual_ids={x[0] for x in c.execute('select id from models')};assert actual_ids==expected_ids
reviews=list(c.execute('select model_id,path,sha256,record_json from agent_reviews'));assert len(reviews)==20
for mid,p,h,record in reviews:assert sha(R/p)==h and read(R/p)==json.loads(record),p
mid='kelvin-voigt-comsol63-deviatoric-zero-spin-ode';a=next(x for x in reg if x['model_id']==mid);assert a['definition']['sha256']=='080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da'
assert read(R/a['definition']['path'])==json.loads(c.execute('select definition_json from models where id=?',(mid,)).fetchone()[0])
assert len(c.execute('select url from sources where model_id=?',(mid,)).fetchall())==3
s=read(B/'package-v7/supported-package.json');assert s['status']=='passed' and len(s['ordinary'])==15 and len(s['named'])==1
assert {x['id'] for x in s['ordinary']}==set(read(R/'catalogue/laboratory-package-policy.json')['models'])
log=(B/'package-v7/build.log').read_text();assert log.rstrip().endswith('Packaged '+str(P))
for token in ['"fullStateStressComparisons": 360','"exactReplay": true','"failedRequestRecovery": true']:assert token in log
kv=read(P/'engine-kelvin-voigt/identity.json');assert kv['model_sha256']==a['definition']['sha256'] and kv['review_sha256']==a['review']['sha256']
for p,h in read(P/'engine-kelvin-voigt/package-manifest.json')['files'].items():assert sha(P/p)==h
maps=read(B/'integration-v8/current37d-merge-v1/merge-receipt.json')['preserved_maps'];n=0
for p in maps:
 d=read(R/p)
 for path,h in d.get('documents',{}).items():assert sha(R/path)==h,path;n+=1
 for row in d.get('entries',[]):assert sha(R/row['archived_path'])==row['sha256'],row['archived_path'];n+=1
result=dict(identity='independent-final-normal-package-v7-check-v1',passed=True,source_pins=len(f['source_sha256']),package_assets=len(browser['assets']),models=len(actual_ids),discovery=len(manifest),approvals=len(rows),reviews=len(reviews),additional_approved_models=sorted(actual_ids-{x['id'] for x in manifest}),ordinary_requests=15,named_examples=1,map_bindings=n,integrity='ok',database_sha256=sha(P/'atlas.sqlite'),build_log_sha256=sha(B/'package-v7/build.log'),compiled_calls=0)
OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
