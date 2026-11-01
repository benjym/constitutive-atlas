"""Serial, role-bound execution of the frozen current MC numerical study."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess,sys
P=Path(__file__).resolve().parent;R=P.parents[2];C=P.parent/'mc-current-collector-freeze-v3';STAGE=Path('/private/tmp/atlas-mc-execution-v3')
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
sys.path.insert(0,str(C))
from strict_observation_json import loads
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:loads(Path(p).read_bytes())

def plan(role):
 if role not in('native','wasm'):raise ValueError('native or wasm role required')
 stage=STAGE/role;build=stage/'build';out=stage/'observations'
 config=['cmake','-S',str(stage),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release']
 if role=='wasm':config.insert(0,'emcmake')
 commands=[
 ('generate',[sys.executable,'-B','-m','atlas.compiler',str(stage/'generated'),str(C/'models')]),
 ('configure',config),
 ('build',['cmake','--build',str(build),'--target','atlas_solver','--parallel','1']),
 ('observe',['node',str(C/'observe.mjs'),role,str(build),str(out)]),
 ('paths',[sys.executable,'-B',str(C/'assess_paths.py'),str(out/'journal.json')]),
 ('replays',[sys.executable,'-B',str(C/'assess_replays.py'),str(out),role]),
 ('compatibility-collect',['node',str(P/'compatibility.mjs'),role,str(build),str(R/'catalogue/investigations/declared-loading-mixed-v1/requests.json'),str(out/'compatibility.json')]),
 ('compatibility-assess',[sys.executable,'-B',str(P/'assess_compatibility.py'),str(out/'compatibility.json'),role])]
 if role=='wasm':commands.insert(6,('parity',[sys.executable,'-B',str(C/'assess_parity.py'),str(STAGE/'native/observations/journal.json'),str(out/'journal.json')]))
 return commands

def verify_inputs():
 for n,h in read(P/'manifest.json')['files'].items():assert sha(P/n)==h,n
 freeze=read(P/'freeze.json');assert freeze['compiled_calls_at_freeze']==0 and freeze['manifest_sha256']==sha(P/'manifest.json')
 assert freeze['collector_manifest_sha256']==sha(C/'manifest.json')
 review=read(P/'technical-review.json');assert review['blockers']==[] and review['scientific_approval']is False
 assert set(review['reviewed_files'])=={'execute.py','CMakeLists.txt','compatibility.mjs','assess_compatibility.py','check_driver.py'}
 assert freeze['technical_review_sha256']==sha(P/'technical-review.json')
 for n,h in review['reviewed_files'].items():assert sha(P/n)==h,n
 for n,h in read(C/'manifest.json')['files'].items():assert sha(C/n)==h,n
 for n,h in read(C/'source-pins.json')['sources'].items():assert sha(R/n)==h,n
 for n,h in read(C/'compatibility-policy.json')['baseline'].items():assert sha(R/n)==h,n
 return freeze

def verify_native():
 d=STAGE/'native';receipt=read(d/'receipt.json')
 assert receipt['role']=='native'and receipt['completed']is True
 assert receipt['freeze_sha256']==sha(P/'freeze.json')
 assert [(c['label'],c['argv'])for c in receipt['commands']]==plan('native')
 assert all(type(c['status'])is int and c['status']==0 and c['signal']is None for c in receipt['commands'])
 assert set(receipt['observations'])=={'journal.json','calls.json','replays.json','rejections.json','compatibility.json'}
 assert set(receipt['artifacts'])=={'atlas_solver'}
 for n,h in receipt['artifacts'].items():assert sha(d/'build'/n)==h,n
 for n,h in receipt['observations'].items():assert sha(d/'observations'/n)==h,n
 for n in ['paths','replays','compatibility-assess']:assert read(d/(n+'.stdout'))['passed']is True
 return receipt

def verify_stage(stage):
 for n,h in read(C/'source-pins.json')['sources'].items():
  if n.startswith('cpp/'):assert sha(stage/'frozen'/n)==h,n
 assert (stage/'CMakeLists.txt').read_bytes()==(P/'CMakeLists.txt').read_bytes()
 if (stage/'generated').exists():
  assert (stage/'generated/models.json').read_bytes()==(C/'catalogue.json').read_bytes()
  assert sha(stage/'generated/models.hpp')==read(C/'generation.json')['generated_header_sha256']

def execute(role):
 commands=plan(role);verify_inputs()
 if role=='wasm':verify_native()
 stage=STAGE/role;assert not stage.exists(),'Refuse to overwrite prior outcome'
 stage.mkdir(parents=True);out=stage/'observations';out.mkdir()
 receipt={'role':role,'completed':False,'freeze_sha256':sha(P/'freeze.json'),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[],'artifacts':{},'observations':{}}
 def save():(stage/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 save()
 try:
  # Every copied byte is checked against the live source freeze before use.
  for n,h in read(C/'source-pins.json')['sources'].items():
   if n.startswith('cpp/'):
    source=R/n;assert sha(source)==h
    target=stage/'frozen'/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  shutil.copyfile(P/'CMakeLists.txt',stage/'CMakeLists.txt')
  env=dict(os.environ,EMCC_CORES='1',PYTHONDONTWRITEBYTECODE='1')
  for label,args in commands:
   verify_inputs();verify_stage(stage)
   try:result=subprocess.run(args,cwd=R,env=env,capture_output=True,timeout=180)
   except subprocess.TimeoutExpired as exc:
    (stage/(label+'.stdout')).write_bytes(exc.stdout or b'');(stage/(label+'.stderr')).write_bytes(exc.stderr or b'')
    receipt['commands'].append({'label':label,'argv':args,'status':None,'signal':None,'timeout':True});save();raise
   (stage/(label+'.stdout')).write_bytes(result.stdout);(stage/(label+'.stderr')).write_bytes(result.stderr)
   receipt['commands'].append({'label':label,'argv':args,'status':result.returncode,'signal':-result.returncode if result.returncode<0 else None});save()
   print(role,label,result.returncode,flush=True)
   if result.returncode:raise RuntimeError(label+' failed; preserve original outputs and stop')
   if label=='generate':
    assert (stage/'generated/models.json').read_bytes()==(C/'catalogue.json').read_bytes()
    assert sha(stage/'generated/models.hpp')==read(C/'generation.json')['generated_header_sha256']
   if label=='build':
    names=['atlas_solver']if role=='native'else['atlas.js','atlas.wasm']
    receipt['artifacts']={n:sha(stage/'build'/n)for n in names};save()
    if role=='wasm':(stage/'build/package.json').write_text('{"type":"module"}\n')
   if label in('paths','replays','parity','compatibility-assess'):assert loads(result.stdout)['passed']is True
  receipt['observations']={f.name:sha(f)for f in sorted(out.glob('*.json'))}
  assert set(receipt['observations'])=={'journal.json','calls.json','replays.json','rejections.json','compatibility.json'}
  verify_inputs();verify_stage(stage)
  for n,h in receipt['artifacts'].items():assert sha(stage/'build'/n)==h,n
  receipt['completed']=True
 except BaseException as exc:
  receipt['error']=repr(exc);save();raise
 finally:
  receipt['observations']={f.name:sha(f)for f in sorted(out.glob('*.json'))}
  receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 return receipt

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('role',choices=['native','wasm']);parser.add_argument('--plan',action='store_true');args=parser.parse_args()
 if args.plan:print(json.dumps(plan(args.role),indent=2))
 else:execute(args.role)
