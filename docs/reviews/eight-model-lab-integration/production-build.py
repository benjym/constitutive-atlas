from pathlib import Path
import subprocess,json,os,datetime
r=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
commands=[['emcmake','cmake','-S',str(r),'-B','/private/tmp/atlas-eight-model-wasm','-DCMAKE_BUILD_TYPE=Release'],['cmake','--build','/private/tmp/atlas-eight-model-wasm','--target','atlas_solver','--parallel','1']]
env=dict(os.environ,EMCC_CORES='1',EM_CACHE=str(r/'.cache/emscripten'))
for i,cmd in enumerate(commands):
 path=out/('wasm-production-command-'+str(i)+'.json');assert not path.exists()
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(cmd,cwd=r,env=env,text=True,capture_output=True,timeout=180)
 path.write_text(json.dumps({'argv':cmd,'cwd':str(r),'EMCC_CORES':'1','started_utc':start,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
 print(i,p.returncode,flush=True);assert p.returncode==0
