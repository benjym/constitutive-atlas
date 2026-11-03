from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;D=R/'.local/s-clay1-delivery-v3';S=D/'source'
assert not S.exists()
S.mkdir()
for directory in ['cpp','cmake','atlas','schemas']:
 shutil.copytree(R/directory,S/directory,ignore=shutil.ignore_patterns('__pycache__'))
(S/'models').mkdir()
for p in [O/'candidate/s-clay1.json',R/'models/linear-elastic.json',R/'models/modified-cam-clay.json']:
 shutil.copy2(p,S/'models'/p.name)
(S/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.20)
project(SCLAY1Qualification LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/AtlasScalarFunctions.cmake")
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/models/*.json")
add_custom_command(OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json"
 COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/generated"
 DEPENDS ${MODEL_FILES} WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}")
add_custom_target(atlas_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json")
add_executable(atlas_solver cpp/main.cpp)
add_dependencies(atlas_solver atlas_models)
target_include_directories(atlas_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/generated")
target_compile_options(atlas_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
 target_compile_options(atlas_solver PRIVATE -fexceptions)
 set_target_properties(atlas_solver PROPERTIES OUTPUT_NAME "atlas" SUFFIX ".js")
 target_link_options(atlas_solver PRIVATE "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas" "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1" "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576" "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
''')
# Pin isolated inputs rather than mutable shared trees. No production change.
files={str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(S.rglob('*')) if p.is_file()}
(O/'build-source-manifest.json').write_text(json.dumps({'root':str(S.relative_to(R)),'files':files,'normal_engine':True,'custom_CMake_scope':'isolated standard atlas_solver target and three definitions only; common compiler/scalar sources/main unchanged'},indent=2)+'\n')
# claim is separate from launch; retained fresh inventory has no active matches.
p=R/'IMPLEMENTATION_PLAN.md';b=p.read_bytes();h=hashlib.sha256(b).hexdigest()
r=subprocess.run(['rg','-l','-F',h,'catalogue','docs','tools','schemas','tests','-g','*.json','-g','!**/source-snapshots/**','-g','!docs/ingestion/s-clay1/supplied-original-v3/*claim*.json'],cwd=R,capture_output=True,text=True);assert r.returncode==1,r.stdout
q=R/'catalogue/source-snapshots'/h/'IMPLEMENTATION_PLAN.md';q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
s='''\n- [-] **EXEC-s-clay1-native-v3** — Coordinator /root ACTIVE2026-11-03 after fresh complete processinventory no compiler/model/package/browser match; most recent tracked serial consumers terminalRELEASED. Isolated .local/s-clay1-delivery-v3/source exact fullinputmanifest; frozen numericalpolicyv1 and independent55algebra/compliance reference accepted. Own configure, one atlas_solver native target --parallel1 then frozen bounded native material/reference/invalid/rollback/covariance/public/default/regression requests. Stop and retain first failure, explicitrelease before Wasm or otherowner. No sharedsource/schema/kernel/web/remote mutation. Claim before launch.\n'''
assert p.read_bytes()==b;p.write_bytes(b+s.encode())
(O/'native-claim.json').write_text(json.dumps({'board_before':h,'board_archive':str(q.relative_to(R)),'source_manifest_sha256':hashlib.sha256((O/'build-source-manifest.json').read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((O/'policy.json').read_bytes()).hexdigest(),'process_inventory_sha256':hashlib.sha256((D/'processes-before.txt').read_bytes()).hexdigest(),'state':'claimed-before-launch','target':'atlas_solver','parallel':1},indent=2)+'\n')
print('isolatedsource',len(files),'files; nativeclaim recorded')
