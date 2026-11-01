from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
p=Path(__file__).resolve().parent;r=p.parents[2];backend=sys.argv[1];assert backend in('native','wasm')
out=p/backend;assert not out.exists(),'refusing to overwrite observations';out.mkdir()
freeze=json.loads((p/'prospective-freeze.json').read_text());sources=json.loads((p/'source-pins.json').read_text())['sources']
def check():
    for n,h in freeze['files'].items():assert hashlib.sha256((p/n).read_bytes()).hexdigest()==h,n
    for n,h in sources.items():assert hashlib.sha256((r/n).read_bytes()).hexdigest()==h,n
check();build=Path('/private/tmp/atlas-loading-mixed-v1')/backend
receipt={'backend':backend,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[],'artifacts':{}}
env=os.environ.copy();env.update(EMCC_CORES='1',EM_CACHE=str(r/'.cache/emscripten'))
def run(label,args):
    proc=subprocess.run(args,cwd=r,env=env,capture_output=True)
    (out/(label+'.stdout.txt')).write_bytes(proc.stdout);(out/(label+'.stderr.txt')).write_bytes(proc.stderr)
    receipt['commands'].append({'label':label,'argv':args,'exit_code':proc.returncode})
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(backend,label,proc.returncode,flush=True)
    if proc.returncode:raise SystemExit(proc.returncode)
args=['cmake','-S',str(r),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release']
if backend=='wasm':args=['/opt/homebrew/bin/emcmake']+args
run('configure',args);run('build',['cmake','--build',str(build),'--target','atlas_solver','--parallel','1'])
for name in ['models.hpp','models.json']:
    assert (build/'generated'/name).read_bytes()==(p/'expected-generated'/name).read_bytes(),name
names=['atlas_solver']if backend=='native'else['atlas.js','atlas.wasm']
for n in names:
    data=(build/n).read_bytes();receipt['artifacts'][n]={'path':str(build/n),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
if backend=='native':run('observe',[sys.executable,'-B',str(p/'collect_native.py'),str(build/'atlas_solver')])
else:run('observe',['/opt/homebrew/bin/node',str(p/'collect_wasm.mjs'),str(build/'atlas.js'),str(p/'requests.json')])
check();receipt['all_build_inputs_unchanged_after_collection']=True;receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
