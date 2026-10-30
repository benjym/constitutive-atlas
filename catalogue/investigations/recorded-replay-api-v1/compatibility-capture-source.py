import json,subprocess,gzip,hashlib
from pathlib import Path
old=Path('/private/tmp/atlas-browser-settings/native-solver');new=Path('/private/tmp/atlas-recorded-cmake/atlas_solver')
ids=subprocess.check_output([str(old),'--list'],text=True).splitlines();rows=[]
def run(binary,args):
 p=subprocess.run([str(binary),*args],capture_output=True,text=True,timeout=60)
 d=json.loads(p.stdout);d.pop('elapsed_ms',None)
 return dict(returncode=p.returncode,stderr=p.stderr,response=d)
cases=[['--describe']]
for model in ids:
 for protocol in range(1,6):cases.append(['--model',model,'--protocol',str(protocol),'--target','.001','--steps','8'])
 for mode in ['integrate','linearize']:
  cases.append(['--mode',mode,'--model',model,'--strain','.0001,0,0,0,0,0'])
  cases.append(['--mode',mode,'--model',model,'--strain','.0001,0,0,0,0,0','--integration-settings','2e-10,1e-7,45,14,20000,11'])
for args in cases:
 a,b=run(old,args),run(new,args)
 assert a==b,args
 rows.append(dict(argv=args,prior=a,current=b))
out=Path('/private/tmp/atlas-recorded-api-stage')
(out/'compatibility.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
result=dict(ok=True,cases=len(rows),models=ids,excluded_fields=['elapsed_ms'],prior_binary_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),new_binary_sha256=hashlib.sha256(new.read_bytes()).hexdigest())
(out/'compatibility-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
