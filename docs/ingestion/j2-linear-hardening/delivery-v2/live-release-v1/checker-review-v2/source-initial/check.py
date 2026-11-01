"""Saved release/upload/live receipt verification; no network or compiled calls."""
from pathlib import Path
import hashlib,json,math
D=Path(__file__).resolve().parent;ROOT=D.parents[4]
def read(p):return json.loads(p.read_text())
def run():
 release='8e060a425015d65ffe087243204d17b8dba62ab8';ci=read(D/'release-run.json');assert ci['headSha']==release and ci['status']=='completed'and ci['conclusion']=='success'
 assert {j['name'] for j in ci['jobs']}=={'native (macos-26, 3.14)','native (ubuntu-latest, 3.12)','wasm','wasm-linux','deploy'}
 assert all(j['conclusion']=='success'for j in ci['jobs'])
 deployment=read(D/'deployment.json');assert deployment['deployment']['sha']==release and deployment['statuses'][0]['state']=='success'
 upload=read(D/'tested-upload.json');manifest=read(D/'uploaded-package-manifest.json');identity=read(D/'uploaded-engine-identity.json')
 required=set(manifest)|{'material-point-j2/package-manifest.json','app.js','index.html','atlas.js','atlas.wasm','models.json','catalogue.json','laboratory-controller-router.mjs','timed-laboratory.mjs','sls-laboratory.mjs'}
 for p,h in manifest.items():assert upload[p]==h
 for p,n in [('uploaded-package-manifest.json','material-point-j2/package-manifest.json'),('uploaded-engine-identity.json','material-point-j2/identity.json')]:assert hashlib.sha256((D/p).read_bytes()).hexdigest()==upload[n]
 for filename,key in [('j2-linear-isotropic-hardening-be.json','model_sha256'),('approval.json','approval_sha256'),('review.json','review_sha256'),('j2.js','module_sha256'),('j2.wasm','wasm_sha256'),('models.json','catalogue_sha256')]:assert upload['material-point-j2/'+filename]==identity[key]
 approved=read(D/'approved-identities.json')
 for p,key in [('models/research/j2/j2-linear-isotropic-hardening-be.json','model_sha256'),('catalogue/agent-reviews/j2-linear-hardening-agent-v2.json','review_sha256'),('docs/admission/j2-approved-v2/approval.json','approval_sha256')]:assert identity[key]==approved[p]
 assert identity['model']=='j2-linear-isotropic-hardening-be' and identity['catalogue_hash']=='2ce7ce9c486598a15c04c65600478bfb1fba227d442538d4aa3fc99076d15084'
 acquisition=read(D/'upload-acquisition.json');artifacts=read(D/'run-artifacts.json')['artifacts'];artifact=next(x for x in artifacts if x['id']==acquisition['artifact_id']);assert acquisition['run']==artifact['workflow_run']['id']==41299887463 and acquisition['head_sha']==artifact['workflow_run']['head_sha']==release and artifact['name']==acquisition['artifact_name']=='github-pages'
 live=read(D/'live-assets.json');assert live['passed']and live['release']==release and len(live['assets'])>=20
 assert len(live['assets'])==len(required) and {a['path']for a in live['assets']}==required
 for a in live['assets']:assert a['passed']and a['expected']==a['observed']==upload[a['path']]
 identity=read(D/'uploaded-engine-identity.json');export=read(D/'browser-export.json');assert export['ok']and export['failedRow']is None and export['provenance']==identity
 ref=read(ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/preset-references.json');q=export['request'];assert q['parameters']==ref['parameters']and q['initial']==ref['initial']and q['increments']==ref['increments'];assert q['settings']==[float(x)for x in ref['integration_settings'].split(',')]
 assert len(export['points'])==4 and len(export['records'])==3;comparisons=0
 for point,expected in zip(export['points'],[ref['initial'],*ref['expected']]):
  assert len(point['state'])==8
  for i,(a,b)in enumerate(zip(point['state'],expected)):
   assert math.isfinite(a)and abs(a-b)<=(.002 if i<6 else 2e-10);comparisons+=1
 browser=read(D/'browser-state.json');assert browser['url']=='https://benjym.github.io/constitutive-atlas/index.html#laboratory?model=j2-linear-isotropic-hardening-be' and browser['model']=='j2-linear-isotropic-hardening-be'
 assert len(browser['plots'])==2 and all(p['polyline_count']>=1 and p['distinct_point_count']>=3 and p['distinct_y_count']>=2 for p in browser['plots'])
 links={a['href'] for a in browser['links']};assert {'material-point-j2/review.html#law-review','material-point-j2/review.html#interface-review','material-point-j2/approval.json','material-point-j2/review.json','material-point-j2/j2-linear-isotropic-hardening-be.json'}.issubset(links)
 assert browser['J2']and not browser['ordinary']and not browser['Burgers']and not browser['SLS'];assert browser['status']=='Completed 3 increment rows.'and not browser['exportDisabled'];assert read(D/'live-console.json')==[]
 for p,h in read(D/'approved-identities.json').items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 return {'passed':True,'release':release,'all_required_jobs':5,'live_assets':len(live['assets']),'actual_browser_full_state_comparisons':comparisons,'reviewer_or_checker_compiled_calls':0,'scope':'Bounded named preset; no experimental or broader domain qualification'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
