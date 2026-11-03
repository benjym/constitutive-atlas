"""Read-only live asset verification against the actual tested Pages tar upload."""
from pathlib import Path,PurePosixPath
import concurrent.futures,datetime,hashlib,json,sys,tarfile,urllib.request
OUT=Path(__file__).resolve().parent
archive=Path(sys.argv[1]).resolve();base='https://benjym.github.io/constitutive-atlas/'
assert not (OUT/'live-assets.json').exists(), 'Use a fresh verification identity for revised observations'
sha=lambda b:hashlib.sha256(b).hexdigest()
selected=['index.html','app.js','model-profile-data.mjs','model-profiles.mjs','models.json','catalogue.json','atlas.js','atlas.wasm','laboratory-control-support.json','evidence.json','applicability.json','models/s-clay1.json','evidence-records/catalogue/agent-reviews/s-clay1-agent-v1.json','evidence-records/catalogue/approved-models.json','docs/models/s-clay1.md.html','atlas-database.json','atlas.sqlite']
manifest={};payload={}
with tarfile.open(archive) as tar:
 for member in tar:
  if not member.isfile():continue
  name=PurePosixPath(member.name).as_posix().removeprefix('./');assert not name.startswith('/') and '..' not in PurePosixPath(name).parts
  raw=tar.extractfile(member).read();manifest[name]={'sha256':sha(raw),'bytes':len(raw)}
  if name in selected:payload[name]=raw
assert set(selected)<=payload.keys()
(OUT/'tested-upload-files.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert sha(payload['models/s-clay1.json'])=='2d1518c1aee44d9adec35229adc83b32a9f39d9175f307c8ddfd90cdfbd1caec'
assert sha(payload['evidence-records/catalogue/agent-reviews/s-clay1-agent-v1.json'])=='a144221194a97861bb91900108471c668c5e9fe98ee6bf5bd2a2e2a1c80f0a48'
assert 's-clay1' in [m['id'] for m in json.loads(payload['models.json'])['models']]

def fetch(name):
 req=urllib.request.Request(base+name,headers={'Cache-Control':'no-cache','User-Agent':'Constitutive-Atlas-release-verification'})
 with urllib.request.urlopen(req,timeout=60) as response:
  raw=response.read();row={'path':name,'url':response.url,'status':response.status,'sha256':sha(raw),'bytes':len(raw),'expected_sha256':manifest[name]['sha256']};row['matches_tested_upload']=raw==payload[name];return row
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,selected))
report={'application_revision':'ac22788b918a47c837e61ddd76bde5894b35cc5e','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tested_upload':str(archive),'tested_upload_sha256':sha(archive.read_bytes()),'assets':rows,'passed':all(r['status']==200 and r['matches_tested_upload'] for r in rows),'browser_run_verified':False}
(OUT/'live-assets.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['passed'], 'Live deployment differs from tested upload; preserve this attempt'
print(json.dumps({'passed':True,'assets':len(rows),'upload_files':len(manifest),'catalogue_hash':json.loads(payload['models.json'])['sha256']}))
