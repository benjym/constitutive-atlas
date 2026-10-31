from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,sys
root=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(root))
from tools.research_rate_observations import checked_protocol,sha,digest
study=root/'catalogue/investigations/barodesy2015-rates-v1';protocol=study/'protocol.json';p,model,_=checked_protocol(protocol)
assert sha(protocol)=='f16ca12fc78ddbed79af78dc61ae9a17935174acf49b9cb77b37b63a35cb5a7d'
order=list(model['parameters']);native=json.loads((study/'native-generated-models.json').read_text());assert list(native['models'][0]['parameters'])==order
build=Path('/private/tmp/atlas-barodesy2015-wasm-v1');assert not build.exists(),'fresh build directory required'
receipt_path=study/'wasm-build.json';assert not receipt_path.exists()
env=os.environ.copy();env['EM_CACHE']=str(root/'.cache/emscripten');env['EMCC_CORES']='1'
commands=[['emcc','--version'],['node','--version'],['emcmake','cmake','-S',str(root/'cmake/research'),'-B',str(build),'-DATLAS_MODEL_FILE='+str(root/'docs/ingestion/barodesy-sand/rate-study-v2/model-draft.json'),'-DATLAS_RESEARCH_TRANSPORT=rate'],['cmake','--build',str(build),'--target','atlas_isolated','--parallel','1']]
rows=[]
for i,argv in enumerate(commands):
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();result=subprocess.run(argv,cwd=root,text=True,capture_output=True,env=env)
 doc={'argv':argv,'cwd':str(root),'environment':{k:env[k] for k in ('EM_CACHE','EMCC_CORES')},'started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
 path=study/f'wasm-build-command-{i}.json';assert not path.exists();path.write_text(json.dumps(doc,indent=2)+'\n');rows.append({'path':str(path.relative_to(root)),'sha256':sha(path),'returncode':result.returncode})
 print('Retained Wasm command',i,'returncode',result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
checked_protocol(protocol)
for source,target in ((build/'generated/models.hpp',study/'wasm-generated-models.hpp'),(build/'generated/models.json',study/'wasm-generated-models.json')):
 assert not target.exists();shutil.copyfile(source,target)
generated=json.loads((build/'generated/models.json').read_text());assert generated['models']==[model] and generated['sha256']==digest([model]);assert list(generated['models'][0]['parameters'])==order
for name in ('models.hpp','models.json'):assert (build/'generated'/name).read_bytes()==(study/('native-generated-'+name)).read_bytes()
script=study/'wasm-build-script.py';assert not script.exists();shutil.copyfile(__file__,script)
receipt={'version':'isolated-rate-build-receipt-0.1','backend':'wasm','protocol_sha256':sha(protocol),'all_commands_succeeded':True,'artifacts':{role:{'path':str(build/name),'sha256':sha(build/name)}for role,name in (('loader','atlas-isolated.js'),('wasm','atlas-isolated.wasm'))},'commands':rows,'generated':{p.name:sha(p) for p in (study/'wasm-generated-models.hpp',study/'wasm-generated-models.json')},'orchestration_sha256':sha(script),'source_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=root,text=True,capture_output=True,check=True).stdout.strip(),'parameter_order_checked':order}
receipt_path.write_text(json.dumps(receipt,indent=2)+'\n');print('Wasm build retained; no rate execution:',sha(receipt_path),flush=True)
