from pathlib import Path
import json,hashlib,subprocess,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];policy=json.loads((HERE/'POLICY.json').read_text());local=ROOT/'.local/lade-internal-cost-v1';local.mkdir(exist_ok=True)
assert hashlib.sha256(Path(policy['baseline_exe']).read_bytes()).hexdigest()==policy['baseline_exe_sha256']
records=[]
def run(name,command,exe):
 cmd=command.copy();cmd[0]=exe;started=time.monotonic();r={'name':name,'command':cmd,'timeout':False,'exe_sha256':hashlib.sha256(Path(exe).read_bytes()).hexdigest()}
 try:
  p=subprocess.run(cmd,capture_output=True,timeout=policy['timeout_seconds']);out,err=p.stdout,p.stderr;r['returncode']=p.returncode
 except subprocess.TimeoutExpired as e:out,err=e.stdout or b'',e.stderr or b'';r['timeout']=True
 for suffix,data in [('stdout',out),('stderr',err)]:
  path=local/f'{name}.{suffix}';path.write_bytes(data);r[suffix]={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest()}
 r['elapsed_seconds']=time.monotonic()-started;records.append(r);(HERE/'RESULTS.json').write_text(json.dumps({'diagnostic_only':True,'records':records},indent=2)+'\n');return json.loads(out) if not r['timeout'] and out else None
baseline=run('short-baseline',policy['short_command'],policy['baseline_exe']);candidate=run('short-instrumented',policy['short_command'],policy['candidate_exe'])
def normalized(x):
 if not isinstance(x,dict):return x
 x=x.copy();x.pop('elapsed_ms',None);return x
fidelity=baseline is not None and baseline.get('ok') is True and normalized(baseline)==normalized(candidate)
if fidelity:run('long-instrumented',policy['long_command'],policy['candidate_exe'])
(HERE/'RESULTS.json').write_text(json.dumps({'diagnostic_only':True,'not_qualification':True,'fidelity_passed':fidelity,'records':records},indent=2)+'\n');print(json.dumps({'fidelity_passed':fidelity,'records':[{k:v for k,v in r.items() if k not in ['command']} for r in records]},indent=2));raise SystemExit(0 if fidelity else 1)
