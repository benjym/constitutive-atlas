from pathlib import Path
import json,subprocess,hashlib,sys,shutil
R=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(R))
from atlas.model import all_models
from atlas.compiler import generate
P=R/'catalogue/investigations/tresca-mixed-catalogue-v1';S=Path('/private/tmp/atlas-tresca-mixed-catalogue-v1');S.mkdir()
def js(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Build only tracked compiler/engine/schema/fixture sources. Unrelated chats stay outside.
names=subprocess.check_output(['git','ls-files','--','CMakeLists.txt','atlas','cpp','schemas','tests','models'],cwd=R,text=True).splitlines()
pins={n:sha(R/n)for n in names if (R/n).is_file()}
js(P/'source-pins.json',pins)
for n in pins:
 q=S/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,q)
proposal=R/'docs/reviews/tresca-v5-source-integration-v1/public-model.json'
shutil.copyfile(proposal,P/'model.json');shutil.copyfile(proposal,S/'models/tresca-associated-perfect-bk2022v1-be.json')
generate(P/'generated-nine')
generate(P/'generated-ten',list((S/'models').glob('*.json')))
models=all_models();baseline=Path('/private/tmp/atlas-current-source-build-v1/build/atlas_solver')
assert json.loads(subprocess.check_output([str(baseline),'--describe']))['models']==models
js(P/'baseline-artifact.json',{'path':str(baseline),'sha256':sha(baseline),'models_exact':True,'source_receipt':'docs/benchmarks/current-source-build-v1/README.md','qualification':'retained old-nine API regression reference, not scientific truth'})
calls=[];results=[]
def add(label,m,fun,types,args,cli,parent_from=None):
 req={'label':label,'model':m,'function':fun,'types':types,'args':args,'cli':cli}
 if parent_from is not None:req['parent_from']=parent_from
 proc=subprocess.run([str(baseline),*cli],capture_output=True,text=True,timeout=30)
 out=json.loads(proc.stdout);calls.append(req);results.append({'label':label,'returncode':proc.returncode,'response':out});return out
for m in models:
 id=m['id'];z=[x for f in m['state'] for x in (f['initial'] if f.get('shape')=='sym' else [f['initial']])];initial=','.join(map(str,z))
 for protocol in range(5):
  target=1000 if protocol==3 else .0002
  add(id+'/protocol-'+str(protocol),id,'atlas_run',['string']*3+['number']*4,[id,'',initial,protocol,target,8,0],['--model',id,'--initial',initial,'--protocol',str(protocol),'--target',str(target),'--steps','8','--cycles','0'])
 add(id+'/evaluate',id,'atlas_evaluate',['string']*5,[id,'',initial,initial,'0,0,0,1e-6,0,0'],['--model',id,'--mode','evaluate','--initial',initial,'--current',initial,'--strain','0,0,0,1e-6,0,0'])
 parent=initial;prev=None
 for step,d in enumerate(['0,0,0,1e-5,0,0','0,0,0,-2e-5,0,0','0,0,0,1e-5,0,0','0,0,0,0,0,0']):
  label=id+'/history-'+str(step)
  out=add(label,id,'atlas_integrate',['string']*4,[id,'',parent,d],['--model',id,'--mode','integrate','--initial',parent,'--strain',d],prev)
  assert out['ok'],(label,out)
  prev=label;parent=','.join(map(str,out['state']))
 for label,pars,state,d,settings in [('bad-state','',initial+',0','0,0,0,0,0,0',None),('bad-parameter','nan',initial,'0,0,0,0,0,0',None),('forced-failure','',initial,'.1,-.05,-.05,.01,0,0','1e-30,1e-30,1,0,1,0'),('recovery','',initial,'0,0,0,0,0,0',None)]:
  fun='atlas_integrate_with_settings'if settings else 'atlas_integrate';args=[id,pars,state,d]+([settings]if settings else []);cli=['--model',id,'--mode','integrate','--parameters',pars,'--initial',state,'--strain',d]+(['--integration-settings',settings]if settings else [])
  out=add(id+'/'+label,id,fun,['string']*len(args),args,cli)
  if label.startswith('bad-'):assert not out['ok']
  if label=='recovery':assert out['ok']
js(P/'old-nine-requests.json',calls);js(P/'old-nine-baseline-responses.json',results)
js(P/'policy.json',{'version':'mixed-catalogue-compatibility-0.1','old_nine':{'request_count':len(calls),'fields':'recursive comparison of every response field except elapsed_ms and expected catalogue_hash; dictionary keys, booleans, text, integer diagnostics and array lengths exact','native_absolute':1e-10,'native_relative':1e-10,'wasm_absolute':1e-7,'wasm_relative':1e-7,'own_parent_history':True,'baseline':'retained exact-nine-definition native executable; regression evidence, not independent constitutive validation'},'tresca':'unchanged v5 laboratory references and policy (29 cases); unchanged own-state 12-step independent history assessor; metadata-only source equivalence plus exact normal-generated per-model dispatch equivalence; no replacement of original full38-column qualification','build':'current frozen common source; one explicit atlas_solver target, --parallel 1, native then Wasm','stop':'on a failed gate retain results, no installation or gate relaxation'})
# Copy unchanged original laboratory inputs/reference/assessor and history machinery.
V=R/'catalogue/investigations/tresca-certified-corners-v5'
for name in ['laboratory-inputs.json','laboratory-references.json','laboratory-policy.json','assess_laboratory.py','history-inputs.json','assess_history.py']:
 shutil.copyfile(V/name,P/name)
print('Captured',len(calls),'old-nine requests; staged',len(pins),'source files; candidate not built')
