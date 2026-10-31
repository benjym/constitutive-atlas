"""Coordinator-only serial build and opaque C-ABI/CLI collection."""
from pathlib import Path
import json,subprocess,hashlib,datetime,os,sys,platform
s=Path(__file__).resolve().parent;backend=sys.argv[1];assert backend in('native','wasm')
b=Path('/private/tmp/atlas-clay2013-preview-'+backend+'-v1');out=s/backend;assert not out.exists()and not b.exists();out.mkdir()
for name,pin in json.loads((s/'manifest.json').read_text()).items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==pin,name
env=dict(os.environ,EMCC_CORES='1',EM_CACHE='/Users/bmar5496/code/constitutive-atlas/.cache/emscripten')
receipt={'backend':backend,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':platform.platform(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'commands':[],'artifacts':{},'completed':False}
def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def run(label,cmd,expected=(0,)):
 try:p=subprocess.run(cmd,env=env,capture_output=True,timeout=180)
 except Exception as exc:
  receipt['error']=repr(exc);save();raise
 (out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 receipt['commands'].append({'label':label,'argv':cmd,'exit_code':p.returncode});save();print(backend,label,p.returncode,flush=True)
 assert p.returncode in expected,(label,p.returncode)
 return p
save();run('toolchain',['c++'if backend=='native'else'emcc','--version'])
cmd=['cmake','-S',str(s),'-B',str(b),'-DCMAKE_BUILD_TYPE=Release']
if backend=='wasm':cmd.insert(0,'emcmake')
run('configure',cmd);run('build',['cmake','--build',str(b),'--target','atlas_laboratory_preview','--parallel','1'])
for name in(['atlas_laboratory_preview']if backend=='native'else['atlas-preview.js','atlas-preview.wasm']):
 p=b/name;receipt['artifacts'][name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size};save()
if backend=='native':
 rows=[];p=run('describe',[str(b/'atlas_laboratory_preview'),'--describe']);rows.append({'id':'describe','raw':p.stdout.decode()});(out/'journal.json').write_text(json.dumps(rows,indent=2)+'\n')
 for i,r in enumerate(json.loads((s/'requests.json').read_text())):
  cmd=[str(b/'atlas_laboratory_preview'),'--mode',r['mode'],'--model',r['model'],'--parameters',r['parameters'],'--initial',r['initial'],'--integration-settings',r['integration_settings']]
  for k in(['protocol','target','steps','cycles']if r['mode']=='run'else['strain']):cmd+=['--'+k,str(r[k])]
  p=run('request-'+str(i),cmd,(0,1));rows.append({'id':r['id'],'request':r,'raw':p.stdout.decode()});(out/'journal.json').write_text(json.dumps(rows,indent=2)+'\n')
else:run('observe',['node',str(s/'observe.mjs'),str(s),str(b),str(out)])
for name,pin in json.loads((s/'manifest.json').read_text()).items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==pin,name
receipt.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),completed=True,journal_sha256=hashlib.sha256((out/'journal.json').read_bytes()).hexdigest());save()
