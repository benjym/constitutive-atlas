from pathlib import Path
import subprocess,json,hashlib,os,sys,datetime
root=Path('/Users/bmar5496/code/constitutive-atlas');stage=Path(__file__).parent
role=sys.argv[1]
if role not in ['native','wasm']:raise RuntimeError('role')
freeze=json.loads((stage/'prospective-freeze.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 for name,digest in freeze['source_files'].items():
  if sha(root/name)!=digest:raise RuntimeError('source changed '+name)
 for name,digest in freeze['local_files'].items():
  if sha(stage/name)!=digest:raise RuntimeError('study changed '+name)
verify()
build=Path('/private/tmp')/f'atlas-explicit-controls-{role}-v1'
commands=[['cmake','-S',str(root),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(build),'--target','atlas_solver','--parallel','1']]
if role=='wasm':commands[0].insert(0,'emcmake')
env={**os.environ,'EMCC_CORES':'1','PYTHONDONTWRITEBYTECODE':'1'}
for i,argv in enumerate(commands):
 receipt=stage/f'{role}-command-{i}.json'
 if receipt.exists():raise RuntimeError('preserve existing receipt')
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(argv,cwd=root,env=env,text=True,capture_output=True)
 receipt.write_text(json.dumps({'argv':argv,'EMCC_CORES':'1','started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
 print(role,i,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
 verify()
artifacts={}
for name in (['atlas_solver']if role=='native'else['atlas.js','atlas.wasm'])+['generated/models.hpp','generated/models.json']:
 p=build/name;artifacts[name]={'path':str(p),'sha256':sha(p)}
(stage/f'{role}-artifacts.json').write_text(json.dumps(artifacts,indent=2)+'\n')
