"""Compare live public entry and ordinary engine assets to exact tested upload."""
import hashlib,json,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
artifact=Path('/private/tmp/sls-pages-extracted-f18')
proof=json.loads((HERE/'deployment-proof-v3.json').read_text())
assert proof['revision']=='f18db8e75d27cf182f2c03dfcd6534b7f51d5a86' and proof['status']=='success'
rows=[]
for name in ['index.html','app.js','worker.js','atlas.js','atlas.wasm','models.json','catalogue.json','catalogue.mjs']:
 url='https://benjym.github.io/constitutive-atlas/'+name
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=60) as response:
  data=response.read();status=response.status
 expected=hashlib.sha256((artifact/name).read_bytes()).hexdigest();actual=hashlib.sha256(data).hexdigest()
 assert status==200 and actual==expected,(name,status,actual,expected)
 rows.append(dict(path=name,url=url,status=status,bytes=len(data),sha256=actual))
result=dict(ok=True,revision=proof['revision'],assets=rows)
(HERE/'live-entry-verification-v3.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
