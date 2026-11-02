"""Read/hash source only, with no build or material calls."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;P=OUT.parent/'physical-time-v2-standalone-v1';OLD=OUT.parent/'physical-time-v2-profile-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'FREEZE.json';assert sha(f)=='034860d4a4bb74de55adcc576e231388c82f72a820f2ed9a345c69dc80d35df6'
b=json.loads(f.read_text());old=json.loads((OLD/'FREEZE.json').read_text());assert len(b['files'])==185
for n,h in b['files'].items():assert sha(R/n)==h,n
assert all(b['files'][n]==h for n,h in old['files'].items())
assert set(b['files'])-set(old['files'])=={'cmake/physical-time-v2/CMakeLists.txt','docs/investigations/physical-time-v2-standalone-v1/PLAN.md'}
for n in ['TOOLS.json','run_operation.py']:assert (P/n).read_bytes()==(OLD/n).read_bytes()
for n,h in json.loads((P/'TOOLS.json').read_text())['binary_files'].items():assert sha(Path(n))==h,n
assert sha(R/'cmake/physical-time-v2/CMakeLists.txt')=='4a035250ac87628b8ba64a9044237888e808c5565de2f922e1978176c07439ca'
assert sha(P/'pin_artifacts.py')=='ee3746986d32571d4b67e9ea36b17bccdb4ddf369388721373acb43d76c466df'
cm=(R/'cmake/physical-time-v2/CMakeLists.txt').read_text();assert cm.index('runtimes/physical-time-v2/include')<cm.index('cpp/include')
for x in ['atlas_time_v2_target(atlas_time_solver cpp/main.cpp)','atlas_time_v2_target(atlas_schedule_predictor_tests tests/test_schedule_predictor.cpp)','atlas_time_v2_target(atlas_time_tests tests/test_time.cpp)','include("${ATLAS_ROOT}/cmake/AtlasScalarFunctions.cmake")','"${ATLAS_ROOT}/tests/fixtures/time"']:assert x in cm,x
result={'source_decision':'accepted prospectively native only','freeze_sha256':sha(f),'pins':185,'prior183pins_exact':True,'tool_pins':5,'compiled_calls':0,'material_calls':0,'helper_completeness_requires_actual_inventory_review':True}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
