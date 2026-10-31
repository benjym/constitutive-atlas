from pathlib import Path
import json,subprocess,hashlib,datetime,os,sys,platform
s=Path(__file__).resolve().parent;backend=sys.argv[1];assert backend in('native','wasm')
b=Path('/private/tmp/atlas-barodesy-preview-'+backend+'-v2');out=s/backend;assert not out.exists();out.mkdir()
for table in ('manifest.json','execution-freeze.json'):
 for name,pin in json.loads((s/table).read_text()).items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==pin,name
env=os.environ.copy();env.update(EMCC_CORES='1',EM_CACHE='/Users/bmar5496/code/constitutive-atlas/.cache/emscripten')
receipt={'backend':backend,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':platform.platform(),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'commands':[],'artifacts':{}}
def save(): (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def run(label,cmd,expected=(0,)):
 p=subprocess.run(cmd,env=env,capture_output=True);(out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 receipt['commands'].append({'label':label,'argv':cmd,'exit_code':p.returncode});save();print(backend,label,p.returncode,flush=True)
 assert p.returncode in expected,(label,p.returncode)
 return p
cmd=['cmake','-S',str(s),'-B',str(b),'-DCMAKE_BUILD_TYPE=Release']
if backend=='wasm':cmd=['/opt/homebrew/bin/emcmake']+cmd
run('configure',cmd);run('build',['cmake','--build',str(b),'--target','atlas_barodesy_preview','--parallel','1'])
for name in (['atlas_barodesy_preview']if backend=='native'else['atlas-barodesy-preview.js','atlas-barodesy-preview.wasm']):
 p=b/name;receipt['artifacts'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size};save()
if backend=='native':
 rows=[]
 p=run('describe',[str(b/'atlas_barodesy_preview'),'--describe']);rows.append({'id':'describe','raw':p.stdout.decode()})
 for i,r in enumerate(json.loads((s/'requests.json').read_text())):
  cmd=[str(b/'atlas_barodesy_preview'),'--mode',r['mode'],'--model',r['model'],'--parameters',r['parameters'],'--initial',r['initial']]
  for k in (['protocol','target','steps','cycles']if r['mode']=='run'else['strain']):cmd+=['--'+k,str(r[k])]
  p=run('request-'+str(i),cmd,(0,)if r['expected_ok']else(1,));rows.append({'id':r['id'],'request':r,'raw':p.stdout.decode()});(out/'journal.json').write_text(json.dumps(rows,indent=2)+'\n')
else:run('observe',['/opt/homebrew/bin/node',str(s/'observe.mjs'),str(s),str(b),str(out)])
receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
