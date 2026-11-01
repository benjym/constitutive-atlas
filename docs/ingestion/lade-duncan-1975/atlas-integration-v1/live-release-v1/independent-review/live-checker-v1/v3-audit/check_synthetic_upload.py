"""Independent synthetic upload-chain mutations; no real artifact or material call."""
import hashlib,io,json,sys,tarfile,tempfile,types,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[2]/'check_live_v3.py'
code=SOURCE.read_bytes();c=types.ModuleType('reviewed_checker');c.__file__=str(SOURCE);exec(compile(code,str(SOURCE),'exec'),c.__dict__)
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(root,mutation=None):
 c.HERE=c.ROOT=root
 payloads={'app.js':b'app','engine-implicit-path/m.json':b'model','engine-implicit-path/review.json':b'review','engine-implicit-path/approval.json':b'approval','engine-implicit-path/lade-domain.mjs':b'module','engine-implicit-path/lade-domain.wasm':b'wasm','engine-implicit-path/models.json':b'catalogue'}
 identity={'release_revision':'a'*40,'model':'m','public_models':['m']}
 for name,key in [('m.json','model_sha256'),('review.json','review_sha256'),('approval.json','approval_sha256'),('lade-domain.mjs','module_sha256'),('lade-domain.wasm','wasm_sha256'),('models.json','catalogue_file_sha256')]:identity[key]=sha(payloads['engine-implicit-path/'+name])
 policy={'revision':'a'*40,'run':2,'artifact_name':'github-pages','model':'m','app_sha256':sha(b'app'),'required_live_paths':['app.js'],**{k:identity[k] for k in ['model_sha256','review_sha256','module_sha256','wasm_sha256']}}
 if mutation=='identity':identity['release_revision']='b'*40
 payloads['engine-implicit-path/identity.json']=json.dumps(identity).encode()
 payloads['engine-implicit-path/package-manifest.json']=json.dumps({'kind':'implicit-path-main-atlas-1','files':{n:sha(b) for n,b in payloads.items()}}).encode()
 with tarfile.open(root/'artifact.tar','w') as t:
  m=tarfile.TarInfo('./');m.type=tarfile.DIRTYPE;t.addfile(m)
  for n,b in payloads.items():m=tarfile.TarInfo('./'+n);m.size=len(b);t.addfile(m,io.BytesIO(b))
  if mutation=='duplicate':
   m=tarfile.TarInfo('app.js');m.size=3;t.addfile(m,io.BytesIO(b'app'))
  if mutation=='special':
   m=tarfile.TarInfo('sym');m.type=tarfile.SYMTYPE;m.linkname='app.js';t.addfile(m)
  if mutation=='traversal':
   m=tarfile.TarInfo('../escape');m.size=0;t.addfile(m,io.BytesIO())
 with zipfile.ZipFile(root/'artifact.zip','w') as z:
  z.write(root/'artifact.tar','artifact.tar')
  if mutation=='zip-extra':z.writestr('extra',b'x')
 zhash=sha((root/'artifact.zip').read_bytes());digest='sha256:'+zhash
 artifact={'id':1,'name':'github-pages','expired':False,'workflow_run':{'head_sha':'a'*40,'id':2},'digest':digest}
 acquisition={'artifact_id':1,'head_sha':'a'*40,'run':2,'artifact_tar_path':'artifact.tar','artifact_zip_path':'artifact.zip','api_digest':digest,'artifact_zip_sha256':zhash,'artifact_tar_sha256':sha((root/'artifact.tar').read_bytes())}
 if mutation=='run':artifact['workflow_run']['id']=3
 if mutation=='head':artifact['workflow_run']['head_sha']='b'*40
 if mutation=='api-digest':artifact['digest']='sha256:'+'0'*64
 if mutation=='tar-hash':acquisition['artifact_tar_sha256']='0'*64
 if mutation=='expired':artifact['expired']=True
 if mutation=='name':artifact['name']='other'
 artifacts=[artifact,artifact] if mutation=='metadata-duplicate' else [artifact]
 for name,d in [('LIVE_POLICY-v3.json',policy),('upload-acquisition.json',acquisition),('run-artifacts.json',{'artifacts':artifacts})]:(root/name).write_text(json.dumps(d))
checks=[]
for mutation in [None,'identity','duplicate','special','traversal','zip-extra','run','head','api-digest','tar-hash','expired','name','metadata-duplicate']:
 with tempfile.TemporaryDirectory(dir=HERE,prefix='synthetic-') as tmp:
  root=Path(tmp);fixture(root,mutation)
  try:c.upload_data()
  except (AssertionError,ValueError,KeyError):assert mutation is not None, 'valid root directory fixture rejected'
  else:assert mutation is None, 'invalid fixture accepted: '+str(mutation)
  checks.append({'mutation':mutation or 'valid-root-directory','passed':True})
for cap in ['MAX_ZIP','MAX_TAR','MAX_FILES','MAX_FILE']:
 with tempfile.TemporaryDirectory(dir=HERE,prefix='synthetic-cap-') as tmp:
  root=Path(tmp);fixture(root);previous=getattr(c,cap);setattr(c,cap,1)
  try:
   try:c.upload_data()
   except (AssertionError,ValueError):pass
   else:raise AssertionError('limit not enforced: '+cap)
  finally:setattr(c,cap,previous)
  checks.append({'mutation':'cap-'+cap,'passed':True})
assert not c.equal(c.parse('-0'),c.parse('0'))
for token in ['1e999','-1e999','9'*400]:
 try:c.parse(token)
 except ValueError:pass
 else:raise AssertionError('nonfinite token admitted')
checks.append({'mutation':'strict-literal-number-parser','passed':True})
result={'reviewed_source_sha256':sha(code),'checks':checks,'scope':'synthetic owned files only; no saved CI/live artifact read'}
(HERE/'synthetic-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
