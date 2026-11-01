"""Independent final upload exact-byte/approval audit; no compiled execution."""
from pathlib import Path
import json,hashlib,sys,sqlite3
ROOT=Path(__file__).resolve().parents[5];site=Path(sys.argv[1]);S=Path(sys.argv[2]);P='material-point-orthotropic/'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
manifest=read(site/P/'package-manifest.json');required=['orthotropic-contract.mjs','orthotropic-laboratory.mjs']+[P+p for p in ['orthotropic.js','orthotropic.wasm','models.json','model.json','identity.json','approval.json','review.json','review.html']];assert set(manifest)==set(required)
for p,h in manifest.items():assert sha(site/p)==h,p
identity=read(site/P/'identity.json')
for p,k in [('orthotropic.js','module_sha256'),('orthotropic.wasm','wasm_sha256'),('models.json','catalogue_sha256'),('model.json','model_sha256'),('approval.json','approval_sha256'),('review.json','review_sha256'),('review.html','review_html_sha256')]:assert sha(site/P/p)==identity[k]
assert identity['model_sha256']=='60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14';assert identity['review_sha256']=='a2862129dd393f2c73923b06706e12b75767f8b360b57bd1cfbb67c6069ef50f'
model=read(site/P/'model.json');cat=read(site/P/'models.json');approval=read(site/P/'approval.json');review=read(site/P/'review.json');assert cat['models']==[model] and cat['sha256']==identity['catalogue_hash'];assert approval['status']=='approved' and approval['definition']['sha256']==identity['model_sha256'] and approval['review']['sha256']==identity['review_sha256'];assert review['status']=='accepted' and not review['blocking_findings'] and len(review['checklist'])==9 and all(r['outcome']=='pass' for r in review['checklist'])
for p in ['orthotropic-laboratory.mjs','orthotropic-contract.mjs','app.js']:assert sha(site/p)==sha(S/'web'/p),p
assert sha(site/'docs/models/orthotropic-linear-elastic-ogs.md')=='cf995b39d080ab8f51d897024078adf4427e0ec9b09e2f60789b80515df3c12c'
assert sha(site/'docs/models/orthotropic-linear-elastic-ogs.md')==sha(S/'docs/models/orthotropic-linear-elastic-ogs.md')
assert 'the inspected source does not explicitly label its scalar sign convention' in (site/'orthotropic-laboratory.mjs').read_text();assert not (site/'orthotropic.html').exists()
public=read(site/'catalogue.json');ordinary=read(site/'models.json');assert len(ordinary['models'])==14 and sum(r['id']=='orthotropic-linear-elastic-ogs' for r in public['models'])==1
assert public==read(S/'catalogue/manifest.json')
registry=read(S/'catalogue/approved-models.json');assert [r for r in registry['models'] if r.get('model_id')=='orthotropic-linear-elastic-ogs']==[approval]
db=sqlite3.connect(site/'atlas.sqlite');db.row_factory=sqlite3.Row
assert read(site/P/'model.json')==json.loads(db.execute('select definition_json from models where id=?',('orthotropic-linear-elastic-ogs',)).fetchone()[0])
assert approval==json.loads(db.execute('select record_json from model_approvals where model_id=?',('orthotropic-linear-elastic-ogs',)).fetchone()[0]);assert review==json.loads(db.execute('select record_json from agent_reviews where model_id=?',('orthotropic-linear-elastic-ogs',)).fetchone()[0]);assert not list(db.execute('pragma foreign_key_check'))
sources=[dict(r) for r in db.execute('select * from sources where model_id=?',('orthotropic-linear-elastic-ogs',))];assert len({json.dumps(r,sort_keys=True) for r in sources})==3
print(json.dumps({'passed':True,'guarded_assets':len(manifest),'identity':identity,'ordinary_models':14,'catalogue_models':len(public['models']),'exact_registry_exported_definition_approval_review':True,'source_rows':len(sources),'unique_source_identities':3,'foreign_key_failures':0,'final_dossier_sha256':sha(site/'docs/models/orthotropic-linear-elastic-ogs.md'),'final_app_sha256':sha(site/'app.js'),'no_standalone':True},indent=2))
