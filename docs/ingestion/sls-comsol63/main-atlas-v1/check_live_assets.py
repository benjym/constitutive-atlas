"""Check main atlas against an explicitly supplied exact successful Pages upload."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('revision');p.add_argument('output',type=Path);a=p.parse_args();root=a.artifact
identity=json.loads((root/'engine-sls/identity.json').read_text());assert identity['release_revision']==a.revision
manifest=json.loads((root/'engine-sls/package-manifest.json').read_text());names=set(manifest['files'])|{'engine-sls/package-manifest.json','index.html','app.js','worker.js','catalogue.json','models.json','atlas.js','atlas.wasm','catalogue.mjs'}
assert not (root/'sls.html').exists()
rows=[]
for name in sorted(names):
 expected=hashlib.sha256((root/name).read_bytes()).hexdigest()
 if name in manifest['files']:assert expected==manifest['files'][name],name
 url='https://benjym.github.io/constitutive-atlas/'+name
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=60) as response:data=response.read();status=response.status
 actual=hashlib.sha256(data).hexdigest();assert status==200 and actual==expected,(name,status,actual,expected)
 rows.append(dict(path=name,url=url,status=status,bytes=len(data),sha256=actual))
a.output.write_text(json.dumps(dict(ok=True,revision=a.revision,identity=identity,assets=rows),indent=2)+'\n');print('PASS',len(rows),'exact live/upload asset comparisons',a.revision)
