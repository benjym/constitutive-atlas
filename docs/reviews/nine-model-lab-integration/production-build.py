"""Coordinator serial production build from exact frozen integration source pins."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(role):
 assert role in('native','wasm');work=Path('/private/tmp/atlas-nine-model-'+role+'-v1');assert not work.exists()
 pins=json.loads((HERE/'integration-inputs.json').read_text())['source_files']
 for name,pin in pins.items():assert sha(ROOT/name)==pin,name
 env=dict(os.environ,EMCC_CORES='1',EM_CACHE=str(ROOT/'.cache/emscripten'))
 configure=['cmake','-S',str(ROOT),'-B',str(work),'-DCMAKE_BUILD_TYPE=Release']
 if role=='wasm':configure.insert(0,'emcmake')
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();retained=[]
 for i,argv in enumerate([configure,['cmake','--build',str(work),'--target','atlas_solver','--parallel','1']]):
  run=subprocess.run(argv,cwd=ROOT,env=env,text=True,capture_output=True,timeout=180)
  p=HERE/(role+'-command-'+str(i)+'.json');assert not p.exists();p.write_text(json.dumps({'argv':argv,'EMCC_CORES':'1','returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2)+'\n');retained.append({'path':p.name,'sha256':sha(p)});print(role,i,run.returncode,flush=True);assert run.returncode==0,p
 for name,pin in pins.items():assert sha(ROOT/name)==pin,name
 study=ROOT/'catalogue/investigations/clay2005-preview-v1'
 for name in('models.hpp','models.json'):assert(work/'generated'/name).read_bytes()==(study/'generated'/name).read_bytes(),name
 artifacts=['atlas_solver']if role=='native'else['atlas.js','atlas.wasm']
 receipt={'role':role,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_pins_sha256':sha(HERE/'integration-inputs.json'),'commands':retained,'artifacts':{name:{'path':str(work/name),'sha256':sha(work/name)}for name in artifacts},'exact_frozen_generated_declarations':True}
 p=HERE/(role+'-build.json');assert not p.exists();p.write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':build(sys.argv[1])
