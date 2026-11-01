"""Prospective mixed normal-catalogue API qualification. No kernel instrumentation."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,struct,subprocess,sys,time
P=Path(__file__).resolve().parent;ROOT=P.parents[2];STAGE=Path('/private/tmp/atlas-tresca-mixed-catalogue-v1')
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt

def read(p):return json.loads(Path(p).read_text())
def save(n,o):(P/n).write_text(json.dumps(o,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def process(name,cmd):
 t=time.monotonic();r=subprocess.run(cmd,cwd=STAGE,capture_output=True,text=True,timeout=60)
 save(name+'-process.json',{'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.monotonic()-t});print(name,r.returncode,flush=True)
 if r.returncode:raise RuntimeError(name+' failed; retained process receipt')
 return r.stdout

def same_numeric_dispatch():
 from atlas.compiler import generate
 import tempfile,re
 def block(header,start):
  i=header.index(start);j=header.index('{',i);depth=1;k=j+1
  while depth:
   depth+=(header[k]=='{')-(header[k]=='}');k+=1
  return header[i:k]
 with tempfile.TemporaryDirectory()as td:
  generate(td,[P/'model.json']);single=(Path(td)/'models.hpp').read_text();mixed=(P/'generated-ten/models.hpp').read_text();models=read(P/'generated-ten/models.json')['models'];index=next(i for i,m in enumerate(models)if m['id']==read(P/'model.json')['id']);checks={}
  a=block(single,'inline bool solution_constraints_0');b=block(mixed,'inline bool solution_constraints_'+str(index)).replace('solution_constraints_'+str(index),'solution_constraints_0');checks['solution_constraints']=a==b
  for name in ['evaluate_model','prepare_model_increment','model_scales','model_observable_scales']:
   a=block(single,single[single.index(name)-30:].split('\n')[0])if False else single[single.index(name):]
   b=mixed[mixed.index(name):]
   checks[name]=block(a,'case 0: {')==block(b,'case '+str(index)+': {').replace('case '+str(index)+': {','case 0: {',1)
  assert all(checks.values()),checks
  return {'index':index,'checks':checks,'unmodified_normal_generation':True}

class Client:
 def __init__(self,backend):
  self.backend=backend
  self.child=subprocess.Popen(['node',str(P/'rpc.mjs'),str(STAGE/'wasm/atlas.js')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)if backend=='wasm'else None
 def call(self,r):
  before=json.dumps(r,sort_keys=True)
  if self.child:
   self.child.stdin.write(json.dumps(r)+'\n');self.child.stdin.flush();line=self.child.stdout.readline()
   if not line:raise RuntimeError('Wasm RPC exited: '+self.child.stderr.read())
   out=json.loads(line);assert 'transport_error'not in out,out;assert out['inputs_unchanged'];response=out['response']
  else:
   if 'cli'in r:cli=r['cli']
   else:
    args=r['args'];id,params,state=args[:3];cli=['--model',id,'--parameters',params,'--initial',state]
    if 'controls'in r['function']:
     file=STAGE/'wire-controls.txt';file.write_text(args[4]);cli+=['--mode','run-controls','--protocol',str(args[3]),'--laboratory-controls-file',str(file),'--integration-settings',args[5]]
     if 'scope'in r['function']:cli+=['--response-contract','stress-scope-0.1']
    else:
     cli+=['--mode','integrate','--strain',args[3],'--integration-settings',args[4]]
   run=subprocess.run([str(STAGE/'native/atlas_solver'),*cli],capture_output=True,text=True,timeout=30);response=json.loads(run.stdout)
  assert before==json.dumps(r,sort_keys=True)
  return response
 def close(self):
  if self.child:
   self.child.stdin.close();self.child.wait(timeout=10)
   assert self.child.returncode==0,self.child.stderr.read()

def collect(backend):
 client=Client(backend);old=[]
 try:
  bylabel={}
  for r in read(P/'old-nine-requests.json'):
   r=json.loads(json.dumps(r))
   if 'parent_from'in r:
    state=','.join(map(str,bylabel[r['parent_from']]['state']));r['args'][2]=state;r['cli'][r['cli'].index('--initial')+1]=state
   response=client.call(r);bylabel[r['label']]=response;old.append({'label':r['label'],'response':response})
  save(backend+'-old-nine-responses.json',old)
  lab=[];id=read(P/'model.json')['id'];recovery={'function':'atlas_run_controls_scope_with_settings','types':['string','string','string','number','string','string'],'args':[id,'1024,3072,2048,8','64,64,64,0,0,0,0,0,0,0,0,0',4,'0000000000000000,0000000000000000','2e-10,1e-6,45,0,20000,11']}
  for r in read(P/'laboratory-requests.json'):lab.append({'label':r['label'],'inputs_unchanged':True,'response':client.call(r),'recovery':client.call(recovery)})
  save(backend+'-laboratory-responses.json',lab)
  inp=read(P/'history-inputs.json');initial=[float.fromhex(v)for v in inp['initial']];committed=initial;rows=[];accepted=0;stopped=False;exact=mod('mixed_exact',ROOT/'docs/reviews/certified-spectral-range-v1/exact.py');settings='2e-10,1e-6,45,0,20000,11';params=','.join(map(str,inp['parameters'].values()))
  def bits(v):return[str(int.from_bytes(struct.pack('>d',float(x)),'big'))for x in v]
  def callstep(parent,d):return client.call({'function':'atlas_integrate_with_settings','types':['string']*5,'args':[id,params,','.join(map(str,parent)),','.join(map(str,d)),settings]})
  baseline=callstep(initial,[0]*6);assert baseline['ok']
  for i,d in enumerate(inp['loading']):
   parent=committed.copy()
   if stopped:rows.append({'step':i,'attempted':False,'parent_bits':bits(parent)});continue
   result=callstep(parent,[float.fromhex(x)for x in d]);out=result['state'];recovered=callstep(initial,[0]*6);unchanged=parent==committed;rollback=bits(out)==bits(parent)
   if result['ok']:committed=out;accepted+=1
   else:stopped=True
   rows.append({'step':i,'attempted':True,'ok':result['ok'],'parent_in':exact.range_le(parent[:6],6.),'output_in':exact.range_le(out[:6],6.),'input_unchanged':unchanged,'returned_parent':rollback,'baseline_recovery':recovered['ok']and recovered['state']==baseline['state'],'iterations':result['diagnostics']['iterations'],'substeps':result['diagnostics']['substeps'],'parent_bits':bits(parent),'output_bits':bits(out),'committed_bits':bits(committed)})
  rows.append({'summary':True,'scheduled':len(inp['loading']),'accepted':accepted,'stopped':stopped,'final_bits':bits(committed)});save(backend+'-history-responses.json',rows)
 finally:client.close()

if __name__=='__main__':
 phase=sys.argv[1]
 if phase=='freeze':
  assert not(P/'prospective-freeze.json').exists()
  save('generated-equivalence.json',same_numeric_dispatch())
  files={q.relative_to(ROOT).as_posix():sha(q)for q in P.rglob('*')if q.is_file()and '__pycache__'not in q.parts}
  save('prospective-freeze.json',{'version':'tresca-mixed-catalogue-freeze-0.1','files':files,'no_candidate_build_or_execution_before_freeze':True,'history_transport':'explicit complete API JSON/CSV restart from each returned state; previous in-process history qualification remains distinct'})
 else:
  assert phase in ['native','wasm']
  for path,h in read(P/'prospective-freeze.json')['files'].items():assert sha(ROOT/path)==h,path
  for path,h in read(P/'source-pins.json').items():assert sha(STAGE/path)==h,path
  assert sha(STAGE/'models/tresca-associated-perfect-bk2022v1-be.json')==sha(P/'model.json')
  process(phase+'-configure',(['emcmake']if phase=='wasm'else [])+['cmake','-S',str(STAGE),'-B',str(STAGE/phase),'-DCMAKE_BUILD_TYPE=Release'])
  process(phase+'-build',['cmake','--build',str(STAGE/phase),'--target','atlas_solver','--parallel','1'])
  for n in ['models.hpp','models.json']:assert(STAGE/phase/'generated'/n).read_bytes()==(P/'generated-ten'/n).read_bytes(),n
  collect(phase)
  artifacts=[STAGE/'native/atlas_solver']if phase=='native'else[STAGE/'wasm/atlas.js',STAGE/'wasm/atlas.wasm']
  save(phase+'-artifacts.json',{str(p):sha(p)for p in artifacts});print(phase+' responses retained',flush=True)
