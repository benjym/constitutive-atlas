"""One serial standalone backend build and literal request execution per identity."""
from pathlib import Path
import sys,subprocess,json,hashlib,gzip,os,time
from datetime import datetime,timezone
import study
P=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def verify():
 for n,h in study.load(P/'prospective-freeze.json')['files'].items():assert sha(P/n)==h,n

def main(role):
 assert role in ('native','wasm');verify();out=P/role;assert not out.exists();out.mkdir()
 build=Path('/private/tmp/atlas-spectral-primitive-'+role+'-v1');assert not build.exists(),build
 env=dict(os.environ,EMCC_CORES='1')
 commands=[['cmake','-S',str(P),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(build),'--target','atlas_spectral_study','--parallel','1']]
 if role=='wasm':commands[0].insert(0,'emcmake')
 record={'role':role,'started':now(),'freeze_sha256':sha(P/'prospective-freeze.json'),'commands':commands,'compiled_calls':0}
 for name,command in zip(('configure','build'),commands):
  print(role,name,'started',flush=True);start=now();r=subprocess.run(command,env=env,capture_output=True,text=True)
  (out/(name+'.stdout.txt')).write_text(r.stdout);(out/(name+'.stderr.txt')).write_text(r.stderr)
  record[name]={'started':start,'finished':now(),'returncode':r.returncode}
  (out/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
  if r.returncode:return r.returncode
 command=[str(build/'atlas_spectral_study')]if role=='native'else['node',str(build/'spectral-study.js')]
 artifacts=[build/'atlas_spectral_study']if role=='native'else[build/'spectral-study.js',build/'spectral-study.wasm']
 record['artifacts']={str(p):sha(p)for p in artifacts};record['runtime_command']=command
 requests=study.load(P/'requests.json.gz');payload=study.payload(requests).encode();record['request_payload_sha256']=hashlib.sha256(payload).hexdigest()
 record['runtime_started']=now();print(role,'literal requests',len(requests),flush=True)
 r=subprocess.run(command,input=payload,capture_output=True);record['runtime_finished']=now();record['runtime_returncode']=r.returncode;record['compiled_calls']=len(requests)
 (out/'responses.jsonl.gz').write_bytes(gzip.compress(r.stdout,mtime=0));(out/'runtime.stderr.txt').write_bytes(r.stderr)
 record['finished']=now();(out/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
 if r.returncode:return r.returncode
 try:
  rows=[json.loads(line,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite JSON:'+x)))for line in r.stdout.splitlines()]
  assessment=study.assess(rows)
 except Exception as e:
  (out/'assessment-error.txt').write_text(type(e).__name__+': '+str(e)+'\n');raise
 (out/'assessment.json').write_text(json.dumps(assessment,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'role':role,'requests':assessment['requests'],'passed':assessment['passed'],'failures':len(assessment['failures']),'worst_error_fraction':assessment['worst_error_fraction']},sort_keys=True),flush=True)
 return 0 if assessment['passed']else 1
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
