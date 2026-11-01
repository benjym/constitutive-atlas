from pathlib import Path
import json,hashlib,subprocess,time
from fidelity import parse_response,same_response
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];policy=json.loads((HERE/'FIDELITY_POLICY.json').read_text());local=ROOT/'.local/lade-outer-reuse-v1';records=[]
assert hashlib.sha256(Path(policy['baseline_exe']).read_bytes()).hexdigest()==policy['baseline_exe_sha256']
def run(case,kind,exe):
 cmd=case['command'].copy();cmd[0]=exe;t=time.monotonic();r={'name':case['name'],'kind':kind,'command':cmd,'timeout':False,'exe_sha256':hashlib.sha256(Path(exe).read_bytes()).hexdigest()}
 try:
  result=subprocess.run(cmd,capture_output=True,timeout=policy['timeout_seconds']);out,err=result.stdout,result.stderr;r['returncode']=result.returncode
 except subprocess.TimeoutExpired as e:r['timeout']=True;out,err=e.stdout or b'',e.stderr or b''
 for suffix,data in [('stdout',out),('stderr',err)]:
  path=local/f"fidelity-{case['name']}-{kind}.{suffix}";path.write_bytes(data);r[suffix]={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest()}
 r['elapsed_seconds']=time.monotonic()-t;records.append(r);(HERE/'fidelity-results.json').write_text(json.dumps({'passed':False,'records':records},indent=2)+'\n')
 return parse_response(out) if not r['timeout'] and r.get('returncode')==0 and out else None
passed=True
for case in policy['cases']:
 a=run(case,'baseline',policy['baseline_exe']);b=run(case,'reuse',policy['candidate_exe']);ok=isinstance(a,dict) and isinstance(b,dict) and a.get('ok') is True and b.get('ok') is True and same_response(a,b);records[-1]['pair_exact']=ok;passed=passed and ok
 if not ok:break
(HERE/'fidelity-results.json').write_text(json.dumps({'passed':passed,'records':records},indent=2)+'\n');print(json.dumps({'passed':passed,'requests':len(records)}));raise SystemExit(0 if passed else 1)
