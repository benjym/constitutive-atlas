import subprocess,json,hashlib,zipfile,tarfile
from pathlib import Path
root=Path('/private/tmp/ramberg-pages-ci-41357170257');root.mkdir(exist_ok=True)
evidence=Path(__file__).resolve().parent
raw=subprocess.check_output(['gh','api','repos/benjym/constitutive-atlas/actions/runs/41357170257/artifacts']);data=json.loads(raw)
a=next(x for x in data['artifacts'] if x['name']=='github-pages');assert a['workflow_run']['id']==41357170257 and a['workflow_run']['head_sha']=='ecd1f3b12381dd8edec34fe6121b80a0bd5792aa' and not a['expired']
(evidence/'github-artifact-api.json').write_bytes(raw)
z=root/'github-pages.zip'
with z.open('wb') as f:subprocess.run(['gh','api',f"repos/benjym/constitutive-atlas/actions/artifacts/{a['id']}/zip"],stdout=f,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert 'sha256:'+sha(z)==a['digest']
with zipfile.ZipFile(z) as f:
 assert f.namelist()==['artifact.tar'];f.extractall(root)
t=root/'artifact.tar';site=root/'site';site.mkdir(exist_ok=True)
with tarfile.open(t) as f:f.extractall(site,filter='data')
manifest={str(p.relative_to(site)):sha(p) for p in sorted(site.rglob('*')) if p.is_file()}
r={'run_id':41357170257,'head_sha':a['workflow_run']['head_sha'],'artifact':a,'zip_sha256':sha(z),'tar_sha256':sha(t),'extracted_manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),'files':len(manifest),'acquisition':'Authenticated gh api exact run artifacts; downloaded archive digest verified against API; sole artifact.tar extracted with tarfile data filter.','local_archive':str(z),'local_tar':str(t),'local_site':str(site)}
(evidence/'artifact-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
