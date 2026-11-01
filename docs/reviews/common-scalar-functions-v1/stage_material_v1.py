"""Distinct unchanged Duncan E4 execution against proposed common scalar runtime."""
from pathlib import Path
import json,hashlib,shutil
r=Path.cwd();p=r/'docs/reviews/common-scalar-functions-v1';old=r/'docs/ingestion/duncan-chang-1970/material-v1';dst=p/'material-reference-v1';assert not dst.exists();dst.mkdir();b=dst/'execution-v3';b.mkdir();same={}
def cp(f,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);same[str(f.relative_to(r))]=dict(copy=str(d.relative_to(r)),sha256=hashlib.sha256(f.read_bytes()).hexdigest())
for n in ['reference.py','references.json','refinement.py','refinement-references.json','smooth_v2.py','smooth-v2.json']:cp(old/n,dst/n)
for n in ['POLICY.md','candidate.json','requests.json','requests-binary64.json','inspector.cpp','collect_native.py','collect_wasm.mjs','assess-v2.py','assess_partition_diagnostics.py','parity.py']:cp(old/'execution-v2'/n,b/n)
for f in sorted((old/'execution-v2/frozen/generated').glob('*')):
 if f.is_file():cp(f,b/'frozen/generated'/f.name)
source=Path('/private/tmp/atlas-common-scalar-functions-v1/scalar-probe-source-v1')
for f in sorted((source/'cpp').rglob('*')):
 if f.is_file():
  d=b/'frozen'/f.relative_to(source);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
cp(r/'cpp/main.cpp',b/'frozen/cpp/main.cpp')
cm=(old/'execution-v2/CMakeLists.txt').read_text().replace('LANGUAGES CXX','LANGUAGES C CXX').replace('set(CMAKE_CXX_STANDARD_REQUIRED ON)','set(CMAKE_CXX_STANDARD_REQUIRED ON)\ninclude("${CMAKE_CURRENT_SOURCE_DIR}/frozen/cmake/AtlasScalarFunctions.cmake")')
(b/'CMakeLists.txt').write_text(cm);d=b/'frozen/cmake/AtlasScalarFunctions.cmake';d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p/'proposed-v2/cmake/AtlasScalarFunctions.cmake',d)
(dst/'unchanged-bindings.json').write_text(json.dumps(same,indent=2)+'\n')
files=[f for f in dst.rglob('*') if f.is_file()];(p/'material-source-freeze-v1.json').write_text(json.dumps({'identity':'duncan-complete-material-common-scalar-execution-v3','source':str(b),'unchanged_original_policy':'72endpoint42paths43invalid2transactions2AD2presets,4e-8backendparity','files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)},'status':'Prospective before any compiled material observations'},indent=2)+'\n')
commands={};tmp='/private/tmp/atlas-common-scalar-functions-v1'
for backend in ['native','wasm']:
 commands[backend+'_configure']=(['emcmake'] if backend=='wasm' else [])+['cmake','-S',str(b),'-B',tmp+'/material-'+backend+'-v1','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
 commands[backend+'_build']=['cmake','--build',tmp+'/material-'+backend+'-v1','--target','atlas_duncan_api','--parallel','1']
(p/'material-commands-v1.json').write_text(json.dumps(commands,indent=2)+'\n');print(len(files),'materialclosurefiles',len(same),'unchangedoriginalbindings')
