"""Acquire exact trusted-run upload and compare public bytes; no compiled calls."""
from pathlib import Path
import hashlib,json,tarfile,urllib.request,datetime,shutil,sys,zipfile
D=Path(__file__).resolve().parent; ROOT=D.parents[4]
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main(download):
 policy=read(D/'POLICY.json');meta=read(D/'run-artifacts.json');matches=[a for a in meta['artifacts']if a['name']=='github-pages'];assert len(matches)==1
 a=matches[0];assert a['workflow_run']['id']==policy['run'] and a['workflow_run']['head_sha']==policy['release'] and not a['expired']
 archive_zip=Path(download);zip_sha=sha(archive_zip.read_bytes());assert a['digest']=='sha256:'+zip_sha
 private=ROOT/'.local/private-evidence/occ-live-v1';private.mkdir(parents=True,exist_ok=True);zip_target=private/(zip_sha+'.zip');shutil.copyfile(archive_zip,zip_target)
 with zipfile.ZipFile(zip_target)as z:
  names=[n for n in z.namelist()if not n.endswith('/')];assert names==['artifact.tar'];tar_bytes=z.read('artifact.tar')
 target=private/(sha(tar_bytes)+'.tar');target.write_bytes(tar_bytes)
 with tarfile.open(target)as t:
  members=t.getmembers();assert all(m.isfile()or m.isdir()for m in members)
  assert all(not Path(m.name).is_absolute()and '..'not in Path(m.name).parts for m in members)
  files=[m for m in members if m.isfile()];assert len(files)==len({m.name.removeprefix('./')for m in files})
  inventory={m.name.removeprefix('./'):sha(t.extractfile(m).read())for m in files}
 dump(D/'upload-acquisition.json',dict(run=policy['run'],release=policy['release'],artifact_id=a['id'],artifact_name=a['name'],api_digest=a['digest'],zip_sha256=zip_sha,private_zip_path=str(zip_target.relative_to(ROOT)),private_artifact_path=str(target.relative_to(ROOT)),tar_sha256=sha(target.read_bytes()),download_command=f"gh api repos/benjym/constitutive-atlas/actions/artifacts/{a['id']}/zip > {download}"))
 dump(D/'upload-inventory.json',inventory)
 rows=[];attempt=D/f"live-assets-attempt-{len(list(D.glob('live-assets-attempt-*.json')))+1}.json"
 for name in policy['assets']:
  expected=inventory[name];req=urllib.request.Request(policy['base_url']+name,headers={'Cache-Control':'no-cache','User-Agent':'ConstitutiveAtlasReleaseVerification'})
  with urllib.request.urlopen(req,timeout=45)as response:body=response.read();headers=dict(response.headers);status=response.status
  rows.append(dict(path=name,status=status,expected=expected,observed=sha(body),passed=status==200 and sha(body)==expected,etag=headers.get('ETag'),last_modified=headers.get('Last-Modified')))
  dump(attempt,dict(date_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),run=policy['run'],release=policy['release'],complete=False,assets=rows));assert rows[-1]['passed'],name
 dump(D/'live-assets.json',dict(date_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),run=policy['run'],release=policy['release'],passed=True,assets=rows))
 print('PASS upload/live',len(rows),'assets')
if __name__=='__main__':main(sys.argv[1])
