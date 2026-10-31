from pathlib import Path
import hashlib,json,os,subprocess,sys
R=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(R))
from atlas.evidence import verify_manifest_files
mode=sys.argv[1];assert mode in('native','wasm');packet=R/'catalogue/investigations/clay2014-paths-v1';source='catalogue/investigations/clay2014-paths-v1/preobservation-source.json';verify_manifest_files(R,source)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
folder='build'if mode=='native'else'build-wasm';commands=[['cmake','-S','.','-B',folder,'-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',folder,'--target','atlas_clay2014_solver','--parallel','1']]
env=os.environ.copy()
if mode=='wasm':env['EM_CACHE']=str(R/'.cache/emscripten')
commit=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True,check=True).stdout.strip();logs=packet/'logs';logs.mkdir(exist_ok=True);results=[]
for name,cmd in zip(('configure','build'),commands):
 log=logs/f'{mode}-{name}.txt';meta=logs/f'{mode}-{name}-command.json';assert not log.exists()and not meta.exists()
 meta.write_text(json.dumps({'argv':cmd,'cwd':str(R),'source_commit':commit,'preobservation_sha256':sha(R/source),'EM_CACHE':env.get('EM_CACHE')if mode=='wasm'else None,'runner_sha256':sha(__file__)},indent=2)+'\n')
 with log.open('xb')as out:completed=subprocess.run(cmd,cwd=R,env=env,stdout=out,stderr=subprocess.STDOUT)
 results.append({'argv':cmd,'returncode':completed.returncode,'log':log.relative_to(R).as_posix(),'log_sha256':sha(log),'command_record':meta.relative_to(R).as_posix(),'command_record_sha256':sha(meta)})
 print(mode,name,'exit',completed.returncode,flush=True)
 if completed.returncode:break
outputs=[f'{folder}/clay2014-generated/models.hpp',f'{folder}/clay2014-generated/models.json',f'{folder}/CMakeCache.txt']+([f'{folder}/atlas_clay2014_solver']if mode=='native'else[f'{folder}/clay2014-paths.js',f'{folder}/clay2014-paths.wasm'])
receipt={'version':'clay2014-path-build-receipt-v1','backend':mode,'source_commit':commit,'preobservation_sha256':sha(R/source),'commands':results,'all_commands_succeeded':len(results)==2 and all(x['returncode']==0 for x in results),'files':{p:sha(R/p)for p in outputs if(R/p).is_file()},'scope':'Local narrowly targeted serial build and exact artifact receipts; no reproducible-build, equation review or numerical acceptance claim.'}
p=packet/f'preobservation-{mode}-build.json';assert not p.exists();p.write_text(json.dumps(receipt,indent=2)+'\n');verify_manifest_files(R,source)
assert receipt['all_commands_succeeded'];assert len(receipt['files'])==len(outputs)
print(json.dumps({'backend':mode,'artifact_files':receipt['files']}),flush=True)
