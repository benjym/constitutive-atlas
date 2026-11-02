"""Coordinator-only serial common-engine stage with immutable-input guards/logs."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
plan=json.loads((OUT/'source-freeze-v2.json').read_text());work=Path(plan['snapshot']).parent
stage=sys.argv[1]
assert stage in ['native-build','native-calls','wasm-build','wasm-calls']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def guard():
 for n,h in plan['source_closure'].items():assert sha(ROOT/n)==sha(Path(plan['snapshot'])/n)==h,('source drift',n)
 for n,h in (plan['cases']|plan['transport_sources']).items():assert sha(ROOT/n)==h,('evidence drift',n)
guard();dest=OUT/stage;dest.mkdir(exist_ok=False)
env=os.environ.copy();env['EM_CACHE']=str(work/'em-cache')
source=Path(plan['snapshot']);model=source/'models/research/interface2016/hvwe2016-reconciled-fixed-local.json';req=ROOT/'docs/ingestion/hypoplastic-interface-2016/implementation-v1/backend-requests.json'
commands=[]
if stage=='native-build':
 commands=[['cmake','-S',str(source/'cmake/controlled-path'),'-B',str(work/'native'),'-DCMAKE_BUILD_TYPE=Release','-DATLAS_PATH_MODELS='+str(model),'-DPython3_EXECUTABLE='+sys.executable],['cmake','--build',str(work/'native'),'--target','atlas_path_capability','--parallel','1','--verbose']]
elif stage=='wasm-build':
 commands=[['emcmake','cmake','-S',str(source/'cmake/controlled-path'),'-B',str(work/'wasm'),'-DCMAKE_BUILD_TYPE=Release','-DATLAS_PATH_MODELS='+str(model),'-DPython3_EXECUTABLE='+sys.executable],['cmake','--build',str(work/'wasm'),'--target','atlas_path_capability','--parallel','1','--verbose']]
else:
 result=OUT/('native-results.json' if stage=='native-calls' else 'wasm-results.json')
 if stage=='native-calls':
  libs=list((work/'native').glob('libatlas_path_capability.*'));assert len(libs)==1
  commands=[[sys.executable,'-B',str(ROOT/'docs/ingestion/norsand-1993/e2-v3/run_native_requests_v2.py'),str(libs[0]),str(req),str(result)]]
 else:commands=[['node',str(ROOT/'docs/ingestion/norsand-1993/e2-v3/run_wasm_requests_v2.mjs'),str(work/'wasm/atlas_path_capability.mjs'),str(work/'wasm/atlas_path_capability.wasm'),str(req),str(result)]]
 commands.append([sys.executable,'-B',str(ROOT/'docs/ingestion/hypoplastic-interface-2016/implementation-v1/check_backend_results_v2.py'),str(result),'--output',str(OUT/(stage+'-assessment.json'))])
record={'stage':stage,'commands':[],'source_freeze_sha256':sha(OUT/'source-freeze-v2.json'),'status':'running'}
try:
 for i,argv in enumerate(commands):
  guard();start=time.time();log=dest/(str(i+1)+'.log')
  with log.open('wb') as output:
   p=subprocess.run(argv,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=180)
  row={'argv':argv,'exit':p.returncode,'seconds':time.time()-start,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log)};record['commands'].append(row)
  (dest/'receipt.json').write_text(json.dumps(record,indent=2)+'\n');guard()
  if p.returncode:raise RuntimeError('Child failed: '+str(argv))
 record['status']='passed'
except BaseException as e:
 record['status']='failed';record['error']=repr(e);raise
finally:(dest/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'stage':stage,'status':record['status'],'children':len(record['commands'])}))
