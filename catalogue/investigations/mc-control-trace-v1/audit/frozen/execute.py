from pathlib import Path
import json,hashlib,subprocess,sys,os,datetime
s=Path(__file__).resolve().parent;b=sys.argv[1];assert b in('native','wasm');out=s/b;build=Path('/private/tmp/atlas-control-trace-'+b+'-v1');assert not out.exists()and not build.exists();out.mkdir()
manifest=json.loads((s/'manifest.json').read_text())
for n,p in manifest.items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==p,n
env=dict(os.environ,EMCC_CORES='1');receipt={'backend':b,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'commands':[],'artifacts':{},'completed':False}
def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def run(label,cmd):
 p=subprocess.run(cmd,env=env,capture_output=True,timeout=180);(out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr);receipt['commands'].append({'label':label,'argv':cmd,'exit':p.returncode});save();print(b,label,p.returncode,flush=True);assert p.returncode==0
 return p
save();run('toolchain',['c++'if b=='native'else'emcc','--version']);cmd=['cmake','-S',str(s),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release']
if b=='wasm':cmd.insert(0,'emcmake')
run('configure',cmd);run('build',['cmake','--build',str(build),'--target','atlas_control_trace','--parallel','1'])
for name in (['atlas_control_trace']if b=='native'else['control-trace.js','control-trace.wasm']):
 p=build/name;receipt['artifacts'][name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};save()
if b=='native':
 p=run('observe',[str(build/'atlas_control_trace')]);(out/'raw.json').write_bytes(p.stdout)
else:run('observe',['node',str(s/'observe.mjs'),str(build),str(out/'raw.json')])
for n,p in manifest.items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==p,n
receipt.update(completed=True,raw_sha256=hashlib.sha256((out/'raw.json').read_bytes()).hexdigest());save()
