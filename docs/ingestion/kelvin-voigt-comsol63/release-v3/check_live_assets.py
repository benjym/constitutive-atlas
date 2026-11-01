"""Compare the public Pages response bytes to the exact tested upload."""
import argparse,concurrent.futures,hashlib,json,urllib.request,urllib.parse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
base='https://benjym.github.io/constitutive-atlas/'
files=sorted(x for x in a.artifact.rglob('*') if x.is_file())
def check(path):
 rel=path.relative_to(a.artifact).as_posix();expected=hashlib.sha256(path.read_bytes()).hexdigest()
 request=urllib.request.Request(base+urllib.parse.quote(rel),headers={'Cache-Control':'no-cache','User-Agent':'Constitutive-Atlas-release-verification'})
 try:
  with urllib.request.urlopen(request,timeout=45) as response:
   data=response.read();actual=hashlib.sha256(data).hexdigest();status=response.status
  return {'path':rel,'expected_sha256':expected,'actual_sha256':actual,'bytes':len(data),'status':status,'passed':actual==expected and status==200}
 except Exception as e:return {'path':rel,'expected_sha256':expected,'passed':False,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(check,files))
x={'passed':all(x['passed'] for x in results),'source':'exact github-pages upload from workflow41357170257/applicationecd1f3b1','base_url':base,'assets':len(results),'failures':[x for x in results if not x['passed']],'results':results}
a.output.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({k:v for k,v in x.items() if k!='results'}));raise SystemExit(not x['passed'])
