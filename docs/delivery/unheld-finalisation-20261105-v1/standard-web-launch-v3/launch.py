from pathlib import Path
import importlib.util,json,sys,hashlib,subprocess,shutil,time
HERE=Path(__file__).resolve().parent;N=HERE.parent
LAUNCH_SHA='0b1f14757dd91c767cf2cfb560236c75741166fdfbac3210623dd5db6e22f374'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(HERE/'launch.json')==LAUNCH_SHA
launch=json.loads((HERE/'launch.json').read_text());assert launch['ready_for_actual']is True
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
c=load('reviewed_C4',N/'rate-restoration-qualification-plan-v4/commands.py');m=c.m
a=load('reviewed_package_adapter',N/'standard-web-delivery-plan-v2/adapter.py')
pc=load('reviewed_packaging_continuation',N/'package-final-source-binding-v1/continuation.py')
pre=json.loads((N/'rate-restoration-qualification-actual-v3/source-freeze.json').read_text())
S=c.SOURCE;OPS=launch['recipe']['operations'];phase=sys.argv[1];ids=[x['id']for x in OPS];assert phase in ids
OUT=N/'standard-web-delivery-actual-v2';index=ids.index(phase)
if index:
 previous=json.loads((OUT/('outer-'+ids[index-1])/'receipt.json').read_text())
 assert previous['returncode']==0 and previous['mandatory_reap']is True and previous['reaped_returncode']==0
else:
 assert not OUT.exists(),'never overwrite a package observation'
 assert not Path('/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v2').exists(),'fresh site required'
def inventory(roots):
 paths=[]
 for root in map(Path,roots):
  for p in root.rglob('*'):
   if '__pycache__'in p.parts or p.name=='.DS_Store'or(S/'web/dist')in p.parents:continue
   if p.is_file():assert not p.is_symlink(),str(p);paths.append(p)
 return [m.pin(p)for p in sorted(paths)]
def guard():
 assert digest(HERE/'launch.json')==LAUNCH_SHA
 for dirname,expected in [('standard-web-delivery-plan-v1','b31cbd5299903175d0ca4d7bb86caa3c00c7acabc0e542442008a8287259b63e'),('standard-web-delivery-plan-v2','56ee1da7d8d1c6113a8dddedff6a85169ca9e8bbde20065d21526ca7b3dedf89')]:
  p=N/dirname;assert digest(p/'manifest.json')==expected
  for row in json.loads((p/'manifest.json').read_text())['files']:
   rel=Path(row['path']);assert not rel.is_absolute()and'..'not in rel.parts
   q=p/rel;assert not q.is_symlink()and digest(q)==row['sha256']and q.stat().st_size==row['size_bytes']
 assert pc.guard(S,'f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9')==launch['postcompile_continuation']
 for row in launch['independent_reviews']:
  m.verify(row);assert json.loads(Path(row['path']).read_text())['accepted']is True
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=S,text=True).strip()==launch['commit']
 for args in [['diff','--quiet'],['diff','--cached','--quiet']]:subprocess.run(['git',*args],cwd=S,check=True)
 assert inventory(launch['web_catalogue_data_input_roots'])==launch['web_catalogue_data_inputs']
 for row in [*launch['source_package_pins'],*launch['retained18'],*launch['other_role_pins']]:m.verify(row)
 assert inventory(launch['other_role_roots'])==sorted(launch['other_role_pins'],key=lambda r:r['path'])
 assert a.validate_recovery(a.RECEIPT_SHA)==launch['SLS_recovery']
guard()
ps=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,command='],text=True)
private=N.parents[2]/'.local/retained-evidence'/('baseline-five-C-web-v2-'+phase+'-preflight-20261105.raw');assert not private.exists();private.write_text(ps)
active=[]
for line in ps.splitlines():
 parts=line.strip().split(None,2)
 if len(parts)!=3:continue
 words=parts[2].split();base=Path(words[0]).name if words else ''
 if base.startswith('atlas_')or base in('clang','clang++','emcc','em++')or(base=='cmake'and'--build'in words)or(base in('node','nodejs')and any(s in parts[2]for s in('/wasm-cli.mjs','/extras.mjs'))):active.append({'pid':int(parts[0]),'executable':base})
assert not active,active
OUT.mkdir(exist_ok=True)
argv=OPS[index]['argv'];before={'epoch':time.time(),'phase':phase,'argv':argv,'commit':launch['commit'],'launch_sha256':LAUNCH_SHA,'private_process_inventory':str(private),'active_compiled':active,'free_bytes':shutil.disk_usage('/private/tmp').free,'ram_bytes':int(subprocess.check_output(['/usr/sbin/sysctl','-n','hw.memsize'],text=True))}
(OUT/(phase+'-preflight.json')).write_text(json.dumps(before,indent=2)+'\n')
assert digest(c.c.OBSERVER)==c.c.OBSERVER_SHA;o=load('original_observer',c.c.OBSERVER)
env=c.c.closed_environment();env.update(launch['recipe']['publication_environment_addition'])
primary=None;post={'phase':phase,'source_pre_passed':True,'source_post_passed':False}
try:
 def operation():
  observed=o.observe(argv,str(S),OUT/('outer-'+phase),env=env,timeout=1800)
  assert observed.returncode==0,'first package failure retained; stop later phases'
  return observed
 result=pc.observe(operation,S,'f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9',OUT/(phase+'-compiled-continuation.json'))
 post['returncode']=result.returncode;post['mandatory_reap']=result.receipt['mandatory_reap']
 assert result.returncode==0,'first package failure retained; stop later phases'
except BaseException as error:primary=error;post['primary_error']=repr(error);raise
finally:
 try:guard();post['source_post_passed']=True
 except BaseException as error:
  post['post_binding_error']=repr(error)
  if primary is None:raise
 finally:(OUT/(phase+'-source-binding.json')).write_text(json.dumps(post,indent=2)+'\n')
print(json.dumps({'phase':phase,'returncode':result.returncode,'mandatory_reap':result.receipt['mandatory_reap'],'elapsed_seconds':result.receipt['elapsed_seconds']}))
