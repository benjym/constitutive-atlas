"""Freeze all live consumer build closures without compiling or editing shared paths."""
from pathlib import Path
import json,shutil,hashlib,subprocess,importlib.util,sys
from unittest.mock import patch
r=Path.cwd();p=r/'docs/reviews/common-scalar-functions-v1';dst=Path('/private/tmp/atlas-common-scalar-functions-v1/consumer-source-v1');assert not dst.exists();shutil.copytree('/private/tmp/atlas-common-scalar-functions-v1/engine-source-v1',dst)
extra=[]
for folder in ['docs/reviews/tensor-trace-implementation-v1','catalogue/investigations/trace-generated-context-v1','catalogue/investigations/trace-generated-context-v2']:
 for f in (r/folder).rglob('*'):
  if f.is_file() and f.suffix in ['.cpp','.hpp']:
   d=dst/f.relative_to(r);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);extra.append(str(f.relative_to(r)))
# Run only preparation paths; intercept NH's explicit build subprocesses.
sys.path.insert(0,str(dst))
def module(name,f):
 spec=importlib.util.spec_from_file_location(name,f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
state=module('common_state_contract',dst/'tools/prepare_state_contract_check.py');state.prepare(dst/'consumer-generated/state-contract')
nh=module('common_nh_generator',dst/'tools/run_nh2004.py');intercepted=[]
def capture(cmd,**kw):intercepted.append(cmd);return subprocess.CompletedProcess(cmd,0)
with patch.object(nh.subprocess,'run',side_effect=capture):nh.build(dst/'consumer-generated/nh2004')
assert len(intercepted)==2 and not (dst/'consumer-generated/nh2004/build').exists()
(p/'consumer-generation-v1.json').write_text(json.dumps({'new_extra_transitive_sources':extra,'NH_build_commands_intercepted_NOT_executed':intercepted,'statement':'Generated prospectiveCMake only; no compiledobservations'},indent=2)+'\n')
targets={'burgers':'atlas_burgers_solver','controlled-path':'atlas_path_capability','j2':'atlas_j2_solver','maxwell':'atlas_maxwell_solver','operator-trace':'atlas_trace_probe','research':'atlas_isolated','research-v3':'atlas_isolated','sls':'atlas_sls_solver','trace-context':'atlas_trace_context','trace-context-v2':'atlas_trace_context','state-contract':'atlas_state_contract','nh2004':'nh2004_solver'};cs={};tmp='/private/tmp/atlas-common-scalar-functions-v1'
for backend in ['native','wasm']:
 for name,t in targets.items():
  source=dst/('consumer-generated/'+name if name in ['state-contract','nh2004'] else 'cmake/'+name);build=tmp+'/consumers-'+backend+'-v1/'+name;config=(['emcmake'] if backend=='wasm' else [])+['cmake','-S',str(source),'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
  if name in ['research','research-v3']:config+=['-DATLAS_MODEL_FILE='+str(dst/'models/linear-elastic.json'),'-DATLAS_RESEARCH_TRANSPORT=rate']
  # Generated native-only CLI projects are qualified natively; no unsolicited Wasm transport promise.
  if backend=='wasm' and name in ['state-contract','nh2004']:continue
  cs[backend+'/'+name]={'configure':config,'build':['cmake','--build',build,'--target',t,'--parallel','1'],'target':t}
fs=[f for f in dst.rglob('*') if f.is_file() and '__pycache__' not in f.parts];(p/'consumer-source-freeze-v1.json').write_text(json.dumps({'source':str(dst),'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(fs)},'status':'Prospective12native+10Wasm consumer linkqualification; no materialapproval/compiledobservations'},indent=2)+'\n');(p/'consumer-commands-v1.json').write_text(json.dumps(cs,indent=2)+'\n');print(len(fs),'consumerclosurefiles',len(cs),'explicitconfigure/buildpairs')
