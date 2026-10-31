"""Coordinator-only serial builds and raw collection from a prospective freeze."""
from pathlib import Path
import json,subprocess,hashlib,datetime,os,sys,platform
s=Path(__file__).resolve().parent;backend=sys.argv[1]
if backend not in('native','wasm'):raise RuntimeError('backend')
b=Path('/private/tmp/atlas-mc-explicit-paths-'+backend+'-v1');out=s/backend
if out.exists()or b.exists():raise RuntimeError('preserve existing execution')
manifest=json.loads((s/'manifest.json').read_text())
def verify():
 for name,pin in manifest.items():
  if hashlib.sha256((s/name).read_bytes()).hexdigest()!=pin:raise RuntimeError('changed '+name)
verify();out.mkdir()
env=dict(os.environ,EMCC_CORES='1',PYTHONDONTWRITEBYTECODE='1')
freeze=json.loads((s/'prospective-freeze.json').read_text())
if freeze['compiled_observations_at_freeze']!=0 or freeze['manifest_sha256']!=hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest():raise RuntimeError('freeze')
receipt={'backend':backend,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':platform.platform(),'EMCC_CORES':'1','manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'commands':[],'artifacts':{},'completed':False}
def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def run(label,cmd,expected=(0,)):
 try:p=subprocess.run(cmd,env=env,capture_output=True,timeout=180)
 except Exception as exc:receipt['error']=repr(exc);save();raise
 (out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 receipt['commands'].append({'label':label,'argv':cmd,'exit_code':p.returncode,'ATLAS_SOLVER':env.get('ATLAS_SOLVER')});save();print(backend,label,p.returncode,flush=True)
 if p.returncode not in expected:raise RuntimeError(label+' failed')
 return p
save();run('toolchain',['c++'if backend=='native'else'emcc','--version'])
cmd=['cmake','-S',str(s),'-B',str(b),'-DCMAKE_BUILD_TYPE=Release']
if backend=='wasm':cmd.insert(0,'emcmake')
run('configure',cmd);run('build',['cmake','--build',str(b),'--target','atlas_laboratory_preview','--parallel','1'])
for name in(['atlas_laboratory_preview']if backend=='native'else['atlas-preview.js','atlas-preview.wasm']):
 p=b/name;receipt['artifacts'][name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size};save()
if backend=='wasm':(b/'package.json').write_text('{"type":"module"}\n')
run('observe',['node',str(s/'observe.mjs'),str(s),backend,str(b),str(out)])
run('assess',['python3','-B',str(s/'assess_paths.py'),str(out/'journal.json')])
if backend=='native':
 # Keep explicit per-command ATLAS_SOLVER in receipt rather than an implicit fixture fallback.
 previous=env.get('ATLAS_SOLVER');env['ATLAS_SOLVER']=str(b/'atlas_laboratory_preview')
 run('initial-checks',['python3','-B','-m','unittest','discover','-s',str(s/'tests'),'-p','test_laboratory_initial_checks.py','-v'])
 if previous is None:env.pop('ATLAS_SOLVER')
 else:env['ATLAS_SOLVER']=previous
verify();receipt.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),completed=True,journal_sha256=hashlib.sha256((out/'journal.json').read_bytes()).hexdigest(),rejections_sha256=hashlib.sha256((out/'rejections.json').read_bytes()).hexdigest());save()
