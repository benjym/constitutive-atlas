from pathlib import Path
import json,hashlib,urllib.request,datetime,tarfile
r=Path('/Users/bmar5496/code/constitutive-atlas');d=r/'docs/ingestion/j2-linear-hardening/delivery-v2/live-release-v1';a=Path('/private/tmp/atlas-j2-main-v2/pages-artifact-v3');u=Path('/private/tmp/atlas-j2-main-v2/pages-upload-v3');u.mkdir(exist_ok=True)
tars=list(a.rglob('artifact.tar'));assert len(tars)==1
with tarfile.open(tars[0])as t:t.extractall(u,filter='data')
sha=lambda b:hashlib.sha256(b).hexdigest()
artifacts=json.loads((d/'run-artifacts.json').read_text());artifact=next(x for x in artifacts['artifacts'] if x['name']=='github-pages');assert artifact['workflow_run']['id']==41299887463 and artifact['workflow_run']['head_sha']=='8e060a425015d65ffe087243204d17b8dba62ab8'
(d/'upload-acquisition.json').write_text(json.dumps({'run':41299887463,'head_sha':'8e060a425015d65ffe087243204d17b8dba62ab8','artifact_id':artifact['id'],'artifact_name':artifact['name'],'artifact_api_digest':artifact.get('digest'),'download_command':'gh run download 41299887463 --name github-pages --dir /private/tmp/atlas-j2-main-v2/pages-artifact-v3','extracted_artifact_tar_sha256':sha(tars[0].read_bytes())},indent=2)+'\n')
allfiles={str(p.relative_to(u)):sha(p.read_bytes())for p in u.rglob('*')if p.is_file()};(d/'tested-upload.json').write_text(json.dumps(allfiles,indent=2)+'\n')
manifest=json.loads((u/'material-point-j2/package-manifest.json').read_text());ident=json.loads((u/'material-point-j2/identity.json').read_text());assert ident['model_sha256']=='a28068cbb8cfc660e49eb648d6ce7fcbf993ea50b45e8eb0d325c6b75f4ffc3b'
for n,h in manifest.items():assert allfiles[n]==h,n
for filename,key in [('j2-linear-isotropic-hardening-be.json','model_sha256'),('approval.json','approval_sha256'),('review.json','review_sha256'),('j2.js','module_sha256'),('j2.wasm','wasm_sha256'),('models.json','catalogue_sha256')]:assert allfiles['material-point-j2/'+filename]==ident[key]
assert allfiles['app.js']=='971db3394a28e332350e3586db99f1a79a0d29e4e631cbb9ed05651f19cd6023'
paths=sorted(set(manifest)|{'material-point-j2/package-manifest.json','app.js','index.html','atlas.js','atlas.wasm','models.json','catalogue.json','laboratory-controller-router.mjs','timed-laboratory.mjs','sls-laboratory.mjs'})
base='https://benjym.github.io/constitutive-atlas/';results=[];attempt=d/('live-assets-attempt-'+str(len(list(d.glob('live-assets-attempt-*.json')))+1)+'.json')
for n in paths:
 req=urllib.request.Request(base+n,headers={'Cache-Control':'no-cache','User-Agent':'ConstitutiveAtlasReleaseVerification'})
 with urllib.request.urlopen(req,timeout=60)as f:b=f.read();h=dict(f.headers)
 observed=sha(b);results.append({'path':n,'expected':allfiles[n],'observed':observed,'passed':observed==allfiles[n],'etag':h.get('ETag'),'last_modified':h.get('Last-Modified')});attempt.write_text(json.dumps({'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':False,'assets':results},indent=2)+'\n');assert observed==allfiles[n],n
(d/'uploaded-engine-identity.json').write_bytes((u/'material-point-j2/identity.json').read_bytes());(d/'uploaded-package-manifest.json').write_bytes((u/'material-point-j2/package-manifest.json').read_bytes());(d/'live-assets.json').write_text(json.dumps({'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release':'8e060a425015d65ffe087243204d17b8dba62ab8','run':41299887463,'passed':True,'assets':results},indent=2)+'\n');print('PASS exact upload/live',len(results),'assets')
