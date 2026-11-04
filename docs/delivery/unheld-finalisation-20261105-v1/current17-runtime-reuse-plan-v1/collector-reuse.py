"""Prospective source/artifact binding and serial collection. Execution needs separate handoff."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import selectors
import subprocess
import sys
import traceback
import tempfile

HERE=Path(__file__).resolve().parent
MODELS=['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']
GATES=[('elasticity','tools/verify_elasticity.py',None),('vw96','tools/verify_hypoplasticity.py',None),('igs97','tools/verify_igs.py',None),('mcc','tools/verify_plasticity.py','modified-cam-clay')]
DP='catalogue/investigations/dp-dilatancy-domain-v1'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def csv(v):return ','.join(format(x,'.17g') for x in v)
def pin(p):p=Path(p).resolve();return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def verify(p):
 q=Path(p['path']);assert q.stat().st_size==p['bytes'] and sha(q)==p['sha256'],p['path']
def source_files(repo):
 paths={repo/'CMakeLists.txt',repo/DP/'cases.json',repo/DP/'run_study.py',repo/DP/'prospective-freeze.json'}
 for directory in ['atlas','cpp','models','schemas','cmake','tools']:
  paths.update(p for p in (repo/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != '.DS_Store')
 paths.update(repo/p for _,p,_ in GATES)
 # The old DP saved assessor verifies its whole immutable original freeze itself.
 paths.update(repo/DP/f for f in json.loads((repo/DP/'prospective-freeze.json').read_text())['files'])
 return sorted(paths)

REVISION='64002531f0af5c06ad0402d0d80548102f8e6a38'
REUSE_ID='baseline-five-current17-reused-execution-freeze-v1'

def source_map(repo):
 return {str(p.relative_to(repo)):sha(p) for p in source_files(repo)}

def validate_handoff(repo,handoff,review):
 """Existing-build authority remains genuine, reviewed, and distinct from v5 prebuild."""
 h=json.loads(Path(handoff['path']).read_text());r=json.loads(Path(review['path']).read_text())
 verify(handoff);verify(review)
 assert h['identity']=='baseline-five-current17-existing-build-handoff-v1'
 assert h['revision']==REVISION and h['source_sha256']==source_map(repo)
 assert r['decision']=='accepted' and r['handoff_sha256']==handoff['sha256']
 assert r.get('author_run') and r.get('reviewer_run') and r['author_run']!=r['reviewer_run']
 assert r['unresolved_blockers']==[] and r['existing_build_provenance_accepted'] is True
 assert set(h['artifacts'])=={'native','module','wasm','node'}
 assert set(h['builds'])==set(h['generated'])=={'native','wasm'}
 assert set(h['build_tools'])=={'cmake','native_cxx','emcmake','emcc'}
 items=[*h['artifacts'].values(),*h['build_tools'].values(),*h['raw_provenance']]
 assert h['raw_provenance'],'genuine source-to-build receipts/logs required'
 definitions=[]
 for backend in ['native','wasm']:
  b=h['builds'][backend];assert b['returncode']==0
  argv=b['argv'];assert '--build' in argv and argv[argv.index('--target')+1]=='atlas_solver' and argv[argv.index('--parallel')+1]=='1'
  assert b['configure_returncode']==0 and b['logs'] and b['compiler_version_logs']
  items.extend([*b['logs'],*b['compiler_version_logs'],b['resolved_compiler']])
  g=h['generated'][backend];assert set(g)=={'header','json'}
  items.extend(g.values());verify(g['json'])
  d=json.loads(Path(g['json']['path']).read_text());models=d['models'];assert len(models)==17 and len({m['id'] for m in models})==17
  policy=json.loads((HERE/'policy.json').read_text())
  for model,expected in policy['candidate_sha256'].items():
   assert sha(repo/'models'/f'{model}.json')==expected
   assert next(m for m in models if m['id']==model)==json.loads((repo/'models'/f'{model}.json').read_text())
  definitions.append(d)
 assert definitions[0]==definitions[1],'generated native/Wasm catalogues differ'
 assert h['generated']['native']['header']['sha256']==h['generated']['wasm']['header']['sha256']
 for item in items:verify(item)
 return h

def reuse_freeze(a):
 repo=a.repo.resolve();assert not a.output.exists(),'never overwrite a reuse freeze'
 assert sha(a.handoff)==a.handoff_sha256 and sha(a.review)==a.review_sha256
 handoff=pin(a.handoff);review=pin(a.review);h=validate_handoff(repo,handoff,review)
 policy=json.loads((HERE/'policy.json').read_text())
 for path,expected in policy['unchanged_gate_sha256'].items():assert sha(repo/path)==expected
 candidates={model:pin(repo/'models'/f'{model}.json') for model in MODELS}
 for model,p in candidates.items():assert p['sha256']==policy['candidate_sha256'][model]
 plan=[HERE/'collector-reuse.py',HERE/'wasm-cli.mjs',HERE/'policy.json',HERE/'GATES.json']
 inputs=source_files(repo)+plan+[a.handoff.resolve(),a.review.resolve()]
 data={'identity':REUSE_ID,'revision':REVISION,'repo':str(repo),'source_inventory':[pin(p) for p in source_files(repo)],'candidates':candidates,'inputs':[pin(p) for p in inputs],'artifacts':h['artifacts'],'python':pin(sys.executable),'python_version':platform.python_version(),'platform':platform.platform(),'policy':policy,'compiled_observations':False,'handoff':handoff,'handoff_review':review}
 validate_execution_freeze(data);write(a.output,data)

def validate_execution_freeze(f):
 repo=Path(f['repo']);assert f['identity']==REUSE_ID and f['revision']==REVISION and f['compiled_observations'] is False
 assert f['policy']==json.loads((HERE/'policy.json').read_text())
 h=validate_handoff(repo,f['handoff'],f['handoff_review'])
 assert f['artifacts']==h['artifacts'] and set(f['candidates'])==set(MODELS)
 files=source_files(repo);assert f['source_inventory']==[pin(p) for p in files]
 plan=[HERE/'collector-reuse.py',HERE/'wasm-cli.mjs',HERE/'policy.json',HERE/'GATES.json']
 expected=files+plan+[Path(f[key]['path']) for key in ['handoff','handoff_review']]
 assert f['inputs']==[pin(p) for p in expected]
 for item in [*f['inputs'],*f['artifacts'].values(),f['python']]:verify(item)
 for model,expected in f['policy']['candidate_sha256'].items():assert f['candidates'][model]==pin(repo/'models'/f'{model}.json') and f['candidates'][model]['sha256']==expected
 for path,expected in f['policy']['unchanged_gate_sha256'].items():assert sha(repo/path)==expected


class Transport:
 def __init__(self,freeze,backend,out):
  self.freeze=freeze;self.backend=backend;self.out=out;self.calls=[];self.stage='describe';self.child=None;self.stderr=None
  if backend=='wasm':
   art=freeze['artifacts'];self.stderr=(out/'wasm-process.stderr').open('w')
   self.process_argv=[art['node']['path'],str(HERE/'wasm-cli.mjs'),art['module']['path'],art['wasm']['path'],'--serve']
   self.child=subprocess.Popen(self.process_argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True,cwd=freeze['repo'])
 def close(self):
  if self.child:
   self.child.stdin.close()
   try:self.child.wait(timeout=10)
   except subprocess.TimeoutExpired:
    self.child.terminate()
    try:self.child.wait(timeout=10)
    except subprocess.TimeoutExpired:self.child.kill();self.child.wait(timeout=10)
   self.stderr.close()
   assert self.child.returncode==0,'Wasm transport exit failure'

 def run(self,command,**kwargs):
  # All unchanged gates may select only the already-bound native pseudo-solver.
  assert str(command[0])==self.freeze['artifacts']['native']['path']
  args=list(map(str,command[1:]));art=self.freeze['artifacts']
  argv=[art['native']['path'],*args] if self.backend=='native' else [art['node']['path'],str(HERE/'wasm-cli.mjs'),art['module']['path'],art['wasm']['path'],*args]
  record={'sequence':len(self.calls),'stage':self.stage,'arguments':args,'command':self.process_argv if self.child else argv,'transport':'persistent-wasm-public-api' if self.child else 'native-cli-process'}
  self.calls.append(record)
  try:
   if self.child:
    self.child.stdin.write(json.dumps(args)+'\n');self.child.stdin.flush()
    with selectors.DefaultSelector() as selector:
     selector.register(self.child.stdout,selectors.EVENT_READ)
     assert selector.select(kwargs.get('timeout',30)),'Wasm response timeout'
    envelope=json.loads(self.child.stdout.readline());assert 'transport_error' not in envelope,envelope
    p=subprocess.CompletedProcess(argv,envelope['returncode'],envelope['stdout'],'')
   else:p=subprocess.run(argv,capture_output=True,text=True,timeout=kwargs.get('timeout',30),cwd=self.freeze['repo'],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
   record.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
   # Never reconstruct a state from diagnostics or discard failures.
   json.loads(p.stdout)
   return p
  except BaseException as error:
   record['transport_error']=repr(error);raise
  finally:write(self.out/'raw-calls.json',self.calls)
 def check_output(self,command,**kwargs):
  p=self.run(command,**kwargs)
  if p.returncode:raise subprocess.CalledProcessError(p.returncode,command,output=p.stdout,stderr=p.stderr)
  return p.stdout

def load_gate(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def interface_cases(t,definitions):
 rows=[]
 for model in MODELS:
  d=next(m for m in definitions['models'] if m['id']==model)
  initial=[x for f in d['state'] for x in (f['initial'] if isinstance(f['initial'],list) else [f['initial']])]
  parameters=[p['default'] for p in d['parameters'].values()]
  base=['--model',model,'--mode','integrate','--parameters',csv(parameters)]
  def call(z,strain):
   args=base+([] if z is None else ['--initial',z])+['--strain',strain]
   p=t.run([t.freeze['artifacts']['native']['path'],*args]);return p,json.loads(p.stdout)
  p,valid=call(csv(initial),csv([0]*6));assert p.returncode==0 and valid['ok'] and len(valid['state'])==len(initial)
  # Invalid parsers can fail before a state exists: no fabricated rollback field.
  invalid=[('missing-state',None,csv([0]*6)),('empty-state','',csv([0]*6)),('short-state',csv(initial[:-1]),csv([0]*6)),('nonfinite-state','nan,'+csv(initial[1:]),csv([0]*6)),('missing-loading',csv(initial),''),('short-loading',csv(initial),'0,0,0,0,0'),('nonfinite-loading',csv(initial),'nan,0,0,0,0,0'),('malformed-loading',csv(initial),'bad,0,0,0,0,0')]
  for ident,z,strain in invalid:
   p,r=call(z,strain);assert p.returncode!=0 and r.get('ok') is False,(model,ident,r)
   # Stateless public calls reject then repeat exact original successful request.
   q,retry=call(csv(initial),csv([0]*6));assert q.returncode==0 and retry==valid,(model,ident,'recovery mismatch')
   rows.append({'model':model,'id':ident,'passed':True,'rollback_state_present':'state' in r,'recovery':'exact complete same-backend zero-load result'})
  if model in ['drucker-prager','modified-cam-clay']:
   # Full solve-vector API still includes gamma; its role is temporary, not caller history.
   assert d['state'][-1]['semantics']['role']=='plastic_multiplier'
   changed=initial.copy();changed[-1]=.125
   p,r=call(csv(changed),csv([0]*6));assert p.returncode==0 and r==valid,(model,'gamma affected zero-load solve')
   rows.append({'model':model,'id':'gamma-is-not-history','passed':True,'comparison':'complete zero-load output identical after changing incoming gamma only'})
 return rows

OriginalTransport=Transport
class Transport(OriginalTransport):
 """Preserve original transport and add actual artifact checks around every call."""
 def run(self,command,**kwargs):
  def bound():
   for item in [*self.freeze['artifacts'].values(),self.freeze['python']]:verify(item)
  bound();primary=None
  try:return super().run(command,**kwargs)
  except BaseException as error:primary=error;raise
  finally:
   try:bound()
   except BaseException as error:
    if self.calls:self.calls[-1]['post_artifact_binding_error']=repr(error)
    write(self.out/'raw-calls.json',self.calls)
    if primary is None:raise
    primary.artifact_post_errors=[*getattr(primary,'artifact_post_errors',[]),repr(error)]


def collect(a):
 f=json.loads(a.freeze.read_text());out=a.output.resolve();assert not out.exists(),'never overwrite an attempt';out.mkdir(parents=True)
 t=None
 receipt={'identity':'baseline-five-qualification-attempt-v1','backend':a.backend,'freeze':pin(a.freeze),'command':sys.argv,'started':True,'passed':False,'failures':[],'gate_reports':{},'current_candidates':f['candidates'],'historical_reports_modified':False}
 def bindings():
  validate_execution_freeze(f)
  for p in [*f['inputs'],*f['artifacts'].values(),f['python']]:verify(p)
  assert str(Path(sys.executable).resolve())==f['python']['path']
  assert platform.python_version()==f['python_version']
  assert [pin(p) for p in source_files(Path(f['repo']))]==f['source_inventory'],'source/reference inventory changed'
 try:
  bindings();repo=Path(f['repo']);sys.path.insert(0,str(repo));sys.path.insert(0,str(repo/'tools'))
  t=Transport(f,a.backend,out);solver=Path(f['artifacts']['native']['path'])
  definitions=json.loads(t.check_output([str(solver),'--describe']))
  write(out/'describe.json',definitions)
  for model in MODELS:
   local=json.loads(Path(f['candidates'][model]['path']).read_text());embedded=next(m for m in definitions['models'] if m['id']==model)
   assert local==embedded and embedded['schema_version']=='0.3',model
  receipt['embedded_catalogue_hash']=definitions['sha256']
  for ident,path,model in GATES:
   t.stage=ident;m=load_gate(repo/path,'baseline_gate_'+ident);m.subprocess=t
   report=m.execute(solver,model) if model else m.execute(solver)
   assert len(report['cases'])==f['policy']['expected_case_counts'][ident] and all(c['passed'] for c in report['cases']) == report['passed'],ident+' complete gate corpus'
   write(out/(ident+'.json'),report);receipt['gate_reports'][ident]={'report':pin(out/(ident+'.json')),'passed':report['passed'],'unchanged_gate_source':pin(repo/path),'actual_backend':a.backend,'actual_artifacts':f['artifacts'],'original_runtime_solver_sha_note':'Unchanged oracle runtime solver_sha256 hashes its supplied native-path transport token; actual Wasm artifact/process bindings are in this outer receipt and raw calls.'}
   if not report['passed']:receipt['failures'].append(ident)
  t.stage='dp83';deck=json.loads((repo/DP/'cases.json').read_text());calls=[]
  for case in deck['cases']:
   p=t.run([str(solver),*case['arguments']]);calls.append({'id':case['id'],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
  assert len(calls)==83
  raw={'solver_sha256':sha(solver) if a.backend=='native' else f['artifacts']['wasm']['sha256'],'catalogue_sha256':definitions['sha256'],'calls':calls};write(out/'dp83-raw.json',raw)
  # Saved assessor unchanged: retains original candidate label/native scope text.
  # Outer receipt, current describe and raw-calls bind actual new model/backend.
  p=subprocess.run([f['python']['path'],str(repo/DP/'run_study.py'),'--replay',str(out/'dp83-raw.json'),'--output',str(out/'dp83-original-assessor')],capture_output=True,text=True,cwd=repo,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  write(out/'dp83-assessor-process.json',{'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
  report=json.loads((out/'dp83-original-assessor/report.json').read_text());receipt['gate_reports']['dp83']={'passed':p.returncode==0 and report['passed'],'historical_gate_candidate_label':report['candidate_sha256'],'current_candidate_sha256':f['candidates']['drucker-prager']['sha256'],'actual_backend':a.backend,'report':pin(out/'dp83-original-assessor/report.json'),'unchanged_gate_source':pin(repo/DP/'run_study.py')}
  if not receipt['gate_reports']['dp83']['passed']:receipt['failures'].append('dp83')
  t.stage='explicit-interface';write(out/'interface-cases.json',interface_cases(t,definitions))
  receipt['raw_call_count']=len(t.calls);receipt['passed']=not receipt['failures']
 except BaseException as error:
  receipt['failures'].append({'exception':repr(error),'traceback':traceback.format_exc()})
 finally:
  if t:
   try:t.close();receipt['owned_transport_closed']=True
   except BaseException as error:receipt['passed']=False;receipt['failures'].append({'transport_cleanup_error':repr(error)})
  try:bindings();receipt['post_bindings_unchanged']=True
  except BaseException as error:receipt['post_bindings_unchanged']=False;receipt['passed']=False;receipt['failures'].append({'post_binding_error':repr(error)})
  receipt['outputs']=[pin(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='receipt.json'];write(out/'receipt.json',receipt)
 if not receipt['passed']:raise SystemExit(1)

class Replay:
 """Replay every original request/result through unchanged oracles, no engine."""
 def __init__(self,rows,freeze):self.rows=iter(rows);self.freeze=freeze;self.used=0
 def run(self,command,**kwargs):
  row=next(self.rows);self.used+=1
  assert str(command[0])==self.freeze['artifacts']['native']['path']
  assert list(map(str,command[1:]))==row['arguments'],'raw request order/content differs'
  assert 'transport_error' not in row and isinstance(row['returncode'],int)
  return subprocess.CompletedProcess(command,row['returncode'],row['stdout'],row['stderr'])
 def check_output(self,command,**kwargs):
  p=self.run(command,**kwargs)
  if p.returncode:raise subprocess.CalledProcessError(p.returncode,command,output=p.stdout,stderr=p.stderr)
  return p.stdout
 def exhausted(self):
  try:next(self.rows)
  except StopIteration:return
  raise AssertionError('unconsumed raw call')

def assess_pair(a):
 assert not a.output.exists(),'never overwrite a pair assessment'
 paths=[a.native.resolve(),a.wasm.resolve()]
 receipts=[json.loads((path/'receipt.json').read_text()) for path in paths]
 assert [r['backend'] for r in receipts]==['native','wasm']
 assert receipts[0]['freeze']==receipts[1]['freeze'],'different prospective contexts'
 frozen=receipts[0]['freeze'];verify(frozen);f=json.loads(Path(frozen['path']).read_text())
 validate_execution_freeze(f)
 assert f['identity']=='baseline-five-current17-reused-execution-freeze-v1'
 assert f['policy']==json.loads((HERE/'policy.json').read_text())
 assert set(f['candidates'])==set(MODELS) and set(f['artifacts'])=={'native','module','wasm','node'}
 for item in [*f['inputs'],*f['artifacts'].values(),f['python'],*f['candidates'].values()]:verify(item)
 repo=Path(f['repo'])
 assert [pin(p) for p in source_files(repo)]==f['source_inventory']
 assert {m:p['sha256'] for m,p in f['candidates'].items()}==f['policy']['candidate_sha256']
 for model,p in f['candidates'].items():assert p==pin(repo/'models'/f'{model}.json')
 required={'describe.json','raw-calls.json','interface-cases.json','elasticity.json','vw96.json','igs97.json','mcc.json','dp83-raw.json','dp83-assessor-process.json','dp83-original-assessor/report.json'}
 for path,r in zip(paths,receipts):
  assert r['identity']=='baseline-five-qualification-attempt-v1'
  assert r['passed'] is True and r['failures']==[] and r['post_bindings_unchanged'] is True and r['owned_transport_closed'] is True
  assert r['current_candidates']==f['candidates']
  actual=[pin(p) for p in sorted(path.rglob('*')) if p.is_file() and p.name!='receipt.json']
  assert r['outputs']==actual and required<={str(Path(p['path']).relative_to(path)) for p in actual}
  assert set(r['gate_reports'])=={'elasticity','vw96','igs97','mcc','dp83'}
  rows=json.loads((path/'raw-calls.json').read_text())
  assert len(rows)==r['raw_call_count'] and rows and [x['sequence'] for x in rows]==list(range(len(rows)))
  expected_transport='native-cli-process' if r['backend']=='native' else 'persistent-wasm-public-api'
  for row in rows:
   assert row['transport']==expected_transport and 'transport_error' not in row
   command=[f['artifacts']['native']['path'],*row['arguments']] if r['backend']=='native' else [f['artifacts']['node']['path'],str(HERE/'wasm-cli.mjs'),f['artifacts']['module']['path'],f['artifacts']['wasm']['path'],'--serve']
   assert row['command']==command
   json.loads(row['stdout'])
  assert set(x['stage'] for x in rows)=={'describe',*[x[0] for x in GATES],'dp83','explicit-interface'}
  stages=[row['stage'] for i,row in enumerate(rows) if i==0 or row['stage']!=rows[i-1]['stage']]
  assert stages==['describe',*[x[0] for x in GATES],'dp83','explicit-interface'],'global raw stage order/contiguity differs'
  replay=Replay([x for x in rows if x['stage']=='describe'],f)
  definitions=json.loads(replay.check_output([f['artifacts']['native']['path'],'--describe']));replay.exhausted()
  assert definitions==json.loads((path/'describe.json').read_text()) and definitions['sha256']==r['embedded_catalogue_hash']
  for model in MODELS:assert next(m for m in definitions['models'] if m['id']==model)==json.loads(Path(f['candidates'][model]['path']).read_text())
  sys.path.insert(0,str(repo));sys.path.insert(0,str(repo/'tools'))
  solver=Path(f['artifacts']['native']['path'])
  for ident,source,model in GATES:
   replay=Replay([x for x in rows if x['stage']==ident],f)
   module=load_gate(repo/source,'replay_'+r['backend']+'_'+ident);module.subprocess=replay
   result=module.execute(solver,model) if model else module.execute(solver);replay.exhausted()
   assert result==json.loads((path/(ident+'.json')).read_text())
   assert result['passed'] is True and len(result['cases'])==f['policy']['expected_case_counts'][ident] and all(x['passed'] for x in result['cases'])
   gate=r['gate_reports'][ident]
   assert gate['passed'] is True and gate['actual_backend']==r['backend'] and gate['report']==pin(path/(ident+'.json')) and gate['unchanged_gate_source']==pin(repo/source)
  deck=json.loads((repo/DP/'cases.json').read_text());raw=json.loads((path/'dp83-raw.json').read_text());dp_rows=[x for x in rows if x['stage']=='dp83']
  assert len(deck['cases'])==len(raw['calls'])==len(dp_rows)==83
  for case,call,row in zip(deck['cases'],raw['calls'],dp_rows):
   assert case['arguments']==row['arguments'] and call=={key:case['id'] if key=='id' else row[key] for key in ['id','returncode','stdout','stderr']}
  assert raw['catalogue_sha256']==definitions['sha256'] and raw['solver_sha256']==f['artifacts']['native' if r['backend']=='native' else 'wasm']['sha256']
  process=json.loads((path/'dp83-assessor-process.json').read_text());assert process['returncode']==0
  with tempfile.TemporaryDirectory(prefix='baseline-pair-replay-') as temp:
   proc=subprocess.run([f['python']['path'],str(repo/DP/'run_study.py'),'--replay',str(path/'dp83-raw.json'),'--output',temp],capture_output=True,text=True,cwd=repo,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
   result=json.loads((Path(temp)/'report.json').read_text())
   assert proc.returncode==0 and result==json.loads((path/'dp83-original-assessor/report.json').read_text()) and result['passed'] is True and result['count']==83
  gate=r['gate_reports']['dp83'];assert gate['passed'] is True and gate['actual_backend']==r['backend'] and gate['report']==pin(path/'dp83-original-assessor/report.json') and gate['unchanged_gate_source']==pin(repo/DP/'run_study.py') and gate['current_candidate_sha256']==f['candidates']['drucker-prager']['sha256']
  replay=Replay([x for x in rows if x['stage']=='explicit-interface'],f)
  interface=interface_cases(replay,definitions);replay.exhausted()
  assert interface==json.loads((path/'interface-cases.json').read_text()) and len(interface)==42 and replay.used==87
 write(a.output,{'identity':'baseline-five-native-wasm-independent-gates-pair-v2','passed':True,'receipts':[pin(path/'receipt.json') for path in paths],'freeze':frozen,'models':MODELS,'scope':'Both backends independently passed unchanged reference gates and new explicit interface corpus. Every saved request/result replayed through unchanged reference assessors and interface assertions; no new parity tolerance or scientific approval.','limitations':['Native failures/retries are separate CLI processes; Wasm same-instance recovery only','No strict15package/browser/live/FE or broader source admission']})

def main():
 if sys.flags.optimize:raise RuntimeError('qualification requires assertions enabled')
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
 freeze_parser=sub.add_parser('reuse-freeze')
 for name in ['repo','handoff','review','output']:freeze_parser.add_argument('--'+name,type=Path,required=True)
 for name in ['handoff-sha256','review-sha256']:freeze_parser.add_argument('--'+name,required=True)
 c=sub.add_parser('collect');c.add_argument('--freeze',type=Path,required=True);c.add_argument('--backend',choices=['native','wasm'],required=True);c.add_argument('--output',type=Path,required=True)
 pair=sub.add_parser('assess-pair')
 for name in ['native','wasm','output']:pair.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();{'reuse-freeze':reuse_freeze,'collect':collect,'assess-pair':assess_pair}[a.action](a)
if __name__=='__main__':main()
