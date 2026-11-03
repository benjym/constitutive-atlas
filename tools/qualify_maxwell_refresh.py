"""Fresh Maxwell build qualification; source preparation and saved checks are separate.

Only explicit native/wasm commands execute material. Builds are NOT run by this
collector: the coordinator performs the frozen serial commands before collection.
Finalization requires an actual separate-agent accepted build-review record.
"""
import argparse,copy,hashlib,importlib.util,json,math,os,shutil,subprocess,sys,time,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKET=Path('docs/ingestion/vibe-2026/maxwell-refresh-v1')
BASE=Path('docs/ingestion/maxwell-itasca900/integration-v1')
MODEL='maxwell-itasca900-zero-spin-ode'
DEFINITION=Path('models/research/maxwell')/(MODEL+'.json')
GATES=('native_references','wasm_references','transactions','parity','presets')
PRESETS={'relaxation':'relaxation-schedule','creep':'creep-schedule','oedometer':'oedometer','load-hold-reverse':'load-hold-reverse'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_new(p,value):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def pin(p):
 p=Path(p);return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def helpers():
 sys.path.insert(0,str(ROOT))
 from tools.build_maxwell_laboratory import source_manifest
 m=module('maxwell_refresh_original_assessor',ROOT/'tests/test_maxwell.py')
 tx=module('maxwell_refresh_original_transactions',ROOT/BASE/'check_transactions.py')
 return source_manifest,m,tx

def freeze():
 """Coordinator must call only after merge; no material/build/module execution."""
 source_manifest,m,tx=helpers();paths=[ROOT/DEFINITION,ROOT/BASE/'reference-cases.json',ROOT/BASE/'check_transactions.py',ROOT/BASE/'compare_backends_v2.py',ROOT/'tests/test_maxwell.py',ROOT/'tools/test_maxwell_wasm.mjs',ROOT/'tools/test_maxwell_public_presets.mjs',ROOT/'tools/qualify_maxwell_refresh.py',ROOT/'tools/build_maxwell_laboratory.py']
 paths += [ROOT/'examples/maxwell'/(n+'.json') for n in PRESETS]
 paths += [ROOT/'web'/n for n in ('maxwell-atlas-contract.mjs','maxwell-atlas-engine.mjs','maxwell-atlas-runner.mjs','maxwell-atlas-worker.mjs','maxwell-laboratory.mjs')]
 cases=read(ROOT/BASE/'reference-cases.json');assert len(cases['cases'])==24
 assert set(PRESETS.values())<={c['id'] for c in cases['cases']}
 for n,cid in PRESETS.items():assert read(ROOT/'examples/maxwell'/(n+'.json'))==next(c for c in cases['cases'] if c['id']==cid)['specification']
 builds={k:'.local/maxwell-refresh-v1/'+k for k in ('native','wasm')}
 commands={}
 for backend,build in builds.items():
  configure=['cmake','-S','cmake/maxwell','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
  commands[backend]=[(['emcmake'] if backend=='wasm' else [])+configure,['cmake','--build',build,'--target','atlas_maxwell_solver','--parallel','1']]
 plan={'identity':'maxwell-current-source-refresh-v1','status':'prospective-no-material-observed','source_manifest':source_manifest(),'files':[pin(p) for p in paths],'builds':builds,'serial_build_commands':commands,'case_count':24,'calls_per_backend':76,'transaction_cases':14,'gates':list(GATES),'original_policy':cases['policy'],'implementation_run':'/root/maxwell-refresh-v1','limits':['Same original analytical cases/settings/bounds; no tolerance relaxation','No new broad scientific approval, browser/live or arbitrary material-parameter validation','Original late committed regular schedule failure remains unproved; no new stronger rollback claim','Actual build commands/terminal receipts must be supplied by coordinator; no fabricated build success']}
 write_new(ROOT/PACKET/'plan.json',plan);print(json.dumps({'status':'frozen-source-only','plan_sha256':sha(ROOT/PACKET/'plan.json')},indent=2))

def guard(plan_path):
 plan=read(plan_path);source_manifest,m,tx=helpers()
 if source_manifest()!=plan['source_manifest']:raise ValueError('Changed Maxwell current source manifest')
 for x in plan['files']:
  if sha(ROOT/x['path'])!=x['sha256']:raise ValueError('Changed Maxwell input '+x['path'])
 return plan,m,tx

class Journal:
 def __init__(self,out):self.out=Path(out);self.path=self.out/'events.jsonl'
 def emit(self,value):
  with self.path.open('a') as f:f.write(json.dumps(value,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
 def command(self,argv,label,timeout=180):
  self.emit({'kind':'before-command','label':label,'argv':list(map(str,argv)),'timeout_seconds':timeout});start=time.monotonic()
  try:
   r=subprocess.run(list(map(str,argv)),cwd=ROOT,capture_output=True,text=True,timeout=timeout)
   result={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.monotonic()-start}
  except subprocess.TimeoutExpired as e:
   result={'returncode':None,'timeout':True,'stdout':e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout,'stderr':e.stderr.decode(errors='replace') if isinstance(e.stderr,bytes) else e.stderr,'elapsed_seconds':time.monotonic()-start};self.emit({'kind':'after-command','label':label,**result});raise
  self.emit({'kind':'after-command','label':label,**result});return result

def artifacts(build,backend):
 names=['generated/models.json','generated/models.hpp','CMakeCache.txt','compile_commands.json']
 names+=['atlas_maxwell_solver'] if backend=='native' else ['maxwell.js','maxwell.wasm']
 return {n:sha(build/n) for n in names}
def rows_native(solver,cases,out,journal,label):
 rows=[]
 # Save every completed call immediately, including expected refusals.
 with (out/(label+'.json')).open('x') as f:f.write('[]\n')
 for case in cases:
  calls=[];row={'id':case['id'],'calls':calls};rows.append(row)
  for repeat in range(2):
   r=journal.command([solver,*case['argv']],case['id']+'-'+str(repeat));calls.append({k:r[k] for k in ['returncode','stdout','stderr']})
   p=out/(label+'.json');p.write_text(json.dumps(rows,indent=2)+'\n')
 return rows

def reference_identity(build):
 catalogue=read(build/'generated/models.json')
 return {'model':MODEL,'model_sha256':sha(ROOT/DEFINITION),'catalogue_hash':catalogue['sha256']}

def check_build_receipts(plan,backend,configure_receipt,build_receipt):
 receipts=[]
 for supplied,expected in zip([configure_receipt,build_receipt],plan['serial_build_commands'][backend]):
  path=Path(supplied).resolve();r=read(path)
  if r.get('returncode')!=0 or r.get('command')!=expected:raise ValueError('Missing exact successful serial build terminal: '+str(path))
  log=path.with_suffix('.log')
  if not log.is_file() or sha(log)!=r.get('log_sha256'):raise ValueError('Changed or missing genuine build log: '+str(log))
  receipts.append({'path':str(path),'sha256':sha(path),'log_sha256':sha(log),'command':expected})
 return receipts

def check_generated(build):
 sys.path.insert(0,str(ROOT));from atlas.compiler import generate
 with tempfile.TemporaryDirectory(prefix='maxwell-refresh-source-only-') as td:
  generate(td,[ROOT/DEFINITION])
  for name in ['models.hpp','models.json']:
   if (Path(td)/name).read_bytes()!=(build/'generated'/name).read_bytes():raise ValueError('Stale Maxwell generated source/catalogue: '+name)

def collect(backend,plan_path,build,out,native_peer=None,configure_receipt=None,build_receipt=None):
 plan,m,tx=guard(plan_path);build=Path(build).resolve();out=Path(out).resolve()
 if out.exists() or out.is_symlink():raise ValueError('New exclusive output directory required')
 out.mkdir(parents=True);journal=Journal(out);before=artifacts(build,backend)
 check_generated(build);receipts=check_build_receipts(plan,backend,configure_receipt,build_receipt)
 bindings={'backend':backend,'plan_sha256':sha(plan_path),'source_manifest_sha256':plan['source_manifest']['sha256'],'artifacts':before,'build_receipts':receipts}
 if backend=='wasm':
  if native_peer is None:raise ValueError('Successful exact native peer required')
  ns=read(Path(native_peer)/'summary.json')
  if ns['status']!='passed' or ns['bindings']['plan_sha256']!=sha(plan_path):raise ValueError('Wrong native peer')
  check_saved(Path(native_peer),ns)
  bindings['native_peer_summary_sha256']=sha(Path(native_peer)/'summary.json')
 write_new(out/'bindings.json',bindings);journal.emit({'kind':'bindings-before-material','bindings':bindings})
 try:
  cases=read(ROOT/BASE/'reference-cases.json')['cases']
  if backend=='native':rows=rows_native(build/'atlas_maxwell_solver',cases,out,journal,'reference-raw')
  else:
   r=journal.command(['node',ROOT/'tools/test_maxwell_wasm.mjs',build/'maxwell.js',ROOT/BASE/'reference-cases.json',out/'reference-raw.json'],'reference-corpus');assert r['returncode']==0
   rows=read(out/'reference-raw.json')
  errors=m.assess_rows(cases,rows);write_new(out/'reference-assessment.json',{'passed':True,'errors_Pa':errors})
  tc=tx.cases_for(out/'reference-raw.json');assert len(tc)==14;write_new(out/'transaction-cases.json',{'cases':tc})
  if backend=='native':tr=rows_native(build/'atlas_maxwell_solver',tc,out,journal,'transaction-raw')
  else:
   r=journal.command(['node',ROOT/'tools/test_maxwell_wasm.mjs',build/'maxwell.js',out/'transaction-cases.json',out/'transaction-raw.json'],'transaction-corpus');assert r['returncode']==0
   tr=read(out/'transaction-raw.json')
  te=tx.assess(tc,tr);write_new(out/'transaction-assessment.json',{'passed':True,'errors_Pa':te,'recovery_pairs':6,'actual_endpoint_restarts':2})
  if backend=='native':
   # Retain original native CLI replay and untimed refusal, plus all four public presets.
   for n,cid in PRESETS.items():
    target=out/('preset-'+n+'.json');r=journal.command([sys.executable,'-B','-m','atlas.cli','run',ROOT/'examples/maxwell'/(n+'.json'),'--solver',build/'atlas_maxwell_solver','--output',target],'native-preset-'+n);assert r['returncode']==0
    m.assess(next(c for c in cases if c['id']==cid),read(target))
   target=out/'creep-replay.json';r=journal.command([sys.executable,'-B','-m','atlas.cli','run',out/'preset-creep.json','--solver',build/'atlas_maxwell_solver','--output',target],'native-creep-cli-replay');assert r['returncode']==0 and read(target)==read(out/'preset-creep.json')
   r=journal.command([build/'atlas_maxwell_solver','--model',MODEL,'--mode','integrate','--initial',m.CSV(m.Z),'--parameters',m.CSV(m.P),'--strain','0,0,0,0,0,0'],'untimed-refusal');assert r['returncode']==1 and json.loads(r['stdout'])['ok'] is False
  else:
   write_new(out/'identity.json',reference_identity(build));r=journal.command(['node',ROOT/'tools/test_maxwell_public_presets.mjs',build,out/'presets.json',out/'identity.json'],'wasm-public-presets');assert r['returncode']==0
   presets=read(out/'presets.json');assert [p['name'] for p in presets]==list(PRESETS)
   for row in presets:
    c=next(c for c in cases if c['id']==PRESETS[row['name']]);source=read(ROOT/'examples/maxwell'/(row['name']+'.json'))
    assert source==c['specification'] and row['controls']=={**source,'solver':row['controls']['solver']}
    assert all(row['controls']['solver'].get(k)==v for k,v in source['solver'].items());assert row['result']==row['replayed_result'];m.assess(c,row['result'])
   parity=assess_parity(Path(native_peer),out);write_new(out/'parity.json',parity)
  guard(plan_path);assert artifacts(build,backend)==before
  result={'status':'passed','bindings':bindings,'reference_cases':len(cases),'transaction_cases':len(tc),'original_bounds_and_settings':True,'events_sha256':sha(journal.path),'files':{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ['events.jsonl','summary.json']}}
 except Exception as e:
  journal.emit({'kind':'exception','type':type(e).__name__,'error':str(e)});write_new(out/'summary.json',{'status':'failed','bindings':bindings,'error':str(e),'events_sha256':sha(journal.path)});raise
 write_new(out/'summary.json',result);print(json.dumps(result,indent=2))

def assess_parity(native,wasm):
 # Execute the original comparer prefix unchanged. Its legacy path-bound loop and
 # report write are deliberately NOT executed; only original compare() is reused.
 path=ROOT/BASE/'compare_backends_v2.py';source=path.read_text();marker="for suffix in ('raw','transactions-raw'):";assert source.count(marker)==1
 namespace={'__file__':str(path)};exec(compile(source.split(marker)[0],str(path),'exec'),namespace)
 for filename in ['reference-raw.json','transaction-raw.json']:
  nr,wr=read(native/filename),read(wasm/filename);assert [r['id'] for r in nr]==[r['id'] for r in wr]
  for n,w in zip(nr,wr):
   assert len(n['calls'])==len(w['calls'])==2
   for a,b in zip(n['calls'],w['calls']):assert a['returncode']==b['returncode'];namespace['compare'](json.loads(a['stdout']),json.loads(b['stdout']))
 return {'passed':True,'numeric_comparisons':namespace['COUNT'],'maximum_stress_difference_Pa':namespace['MAX_STRESS'],'maximum_strain_or_rate_difference':namespace['MAX_STRAIN'],'unchanged_original_comparer_sha256':sha(path)}

def check_saved(folder,summary):
 if summary['status']!='passed':raise ValueError('Saved backend did not pass')
 if sha(folder/'events.jsonl')!=summary['events_sha256']:raise ValueError('Changed backend journal')
 for name,h in summary['files'].items():
  if sha(folder/name)!=h:raise ValueError('Changed saved result '+name)
 for pin in summary['bindings']['build_receipts']:
  if sha(pin['path'])!=pin['sha256'] or sha(Path(pin['path']).with_suffix('.log'))!=pin['log_sha256']:raise ValueError('Changed terminal build receipt/log')

def complete_results(plan_path,native,wasm,build,out):
 plan,m,tx=guard(plan_path);native,wasm,build,out=map(Path,[native,wasm,build,out]);ns,ws=read(native/'summary.json'),read(wasm/'summary.json')
 for folder,s in [(native,ns),(wasm,ws)]:
  assert s['status']=='passed' and s['bindings']['plan_sha256']==sha(plan_path)
  check_saved(folder,s)
 assert ws['bindings']['native_peer_summary_sha256']==sha(native/'summary.json');assert ws['bindings']['artifacts']==artifacts(build,'wasm')
 binding={'model_sha256':sha(ROOT/DEFINITION),'catalogue_file_sha256':sha(build/'generated/models.json'),'module_sha256':sha(build/'maxwell.js'),'wasm_sha256':sha(build/'maxwell.wasm'),'source_manifest_sha256':plan['source_manifest']['sha256'],'reference_policy_sha256':sha(ROOT/BASE/'reference-cases.json')}
 parity=assess_parity(native,wasm)
 result={'status':'passed-pending-independent-build-review','implementation_run':plan['implementation_run'],'binding':binding,'gates':{g:True for g in GATES},'native_summary':{'path':str(native/'summary.json'),'sha256':sha(native/'summary.json')},'wasm_summary':{'path':str(wasm/'summary.json'),'sha256':sha(wasm/'summary.json')},'parity':parity,'limitations':plan['limits']}
 write_new(out,result);print(json.dumps(result,indent=2))

def finalize(plan_path,results_path,review_path,build):
 plan,m,tx=guard(plan_path);result=read(results_path);review=read(review_path);build=Path(build)
 assert result['status']=='passed-pending-independent-build-review'
 for key in ['native_summary','wasm_summary']:
  pin=result[key];path=Path(pin['path']);assert sha(path)==pin['sha256'];check_saved(path.parent,read(path))
 assert review['status']=='accepted' and review['binding']==result['binding'] and review['gates']==result['gates']=={g:True for g in GATES}
 assert isinstance(review['reviewer_run'],str) and review['reviewer_run'].strip() and review['reviewer_run']!=plan['implementation_run']
 assert review['blocking_findings']==[] and review['results_sha256']==sha(results_path)
 current={'model_sha256':sha(ROOT/DEFINITION),'catalogue_file_sha256':sha(build/'generated/models.json'),'module_sha256':sha(build/'maxwell.js'),'wasm_sha256':sha(build/'maxwell.wasm'),'source_manifest_sha256':plan['source_manifest']['sha256'],'reference_policy_sha256':sha(ROOT/BASE/'reference-cases.json')};assert current==result['binding']
 # Preserve the accepted review's exact original bytes in the build; never overwrite.
 with (build/'build-review.json').open('xb') as f:f.write(Path(review_path).read_bytes())
 qualification={'schema_version':'maxwell-qualified-build-1','model':MODEL,'status':'passed','implementation_run':plan['implementation_run'],'binding':current,'gates':result['gates'],'independent_review':{'path':'build-review.json','sha256':sha(build/'build-review.json')},'results_manifest':{'path':str(Path(results_path).resolve().relative_to(ROOT)),'sha256':sha(results_path)},'scope':plan['limits']}
 write_new(build/'maxwell-qualification.json',qualification);print(json.dumps(qualification,indent=2))

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True);sub.add_parser('freeze')
 for name in ['native','wasm']:
  q=sub.add_parser(name);q.add_argument('--plan',type=Path,default=ROOT/PACKET/'plan.json');q.add_argument('--build',type=Path,required=True);q.add_argument('--output',type=Path,required=True);q.add_argument('--configure-receipt',type=Path,required=True);q.add_argument('--build-receipt',type=Path,required=True)
  if name=='wasm':q.add_argument('--native-peer',type=Path,required=True)
 q=sub.add_parser('results');q.add_argument('--plan',type=Path,default=ROOT/PACKET/'plan.json');q.add_argument('--native',type=Path,required=True);q.add_argument('--wasm',type=Path,required=True);q.add_argument('--build',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
 q=sub.add_parser('finalize');q.add_argument('--plan',type=Path,default=ROOT/PACKET/'plan.json');q.add_argument('--results',type=Path,required=True);q.add_argument('--review',type=Path,required=True);q.add_argument('--build',type=Path,required=True)
 a=p.parse_args()
 if a.command=='freeze':freeze()
 elif a.command in ['native','wasm']:collect(a.command,a.plan,a.build,a.output,getattr(a,'native_peer',None),a.configure_receipt,a.build_receipt)
 elif a.command=='results':complete_results(a.plan,a.native,a.wasm,a.build,a.output)
 else:finalize(a.plan,a.results,a.review,a.build)
if __name__=='__main__':main()
