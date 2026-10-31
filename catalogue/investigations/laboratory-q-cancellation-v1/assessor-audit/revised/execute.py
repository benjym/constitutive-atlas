if not __debug__:raise RuntimeError('Required preservation checks cannot be optimized away')
from pathlib import Path
import json,hashlib,subprocess,sys,os,datetime,shutil
s=Path(__file__).parent;role=sys.argv[1];assert role in ['native','wasm','post']
for n,h in json.loads((s/'manifest.json').read_text()).items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==h,n
out=s/role;assert not out.exists();out.mkdir();env=dict(os.environ,EMCC_CORES='1',PYTHONDONTWRITEBYTECODE='1')
r={'role':role,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'completed':False,'commands':[],'artifacts':{}}
def save():(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
def call(label,cmd):
 try:p=subprocess.run(cmd,env=env,capture_output=True,timeout=180)
 except Exception as exc:r['error']=repr(exc);save();raise
 (out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 r['commands'].append({'label':label,'argv':cmd,'exit_code':p.returncode});save();print(role,label,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(label+' failed; original output retained')
save()
if role in ['native','wasm']:
 if role=='wasm':assert json.loads((s/'native/receipt.json').read_text())['completed']is True
 b=Path('/private/tmp/atlas-laboratory-q-'+role+'-v1');assert not b.exists()
 call('toolchain',['c++'if role=='native'else'emcc','--version'])
 cmd=['cmake','-S',str(s),'-B',str(b),'-DCMAKE_BUILD_TYPE=Release']
 if role=='wasm':cmd.insert(0,'emcmake')
 call('configure',cmd)
 for target in ['atlas_q_probe','atlas_solver']:call('build-'+target,['cmake','--build',str(b),'--target',target,'--parallel','1'])
 (b/'generated').mkdir();shutil.copyfile(s/'generated/models.json',b/'generated/models.json');shutil.copyfile(s/'generated/models.hpp',b/'generated/models.hpp')
 if role=='wasm':(b/'package.json').write_text('{"type":"module"}\n')
 for n in ['atlas_q_probe','atlas_solver']if role=='native'else['q-probe.js','q-probe.wasm','atlas.js','atlas.wasm']:
  p=b/n;r['artifacts'][n]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 save();call('observe-probe',['node',str(s/'observe_probe.mjs'),role,str(b),str(out/'probe.json')]);call('assess-probe',['python3','-B',str(s/'assess_probe.py'),str(out/'probe.json')])
else:
 for backend in ['native','wasm']:
  receipt=json.loads((s/backend/'receipt.json').read_text());assert receipt['completed']is True and receipt['manifest_sha256']==r['manifest_sha256']
  for a in receipt['artifacts'].values():assert hashlib.sha256(Path(a['path']).read_bytes()).hexdigest()==a['sha256']
 native='/private/tmp/atlas-laboratory-q-native-v1/atlas_solver';wasm='/private/tmp/atlas-laboratory-q-wasm-v1'
 call('browser-contracts',['node',str(s/'check_backends.mjs'),native,wasm,str(out/'backend-results.json')])
 call('field-invariance',['python3','-B',str(s/'assess_invariance.py'),str(out/'backend-results.json')])
 call('legacy-numerics',['node',str(s/'tools/test_numerics.mjs'),'--native',native,'--wasm',wasm+'/atlas.js','--output',str(out/'legacy-results.json')])
 call('generic-regressions',['node',str(s/'tools/test_wasm.mjs'),'--native',native,'--wasm-dir',wasm])
r.update(completed=True,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
