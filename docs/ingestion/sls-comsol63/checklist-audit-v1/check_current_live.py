"""Fetch the SLS live package again; compare to the qualified upload."""
import hashlib,json,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent;artifact=Path('/private/tmp/sls-pages-extracted-f18')
manifest=json.loads((artifact/'engine-sls/package-manifest.json').read_text());names=list(manifest)+['engine-sls/package-manifest.json'];rows=[]
for name in names:
 url='https://benjym.github.io/constitutive-atlas/'+name
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=60) as response:data=response.read();status=response.status
 actual=hashlib.sha256(data).hexdigest();expected=hashlib.sha256((artifact/name).read_bytes()).hexdigest()
 assert actual==expected and status==200,(name,status,actual,expected)
 rows.append(dict(path=name,status=status,sha256=actual,bytes=len(data)))
print(json.dumps(dict(ok=True,assets=rows,qualified_revision='f18db8e75d27cf182f2c03dfcd6534b7f51d5a86'),indent=2))
