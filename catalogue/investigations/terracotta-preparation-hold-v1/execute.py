"""Serial build and opaque schedule collection from the frozen source tree."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,os,platform
s=Path(__file__).resolve().parent;role=sys.argv[1];assert role in ('native','wasm')
build=Path('/private/tmp/atlas-terracotta-preparation-hold-'+role+'-v1');out=s/role
assert not build.exists() and not out.exists();out.mkdir()
manifest=json.loads((s/'manifest.json').read_text())
def verify():
 for n,h in manifest.items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==h,n
verify()
freeze=json.loads((s/'prospective-freeze.json').read_text());assert freeze['compiled_observations']==0
assert freeze['manifest_sha256']==hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest()
env=dict(os.environ,EMCC_CORES='1',EM_CACHE='/Users/bmar5496/code/constitutive-atlas/.cache/emscripten',PYTHONDONTWRITEBYTECODE='1')
receipt={'backend':role,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':platform.platform(),'environment':{k:env[k] for k in ['EMCC_CORES','EM_CACHE','PYTHONDONTWRITEBYTECODE']},'manifest_sha256':freeze['manifest_sha256'],'commands':[],'completed':False}
def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def run(label,argv,accepted=(0,)):
 p=subprocess.run(argv,capture_output=True,env=env,timeout=240)
 (out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 receipt['commands'].append({'label':label,'argv':argv,'returncode':p.returncode});save();print(role,label,p.returncode,flush=True)
 assert p.returncode in accepted,(label,p.returncode)
 return p
save();run('toolchain',['c++' if role=='native' else 'emcc','--version'])
configure=['cmake','-S',str(s),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release']
if role=='wasm':configure.insert(0,'emcmake')
run('configure',configure);run('build',['cmake','--build',str(build),'--target','atlas_terracotta_study','--parallel','1'])
for name in ['CMakeCache.txt','CMakeFiles/atlas_terracotta_study.dir/flags.make','CMakeFiles/atlas_terracotta_study.dir/link.txt']:
 (out/Path(name).name).write_bytes((build/name).read_bytes())
artifacts=['atlas_terracotta_study'] if role=='native' else ['terracotta-study.js','terracotta-study.wasm']
receipt['artifacts']={name:{'path':str(build/name),'sha256':hashlib.sha256((build/name).read_bytes()).hexdigest()} for name in artifacts};save()
if role=='native':
 # Import transport only from the frozen Python source capsule, never live Atlas.
 sys.path.insert(0,str(s/'frozen'));from atlas.schedule import schedule_command
 rows=[]
 for i,row in enumerate(json.loads((s/'requests.json').read_text())['records']):
  cmd=schedule_command(row['request'],build/'atlas_terracotta_study');p=run('request-'+str(i),cmd,(0,1))
  rows.append({**row,'raw':p.stdout.decode(),'returncode':p.returncode});(out/'journal.json').write_text(json.dumps(rows,indent=2)+'\n')
else:run('observe',['node',str(s/'observe.mjs'),str(s),str(build),str(out)])
verify();receipt.update(completed=True,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),journal_sha256=hashlib.sha256((out/'journal.json').read_bytes()).hexdigest());save()
