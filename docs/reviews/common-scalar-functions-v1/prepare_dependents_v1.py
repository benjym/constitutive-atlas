"""Freeze unchanged dependent package numerical gates; no compiled calls/builds."""
from pathlib import Path
import json,hashlib,shutil
r=Path.cwd();p=r/'docs/reviews/common-scalar-functions-v1';base=Path('/private/tmp/atlas-common-scalar-functions-v1/dependents-v1');src=base/'source';assert not base.exists();shutil.copytree('/private/tmp/atlas-common-scalar-functions-v1/consumer-source-v1',src);same={};patches=[]
def cp(name):
 f=r/name;d=src/name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);same[name]=hashlib.sha256(f.read_bytes()).hexdigest()
maxbase='docs/ingestion/maxwell-itasca900/integration-v1/'
extras=['tests/test_maxwell.py','docs/ingestion/maxwell-itasca900/atlas-build-v1/assess_presets.py']+[maxbase+n for n in ['reference-cases.json','check_transactions.py','compare_backends_v2.py','PLAN.md']]+['examples/maxwell/'+n+'.json' for n in ['relaxation','creep','oedometer','load-hold-reverse']]
norbase='docs/ingestion/norsand-1993/e2-v3/'
extras += [norbase+n for n in ['run_native_requests_v2.py','run_wasm_requests_v2.mjs','check_backend_results_v3.py','backend-requests-v2.json','CONTRACT.md']]
for n in extras:cp(n)
f=src/(maxbase+'check_transactions.py');data=f.read_bytes();old=b'/private/tmp/atlas-maxwell-execution-v1/cli';assert data.count(old)==1;new=str(base/'cli').encode();f.write_bytes(data.replace(old,new));patches.append({'path':maxbase+'check_transactions.py','original_sha256':same[maxbase+'check_transactions.py'],'copied_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'change':'Only hardcoded temporary CLI replay output directory; all requests/tolerances/logic unchanged'})
old=json.loads((r/'docs/ingestion/maxwell-itasca900/atlas-build-v1/prospective-commands.json').read_text());commands={}
for key,cmd in old['commands'].items():
 if key.endswith('_configure') or key.endswith('_build'):continue
 a=[]
 for x in cmd:
  x=x.replace('/private/tmp/atlas-maxwell-current-v1/source',str(src)).replace('/private/tmp/atlas-maxwell-current-v1/native','/private/tmp/atlas-common-scalar-functions-v1/consumers-native-v1/maxwell').replace('/private/tmp/atlas-maxwell-current-v1/wasm','/private/tmp/atlas-common-scalar-functions-v1/consumers-wasm-v1/maxwell').replace('/private/tmp/atlas-maxwell-current-v1/presets',str(base/'presets'))
  if x==str(r/'docs/ingestion/maxwell-itasca900/atlas-build-v1/assess_presets.py'):x=str(src/'docs/ingestion/maxwell-itasca900/atlas-build-v1/assess_presets.py')
  a.append(x)
 commands['maxwell_'+key]={'command':a,'cwd':str(src)}
(base/'presets').mkdir();models=';'.join(str(src/n) for n in ['models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'])
for backend in ['native','wasm']:
 b=base/('norsand-'+backend);commands['norsand_'+backend+'_configure']={'command':(['emcmake'] if backend=='wasm' else [])+['cmake','-S',str(src/'cmake/controlled-path'),'-B',str(b),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DATLAS_PATH_MODELS='+models]}
 commands['norsand_'+backend+'_build']={'command':['cmake','--build',str(b),'--target','atlas_path_capability','--parallel','1']}
 req=str(src/(norbase+'backend-requests-v2.json'));out=str(base/('norsand-'+backend+'-results.json'))
 commands['norsand_'+backend+'_run']={'command':(['python3',str(src/(norbase+'run_native_requests_v2.py')),str(b/'libatlas_path_capability.dylib')] if backend=='native' else ['node',str(src/(norbase+'run_wasm_requests_v2.mjs')),str(b/'atlas_path_capability.mjs'),str(b/'atlas_path_capability.wasm')])+[req,out]}
commands['norsand_assess']={'command':['python3',str(src/(norbase+'check_backend_results_v3.py')),str(src/(norbase+'backend-requests-v2.json')),str(base/'norsand-native-results.json'),str(base/'norsand-wasm-results.json')]}
(p/'dependent-commands-v1.json').write_text(json.dumps({'commands':commands,'source':str(src),'unchanged_inputs':same,'driver_path_patches':patches,'Maxwell_artifacts':'Exact acceptedconsumer native/Wasm maxwell targets; provenance consumer-source-freeze-v1/actualaudits mustverify beforecalls','gate_policy':'Unchanged Maxwell48main+28supplement+4CLI presets/5962parity; NorSand58=40success18rejections plus exactold2e-11 parity; no tolerancechanges'},indent=2)+'\n')
fs=[f for f in src.rglob('*') if f.is_file() and '__pycache__' not in f.parts];(p/'dependent-source-freeze-v1.json').write_text(json.dumps({'source':str(src),'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(fs)},'status':'Prospective unchanged dependent numericalqualification; no fresh compiledcalls for these gates'},indent=2)+'\n');print(len(fs),'dependentfiles; exactoldpolicy commands staged')
