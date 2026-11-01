"""Compare live transport bytes with the tested Pages upload, never local build output."""
from pathlib import Path
import hashlib,json,sys,urllib.request
packet=Path(__file__).resolve().parent
site=Path(sys.argv[1]).resolve()
base='https://benjym.github.io/constitutive-atlas/'
paths=['index.html','app.js','atlas.js','atlas.wasm','models.json','catalogue.json','atlas-database.json','models/duncan-chang-1970-endpoint-average.json','evidence-records/catalogue/agent-reviews/duncan-chang-1970-endpoint-average-agent-v1.json','evidence-records/catalogue/agent-reviews/definitions/duncan-chang-1970-endpoint-average-agent-v1.json','evidence-records/catalogue/approved-models.json','docs/models/duncan-chang-1970-endpoint-average.md.html']
rows=[]
for name in paths:
 req=urllib.request.Request(base+name+'?duncan_release=b529a0ef',headers={'Cache-Control':'no-cache'})
 with urllib.request.urlopen(req,timeout=60) as response:
  data=response.read();status=response.status
 expected=(site/name).read_bytes();row={'path':name,'status':status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'upload_sha256':hashlib.sha256(expected).hexdigest(),'matches_upload':status==200 and data==expected};rows.append(row)
result={'source_commit':'b529a0efc3415b2bc567178a68174575c220cadc','run_id':41337427969,'origin':base,'status':'PASS' if all(x['matches_upload'] for x in rows) else 'FAIL','assets':rows}
(packet/'live-http-assets-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows),'live/upload assets');assert result['status']=='PASS'
