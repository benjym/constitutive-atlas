"""Compare all non-experiment public upload files to Pages; no material execution."""
import concurrent.futures,hashlib,json,urllib.request,urllib.parse,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE="https://benjym.github.io/constitutive-atlas/"
HEAD="43ea5c45f0e6112661fe996b685a3adcdac12ce6"
m=json.loads((HERE/"UPLOAD-MANIFEST.json").read_text());assert m["source_revision"]==HEAD
selected={n:v for n,v in m["files"].items() if not n.startswith("experiments/") and n!=".nojekyll"}
def check(item):
 n,v=item;url=BASE+urllib.parse.quote(n,safe="/")
 try:
  req=urllib.request.Request(url,headers={"Cache-Control":"no-cache","User-Agent":"Constitutive-Atlas-release-verification"})
  with urllib.request.urlopen(req,timeout=60) as r:
   h=hashlib.sha256();size=0
   while chunk:=r.read(1024*1024):h.update(chunk);size+=len(chunk)
   actual=h.hexdigest();return {"path":n,"url":url,"status":r.status,"expected_sha256":v["sha256"],"actual_sha256":actual,"bytes":size,"passed":r.status==200 and actual==v["sha256"] and size==v["bytes"]}
 except Exception as e:return {"path":n,"url":url,"passed":False,"error":type(e).__name__+": "+str(e)}
start=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,selected.items()))
out={"kind":"bingham-live-tested-upload-comparison-v1","source_revision":HEAD,"base":BASE,"selected_files":len(rows),"excluded":"Large unrelated experiments/ payloads and deployment marker .nojekyll; all retained in full authenticated upload manifest. Every other public upload file is checked.","elapsed_seconds":time.time()-start,"passed":all(x["passed"] for x in rows),"files":rows}
(HERE/"LIVE-UPLOAD-COMPARISON.json").write_text(json.dumps(out,indent=2)+"\n");print(json.dumps({k:v for k,v in out.items() if k!="files"}));raise SystemExit(0 if out["passed"] else 1)
