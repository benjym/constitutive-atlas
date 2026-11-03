from pathlib import Path
import tarfile,hashlib,json,sys
archive=Path(sys.argv[1]);out=Path(sys.argv[2]);assert not out.exists()
files={};sizes={}
with tarfile.open(archive,'r:*') as tf:
 for member in tf:
  if member.isdir():continue
  assert member.isfile(),member.name
  name=member.name.removeprefix('./');assert name and not name.startswith('/') and '..' not in Path(name).parts and name not in files,name
  b=tf.extractfile(member).read();files[name]=hashlib.sha256(b).hexdigest();sizes[name]=len(b)
required=['index.html','app.js','plot-labels.mjs','model-profile-data.mjs','model-profiles.mjs','catalogue.json','models.json','atlas.js','atlas.wasm','engine-controlled-time/model.json','engine-controlled-time/identity.json','engine-controlled-time/review.json','engine-controlled-time/approval.json','engine-controlled-time/package-manifest.json']
assert all(n in files for n in required)
report={'revision':sys.argv[3],'pages_run':int(sys.argv[4]),'archive_path':str(archive),'archive_sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'files':files,'bytes':sum(sizes.values())}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2));print('Files:',len(files))
