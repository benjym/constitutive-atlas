"""Fresh saved-data dispatch to frozen assessment/parity code; no artifact calls."""
import argparse,ast,importlib.util,json,os,sys,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;S=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve();p=argparse.ArgumentParser();p.add_argument('profile',choices=['burgers','orthotropic']);p.add_argument('native',type=Path);p.add_argument('wasm',type=Path);p.add_argument('output',type=Path);a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(S)
sys.path.insert(0,str(S));read=lambda p:json.loads(p.read_text());n,w=read(a.native),read(a.wasm)
if a.profile=='burgers':
 sys.path.insert(0,str(D/'adapters'));sys.path.insert(1,str(S/'docs/ingestion/burgers-itasca900/integration-v1'));import study
 original=ast.parse((D/'burgers-original-verify.py').read_text());fn=next(x for x in original.body if isinstance(x,ast.FunctionDef)and x.name=='parity');import math;env={'math':math};exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen-burgers-parity','exec'),env)
 class Replay:
  def __init__(self,rows):self.rows=rows;self.calls=[]
  def call(self,label,function,args,command):
   row=self.rows[len(self.calls)];assert(label,function,args)==(row['label'],row['function'],row['args']);self.calls.append(row);return row['response']
 for rows in [n,w]:
  replay=Replay(rows);study.execute(replay);assert len(replay.calls)==len(rows)
 report={'native':study.assess(n),'wasm':study.assess(w),'parity':env['parity'](n,w),'complete_request_replay':True}
else:
 from tools.orthotropic_reference import assess
 cases=read(S/'docs/ingestion/orthotropic-ogs/execution-v1/references.json')['cases'];report={'native':assess(cases,n),'wasm':assess(cases,w)};assert len(n)==len(w)==len(cases)
 delta=0
 for left,right in zip(n,w):
  assert left['id']==right['id'];x,y=left['response'],right['response'];assert x['ok']==y['ok']
  if x['ok']:
   assert x['diagnostics']['increment_fractions']==y['diagnostics']['increment_fractions'];delta=max(delta,max(abs(v-u)for v,u in zip(x['state'],y['state'])))
 report['paired']={'cases':len(cases),'same_ok_and_partitions':True,'maximum_state_difference_Pa_diagnostic':delta,'gate':'both unchanged per-case source-reference assessments; no added numerical tolerance'}
a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps(report))
