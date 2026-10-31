from pathlib import Path
import subprocess,os,json,hashlib
R=Path('/Users/bmar5496/code/constitutive-atlas');W=Path('/private/tmp/atlas-dp-web-v1');S=R/'catalogue/investigations/dp-dilatancy-domain-v1/source'
env=dict(os.environ,EMCC_CORES='1',EM_CACHE=str(R/'.cache/emscripten'),PYTHONDONTWRITEBYTECODE='1')
for i,argv in enumerate([['emcmake','cmake','-S',str(S),'-B',str(W/'build'),'-DCMAKE_BUILD_TYPE=Debug'],['cmake','--build',str(W/'build'),'--target','atlas_solver','--parallel','1']]):
 p=subprocess.run(argv,env=env,text=True,capture_output=True);(W/f'build-command-{i}.json').write_text(json.dumps({'argv':argv,'EMCC_CORES':'1','EM_CACHE':env['EM_CACHE'],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n');print(i,p.returncode,flush=True)
 if p.returncode:raise SystemExit(p.returncode)
