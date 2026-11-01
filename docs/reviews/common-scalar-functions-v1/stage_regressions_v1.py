from pathlib import Path
import json,hashlib,shutil
r=Path.cwd();p=r/'docs/reviews/common-scalar-functions-v1';dst=p/'generic-regression-v1';assert not dst.exists();dst.mkdir();source=Path('/private/tmp/atlas-common-scalar-functions-v1/scalar-probe-source-v1');shutil.copytree(source/'cpp',dst/'runtime/cpp');(dst/'runtime/cmake').mkdir(parents=True);shutil.copyfile(p/'proposed-v2/cmake/AtlasScalarFunctions.cmake',dst/'runtime/cmake/AtlasScalarFunctions.cmake');unchanged={}
def copy(f,d):
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);unchanged[str(d.relative_to(r))]={'original':str(f.relative_to(r)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
old=r/'docs/reviews/bounded-partition-retry-v1/qualification-v2'
for name in ['regression.cpp','partition.cpp','checks.inc','corpus.inc','history.inc','requests.hpp','requests-v5.json','assess-regression.py','assess_partition.py','analytical_reference.py','POLICY.md']:
 copy(old/name,dst/'partition'/name)
for f in (old/'generated').iterdir():
 if f.is_file():copy(f,dst/'partition/generated'/f.name)
old=r/'docs/reviews/spectral-multiplicity-v1'
for name in ['driver.cpp','requests.txt','references.json','assess.py','POLICY.md','CONTRACT.md','COMPOSITION_V4.md','HISTORY_EXPECTATION_V3.md']:
 copy(old/name,dst/'spectral'/name)
for f in (old/'generated').iterdir():
 if f.is_file():copy(f,dst/'spectral/generated'/f.name)
cm='''cmake_minimum_required(VERSION 3.20)
project(AtlasCommonScalarRegressions LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include("${CMAKE_CURRENT_SOURCE_DIR}/runtime/cmake/AtlasScalarFunctions.cmake")
add_executable(atlas_partition_regression partition/regression.cpp)
add_executable(atlas_partition_analytical partition/partition.cpp)
add_executable(atlas_spectral_multiplicity spectral/driver.cpp)
foreach(target atlas_partition_regression atlas_partition_analytical atlas_spectral_multiplicity)
 target_include_directories(${target} PRIVATE runtime/cpp/include)
 target_compile_options(${target} PRIVATE -Wall -Wextra -Wno-unused-variable -Wno-misleading-indentation -fno-fast-math)
 if(EMSCRIPTEN)
  target_compile_options(${target} PRIVATE -fexceptions)
  target_link_options(${target} PRIVATE -fexceptions "-sENVIRONMENT=node" "-sEXIT_RUNTIME=1" "-sSTACK_SIZE=1048576" "-sALLOW_MEMORY_GROWTH=1")
  set_target_properties(${target} PROPERTIES SUFFIX ".js")
 endif()
endforeach()
target_include_directories(atlas_partition_regression PRIVATE partition/generated)
target_include_directories(atlas_partition_analytical PRIVATE partition/generated)
target_include_directories(atlas_spectral_multiplicity PRIVATE spectral/generated)
''';(dst/'CMakeLists.txt').write_text(cm);(dst/'unchanged-bindings.json').write_text(json.dumps(unchanged,indent=2)+'\n')
fs=[f for f in dst.rglob('*') if f.is_file()];(p/'generic-regression-freeze-v1.json').write_text(json.dumps({'identity':'common-scalar-generic-regressions-v1','source':str(dst),'status':'Prospective sameoriginaldrivers/references/requests/limits; changedruntime and CMake only; no compiledobservations','files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(fs)}},indent=2)+'\n')
cs={};tmp='/private/tmp/atlas-common-scalar-functions-v1'
for backend in ['native','wasm']:
 cs[backend+'_configure']=(['emcmake'] if backend=='wasm' else [])+['cmake','-S',str(dst),'-B',tmp+'/generic-'+backend+'-v1','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
 for t in ['atlas_partition_analytical','atlas_partition_regression','atlas_spectral_multiplicity']:cs[backend+'_build_'+t]=['cmake','--build',tmp+'/generic-'+backend+'-v1','--target',t,'--parallel','1']
(p/'generic-regression-commands-v1.json').write_text(json.dumps(cs,indent=2)+'\n');print(len(fs),'generic regression inputs,',len(unchanged),'unchanged original witnesses')
