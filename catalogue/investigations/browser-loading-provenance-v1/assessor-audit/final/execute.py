if not __debug__: raise RuntimeError('Optimized Python disables required preservation checks')
from pathlib import Path
import json,hashlib,subprocess,sys,os,datetime,shutil
s=Path(__file__).parent;role=sys.argv[1]
assert role in ['pure','native','wasm','post']
for n,h in json.loads((s/'manifest.json').read_text()).items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==h,n
out=s/role;assert not out.exists();out.mkdir();env=dict(os.environ,EMCC_CORES='1',PYTHONDONTWRITEBYTECODE='1')
r={'role':role,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'completed':False,'commands':[],'artifacts':{}}
def save():(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
def call(label,cmd):
 p=subprocess.run(cmd,env=env,capture_output=True,timeout=180)
 (out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 r['commands'].append({'label':label,'argv':cmd,'exit_code':p.returncode});save();print(role,label,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(label+' failed; original output retained')
save()
if role=='pure':
 call('producer-contracts',['node',str(s/'test_loading.mjs'),str(out/'results.json')])
 call('markup',['python3','-B','-m','unittest','discover','-s',str(s/'tests'),'-p','test_browser_numerics.py','-v'])
 call('package-unit',['node','--test',str(s/'tests/test_web_package.mjs')])
elif role in ['native','wasm']:
 assert json.loads((s/'pure/receipt.json').read_text())['completed']is True
 if role=='wasm':assert json.loads((s/'native/receipt.json').read_text())['completed']is True
 b=Path('/private/tmp/atlas-browser-loading-'+role+'-v1');assert not b.exists()
 call('toolchain',['c++'if role=='native'else'emcc','--version'])
 cmd=['cmake','-S',str(s),'-B',str(b),'-DCMAKE_BUILD_TYPE=Release']
 if role=='wasm':cmd.insert(0,'emcmake')
 call('configure',cmd);call('build',['cmake','--build',str(b),'--target','atlas_solver','--parallel','1'])
 (b/'generated').mkdir();shutil.copyfile(s/'generated/models.json',b/'generated/models.json');shutil.copyfile(s/'generated/models.hpp',b/'generated/models.hpp')
 if role=='wasm':(b/'package.json').write_text('{"type":"module"}\n')
 for n in ['atlas_solver']if role=='native'else['atlas.js','atlas.wasm']:
  p=b/n;r['artifacts'][n]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
else:
 for backend in ['native','wasm']:
  receipt=json.loads((s/backend/'receipt.json').read_text());assert receipt['completed']is True
  assert receipt['manifest_sha256']==r['manifest_sha256']
  for a in receipt['artifacts'].values():assert hashlib.sha256(Path(a['path']).read_bytes()).hexdigest()==a['sha256']
 native='/private/tmp/atlas-browser-loading-native-v1/atlas_solver';wasm='/private/tmp/atlas-browser-loading-wasm-v1'
 call('browser-contracts',['node',str(s/'check_backends.mjs'),native,wasm,str(out/'backend-results.json')])
 call('legacy-numerics',['node',str(s/'tools/test_numerics.mjs'),'--native',native,'--wasm',wasm+'/atlas.js','--output',str(out/'legacy-numerics.json')])
 call('generic-regressions',['node',str(s/'tools/test_wasm.mjs'),'--native',native,'--wasm-dir',wasm])
r.update(completed=True,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
