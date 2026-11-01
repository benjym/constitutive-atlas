"""Freeze only the common engine closure and exact OCC candidate, before build."""
from pathlib import Path
import hashlib,json,shutil,subprocess
from atlas.compiler import generate
B=Path(__file__).resolve().parent
R=B.parents[3]
S=B/'source-snapshot'
assert not S.exists(), 'Preserve frozen snapshot; create a new study for changes'
for folder,pattern in [('cpp/include','**/*'),('atlas','*.py'),('schemas','*.json')]:
 for p in sorted((R/folder).glob(pattern)):
  if p.is_file():
   out=S/p.relative_to(R);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
out=S/'cpp/main.cpp';out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'cpp/main.cpp',out)
model=B.parent/'control-selection-v1/candidate-v03-v3.json'
shutil.copyfile(model,S/'candidate.json')
generate(S/'generated',[S/'candidate.json'])
(S/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(AtlasOCCFrozen LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(atlas_occ_solver EXCLUDE_FROM_ALL cpp/main.cpp)
target_include_directories(atlas_occ_solver PRIVATE cpp/include generated)
target_compile_options(atlas_occ_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
 target_compile_options(atlas_occ_solver PRIVATE -fexceptions)
 set_target_properties(atlas_occ_solver PROPERTIES OUTPUT_NAME occ SUFFIX ".js")
 target_link_options(atlas_occ_solver PRIVATE "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas" "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1" "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576" "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
''')
print('Frozen source closure:',len(list(S.rglob('*'))),'entries')
