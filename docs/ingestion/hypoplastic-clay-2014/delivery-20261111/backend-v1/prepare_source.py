"""Small exact common-runtime source closure, not a repository/archive copy."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate

source=ROOT/'.local/clay2014-full13-20261111/runtime-source'
assert not source.exists()
source.mkdir(parents=True)
inputs=[]
for parent in ['cpp/include','cpp/scalar-functions','atlas','schemas']:
    for original in sorted((ROOT/parent).rglob('*')):
        if not original.is_file() or '__pycache__' in original.parts:
            continue
        if parent=='atlas' and original.suffix!='.py':continue
        target=source/original.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
        inputs.append({'path':str(original.relative_to(ROOT)),'bytes':original.stat().st_size,
                       'sha256':hashlib.sha256(original.read_bytes()).hexdigest()})
for name in ['cpp/main.cpp','cmake/AtlasScalarFunctions.cmake']:
    target=source/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    inputs.append({'path':name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
candidate=HERE.parent/'candidate-v3.json'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='e2ea575498d4dbe909b16db70ee40a7d3e78e84590719d5a8fa21cdf9175c9c3'
generate(source/'generated',[candidate])
shutil.copy2(candidate,source/'candidate.json')
(source/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(AtlasCandidate LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/AtlasScalarFunctions.cmake")
add_executable(atlas_solver cpp/main.cpp)
target_include_directories(atlas_solver PRIVATE cpp/include generated)
target_compile_options(atlas_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_solver PRIVATE -fexceptions)
  set_target_properties(atlas_solver PROPERTIES OUTPUT_NAME "atlas" SUFFIX ".js")
  target_link_options(atlas_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions"
    "-sFILESYSTEM=0" "--no-entry")
endif()
''')
files={str(f.relative_to(source)):hashlib.sha256(f.read_bytes()).hexdigest()
       for f in sorted(source.rglob('*')) if f.is_file()}
receipt={'identity':'clay2014-common-runtime-source-v1','source_root':str(source),
         'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
         'original_inputs':inputs,'source_members':files,
         'source_bytes':sum(f.stat().st_size for f in source.rglob('*') if f.is_file()),
         'wrapper':'One common cpp/main.cpp target, existing scalar CMake/link options; no material kernel.',
         'native_wasm_builds':0,'material_calls':0,'archives':0}
out=HERE/'source-receipt.json';assert not out.exists();out.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'members':len(files),'source_bytes':receipt['source_bytes'],'receipt_sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
