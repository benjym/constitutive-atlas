"""Read-only source/profile checks. No builds, compiler or material calls."""
from pathlib import Path
import hashlib,json,difflib
R=Path(__file__).resolve().parents[3];O=Path('/private/tmp/atlas-bingham-delivery-v1');G=Path('/private/tmp/atlas-schedule-predictor-v1');OUT=Path(__file__).resolve().parent
P=R/'docs/investigations/physical-time-v2-profile-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'FREEZE.json';assert sha(f)=='b308f1e965c9c28affeae89a6a47fb3be944313dc5f3593e51b351d40cddcca6'
b=json.loads(f.read_text());assert len(b['files'])==183
for n,h in b['files'].items():assert sha(R/n)==h,n
for n,h in json.loads((P/'TOOLS.json').read_text())['binary_files'].items():assert sha(Path(n))==h,n
assert sha(R/'runtimes/physical-time-v2/include/atlas/schedule.hpp')=='fd05b08d422468802fb788386a2f19463dec65ca66e3cf2153f837a5db0d2702'
assert (R/'runtimes/physical-time-v2/include/atlas/schedule.hpp').read_bytes()==(G/'cpp/include/atlas/schedule.hpp').read_bytes()
assert sha(R/'cpp/include/atlas/schedule.hpp')=='5c90e6cede9f24f124286cf10e2254a47a991e5d62f9bc7b3899ed62e6deb7e9'
# Full fileset comparison in guard-owned trees, excluding runtime caches.
def files(root,folder):return {str(p.relative_to(root)):sha(p) for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
for folder in ['atlas','cpp','schemas']:assert files(R,folder)==files(O,folder),folder
for n in ['tests/test_schedule_predictor.cpp','tests/test_time.cpp','tests/test_time.py','tests/test_schedule.py']:
 assert (R/n).read_bytes()==(G/n).read_bytes(),n
assert files(R,'tests/fixtures/time')==files(G,'tests/fixtures/time')
for n in ['cpp/scalar-functions/'+p.name for p in (R/'cpp/scalar-functions').iterdir() if p.is_file()]:assert n in b['files'],n
for n in files(R,'tests/fixtures/time'):assert n in b['files'],n
# Exact intended CMake source transformations, independent of diff prose.
root=(O/'CMakeLists.txt').read_text()
root=root.replace('target_include_directories(atlas_time_solver PRIVATE cpp/include','target_include_directories(atlas_time_solver PRIVATE runtimes/physical-time-v2/include cpp/include')
root=root.replace('target_include_directories(atlas_time_tests PRIVATE cpp/include','target_include_directories(atlas_time_tests PRIVATE runtimes/physical-time-v2/include cpp/include')
marker='  add_test(NAME atlas_time COMMAND atlas_time_tests)\n'
root=root.replace(marker,marker+'  add_executable(atlas_schedule_predictor_tests tests/test_schedule_predictor.cpp)\n  add_dependencies(atlas_schedule_predictor_tests atlas_time_models)\n  target_include_directories(atlas_schedule_predictor_tests PRIVATE runtimes/physical-time-v2/include cpp/include "${CMAKE_BINARY_DIR}/time-generated")\n  add_test(NAME atlas_schedule_predictor COMMAND atlas_schedule_predictor_tests)\n')
assert root==(R/'CMakeLists.txt').read_text()
cm=(O/'cmake/bingham/CMakeLists.txt').read_text().replace('PRIVATE "${ATLAS_ROOT}/cpp/include"','PRIVATE "${ATLAS_ROOT}/runtimes/physical-time-v2/include" "${ATLAS_ROOT}/cpp/include"')
assert cm==(R/'cmake/bingham/CMakeLists.txt').read_text()
rec=P/'run_operation.py';assert sha(rec)=='a60df28af114e127ec1c17914959bf58deed8a62bdcaee1e9b516206b6ae153f'
assert rec.read_text()==(G/'docs/investigations/schedule-predictor-v1/run_operation.py').read_text().replace('FREEZE-v3.json','FREEZE.json')
# Static include search for the actual schedule consumers; no preprocessor call.
incs=[R/'runtimes/physical-time-v2/include',R/'cpp/include']
resolved=next(p/'atlas/schedule.hpp' for p in incs if (p/'atlas/schedule.hpp').is_file());assert resolved==R/'runtimes/physical-time-v2/include/atlas/schedule.hpp'
# Current packaging closure differs in exactly the already reviewed unused unit module.
release=Path('/private/tmp/atlas-bingham-release-v2/docs/ingestion/bingham-comsol63/current-engine-equivalence-v1')
pack=json.loads((release/'maxwell-current-source.json').read_text())['files'];delta=[n for n,h in pack.items() if not (R/n).is_file() or sha(R/n)!=h]
assert delta==['atlas/measurement_units.py'],delta
ns=json.loads((release/'qualified-packaging-v1/norsand-qualification.json').read_text())['binding']['sources'];assert len(pack)==149 and len(ns)==121
nsdelta=[n for n,h in ns.items() if not (R/n).is_file() or sha(R/n)!=h];assert nsdelta==['atlas/measurement_units.py'],nsdelta
results={'decision':'source/prospective native and bounded Wasm build plan accepted','freeze_sha256':sha(f),'freeze_pins':183,'tool_pins':5,'versioned_header_sha256':sha(resolved),'legacy_header_sha256':sha(R/'cpp/include/atlas/schedule.hpp'),'guard_trees_fileset_and_bytes_exact_old':['atlas','cpp','schemas'],'current_packaging_closure_difference':delta,'unchanged_native_tests':4,'unchanged_time_fixture_count':len(files(R,'tests/fixtures/time')),'actual_dependency_proof':'mandatory before execution; not observed here','compiled_calls':0,'material_calls':0}
(OUT/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
