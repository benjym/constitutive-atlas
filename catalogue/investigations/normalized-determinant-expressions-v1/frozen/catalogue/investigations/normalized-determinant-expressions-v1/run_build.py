"""Coordinator-owned serial explicit-target build, with opaque command receipts."""
import argparse,datetime,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def write(p,d):
 assert not p.exists(),str(p);p.write_text(json.dumps(d,indent=2)+'\n')
def run(role):
 assert role in('native','wasm');work=Path('/private/tmp/atlas-normalized-determinant-context-'+role+'-v1');assert not work.exists()
 freeze=json.loads((HERE/'prospective-freeze.json').read_text());import hashlib
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 for name,pin in freeze['files'].items():assert sha(ROOT/name)==pin,name
 env=dict(os.environ,EMCC_CORES='1',EM_CACHE=str(ROOT/'.cache/emscripten'))
 configure=['cmake','-S',str(HERE),'-B',str(work),'-DCMAKE_BUILD_TYPE=Release']
 if role=='wasm':configure.insert(0,'emcmake')
 commands=[['cmake','--version'],['c++','--version']if role=='native'else['emcc','--version'],configure,['cmake','--build',str(work),'--target','atlas_normalized_determinant_context','--parallel','1']]
 retained=[]
 for i,cmd in enumerate(commands):
  start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,timeout=180)
  path=HERE/(role+'-command-'+str(i)+'.json');write(path,{'argv':cmd,'cwd':str(ROOT),'environment':{'EMCC_CORES':'1','EM_CACHE':env['EM_CACHE']},'started_utc':start,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});retained.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)});print(role,i,p.returncode,flush=True);assert p.returncode==0,path
 artifacts={'native':work/'atlas_normalized_determinant_context'}if role=='native'else{'loader':work/'normalized-determinant-context.mjs','wasm':work/'normalized-determinant-context.wasm'}
 for name,pin in freeze['files'].items():assert sha(ROOT/name)==pin,name
 write(HERE/(role+'-build.json'),{'role':role,'freeze_sha256':sha(HERE/'prospective-freeze.json'),'commands':retained,'artifacts':{k:{'path':str(p),'sha256':sha(p)}for k,p in artifacts.items()}})
if __name__=='__main__':p=argparse.ArgumentParser();p.add_argument('role');run(p.parse_args().role)
