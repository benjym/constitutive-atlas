"""Compare the actual tested Pages upload with live public assets, without cache reuse."""
from pathlib import Path
import argparse,hashlib,json,urllib.request,datetime
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--base',required=True);p.add_argument('--revision',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
identity=json.loads((a.package/'engine-burgers/identity.json').read_text());assert identity['release_revision']==a.revision
manifest=json.loads((a.package/'engine-burgers/package.json').read_text())['files']
for name,digest in manifest.items():assert hashlib.sha256((a.package/name).read_bytes()).hexdigest()==digest,name
assert identity['model_sha256']=='1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c'
names=set(manifest)
names.update(p.name for p in a.package.glob('*.mjs'))
names.update(['worker.js','formulation-view.mjs'])
names.update(['index.html','app.js','style.css','timed-route.mjs','models.json','catalogue.json','atlas.js','atlas.wasm','recorded.mjs','numerics.mjs','loading.mjs','engine-burgers/package.json','engine-burgers/identity.json','docs/models/burgers-main-laboratory-v1.md.html','models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json'])
rows=[]
for name in sorted(names):
 expected=(a.package/name).read_bytes();url=a.base.rstrip('/')+'/'+name+'?release-check='+a.revision
 req=urllib.request.Request(url,headers={'Cache-Control':'no-cache','User-Agent':'Constitutive-Atlas-release-check'})
 with urllib.request.urlopen(req,timeout=60) as response:actual=response.read();status=response.status
 row=dict(path=name,status=status,upload_sha256=hashlib.sha256(expected).hexdigest(),live_sha256=hashlib.sha256(actual).hexdigest(),bytes=len(actual))
 rows.append(row);assert actual==expected,(name,row)
assert hashlib.sha256((a.package/'engine-burgers/burgers.wasm').read_bytes()).hexdigest()==identity['wasm_sha256']
a.output.write_text(json.dumps(dict(revision=a.revision,checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),base=a.base,identity=identity,assets=rows,all_equal=True),indent=2)+'\n')
print(json.dumps(dict(revision=a.revision,assets=len(rows),all_equal=True)))
