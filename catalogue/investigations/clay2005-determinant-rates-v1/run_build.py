"""Serial coordinator-only isolated build; retain commands before any rate call."""
import argparse,datetime,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools.research_rate_observations_v3 import checked_protocol,sha,require
HERE=Path(__file__).resolve().parent

def write(path,value):
 require(not path.exists(),'fresh receipt required: '+str(path))
 path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def main(backend):
 protocol=HERE/'protocol.json';checked_protocol(protocol)
 work=Path('/private/tmp/atlas-clay2005-determinant-'+backend+'-v1')
 require(not work.exists(),'fresh build directory required')
 receipt=HERE/(backend+'-build.json');require(not receipt.exists(),'fresh build receipt required')
 env=dict(os.environ,EMCC_CORES='1',EM_CACHE=str(ROOT/'.cache/emscripten'))
 commands=[['cmake','--version'],['c++','--version'] if backend=='native' else ['emcc','--version']]
 configure=['cmake','-S',str(ROOT/'cmake/research-v3'),'-B',str(work),'-DATLAS_MODEL_FILE='+str(HERE/'model.json'),'-DATLAS_RESEARCH_TRANSPORT=rate','-DCMAKE_BUILD_TYPE=Release']
 if backend=='wasm':configure.insert(0,'emcmake')
 commands.extend([configure,['cmake','--build',str(work),'--target','atlas_isolated','--parallel','1']])
 retained=[]
 for index,argv in enumerate(commands):
  start=datetime.datetime.now(datetime.timezone.utc).isoformat()
  run=subprocess.run(argv,cwd=ROOT,env=env,text=True,capture_output=True,timeout=180)
  path=HERE/(backend+'-build-command-'+str(index)+'.json')
  write(path,{'argv':argv,'cwd':str(ROOT),'environment':{k:env[k] for k in ('EM_CACHE','EMCC_CORES')},'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
  retained.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'returncode':run.returncode})
  print(backend,index,run.returncode,flush=True)
  if run.returncode:raise RuntimeError('build command failed; exact output retained in '+str(path))
 generated={}
 for name in ('models.hpp','models.json'):
  dst=HERE/(backend+'-generated-'+name);require(not dst.exists(),'fresh generated snapshot required')
  shutil.copyfile(work/'generated'/name,dst);generated[dst.name]=sha(dst)
 artifacts=({'native':work/'atlas_isolated'} if backend=='native' else {'loader':work/'atlas-isolated.js','wasm':work/'atlas-isolated.wasm'})
 checked_protocol(protocol)
 write(receipt,{'version':'isolated-rate-build-receipt-0.3','backend':backend,'protocol_sha256':sha(protocol),'all_commands_succeeded':True,'artifacts':{k:{'path':str(p),'sha256':sha(p)} for k,p in artifacts.items()},'commands':retained,'generated':generated,'build_script_sha256':sha(__file__),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('backend',choices=('native','wasm'));main(p.parse_args().backend)
