"""Preserve standalone native/Wasm fixture raw responses; coordinator only."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def preflight():
 for n,h in json.loads((D/'manifest.json').read_text()).items():assert sha(D/n)==h,n
 freeze=json.loads((D/'source-freeze.json').read_text())
 for n,h in freeze['source_files'].items():assert sha(Path(freeze['source_directory'])/n)==h,n
 return {'manifest_sha256':sha(D/'manifest.json'),'source_freeze_sha256':sha(D/'source-freeze.json'),'cases_sha256':sha(D/'cases.json'),'source_files':len(freeze['source_files'])}
if __name__=='__main__':
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--solver');g.add_argument('--engine');p.add_argument('--output',required=True);a=p.parse_args();binding=preflight();out=Path(a.output);out.mkdir(parents=True,exist_ok=False);artifact=Path(a.solver or a.engine).resolve();binding.update(backend='native' if a.solver else 'wasm',artifact_path=str(artifact),artifact_sha256=sha(artifact));calls=[];commands=[]
 if a.engine:binding.update(wasm_path=str(artifact.with_suffix('.wasm')),wasm_sha256=sha(artifact.with_suffix('.wasm')))
 try:
  for repeat in range(2 if a.solver else 1):
   cmd=[str(artifact)] if a.solver else ['node',str(D/'collect_wasm.mjs'),str(artifact)]
   try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
   except subprocess.TimeoutExpired as failure:
    def decoded(v):return v.decode(errors='replace') if isinstance(v,bytes) else v
    commands.append({'command':cmd,'returncode':None,'timeout':True,'stdout':decoded(failure.stdout),'stderr':decoded(failure.stderr)});(out/'processes.json').write_text(json.dumps(commands,indent=2)+'\n');raise
   commands.append({'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'processes.json').write_text(json.dumps(commands,indent=2)+'\n')
   if a.solver:calls.append({'repeat':repeat,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
   else:
    for line in r.stdout.splitlines():calls.append(json.loads(line))
 finally:
  for call in calls:
   try:call['response']=json.loads(call['stdout'],parse_constant=lambda token:(_ for _ in()).throw(ValueError(token)))
   except Exception as failure:call['parse_error']=str(failure)
  (out/'report.json').write_text(json.dumps({'identity':binding,'calls':calls},indent=2,allow_nan=False)+'\n')
 print(json.dumps({'raw_calls':len(calls),'output':str(out)}))
