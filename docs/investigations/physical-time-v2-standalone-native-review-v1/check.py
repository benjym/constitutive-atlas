"""Saved actual native and source-equivalence checks; no material/build calls."""
from pathlib import Path
import json,hashlib,datetime,re
R=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;P=OUT.parent/'physical-time-v2-standalone-v1';A=P/'actual-native-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
summary=A/'SUMMARY.json';assert sha(summary)=='73603c50834cc6ee1145adc01bf5efa22fe0462ce1cf556d3ef7c11f5b4ca195';s=json.loads(summary.read_text());assert s['passed']
f=P/'FREEZE.json';assert sha(f)=='034860d4a4bb74de55adcc576e231388c82f72a820f2ed9a345c69dc80d35df6'
for n,h in json.loads(f.read_text())['files'].items():assert sha(R/n)==h,n
for n,h in json.loads((P/'TOOLS.json').read_text())['binary_files'].items():assert sha(Path(n))==h,n
prev=None
for name,v in s['operations'].items():
 p=A/(name+'.json');b=json.loads(p.read_text());assert sha(p)==v['receipt_sha256'];assert sha(A/(name+'.log'))==v['log_sha256']==b['log_sha256'];assert b['returncode']==0 and b['preverified'] and b['postverified'];assert b['source_freeze_sha256']==sha(f) and b['tools_sha256']==sha(P/'TOOLS.json') and b['recorder_sha256']==sha(P/'run_operation.py')
 start=datetime.datetime.fromisoformat(b['start']);end=datetime.datetime.fromisoformat(b['end']);assert start<end and (prev is None or start>prev);prev=end
 if name.startswith('build-'):assert b['argv'][-2:]==['--parallel','1'] and b['argv'].count('--target')==1
first=datetime.datetime.fromisoformat(json.loads((A/'test-predictor.json').read_text())['start']).timestamp();binaries={}
for name,v in s['build_artifact_inventories'].items():
 p=A/name;assert sha(p)==v['sha256'] and p.stat().st_mtime<first;b=json.loads(p.read_text());assert len(b['files'])==53
 for n,h in b['files'].items():assert sha(R/n)==h,n
 assert 'build-time-v2/libatlas_scalar_functions.a' in b['files']
 assert sum(n.endswith('.c.o') for n in b['files'])==12 and sum(n.endswith('.c.o.d') for n in b['files'])==12
 for tail in ['/atlas_scalar_functions.dir/flags.make','/CMakeCCompiler.cmake','/CMakeCXXCompiler.cmake','/generated/models.hpp','/generated/models.json']:assert any(n.endswith(tail) for n in b['files']),tail
 target=name.replace('-build-artifacts.json','');binaries[target]=b['files']['build-time-v2/'+target]
 deps=[R/n for n in b['files'] if n.endswith('.cpp.o.d')];assert len(deps)==1
 hs={str(Path(w).resolve()) for p in deps for w in p.read_text().replace('\\\n',' ').split() if w.endswith('/atlas/schedule.hpp')}
 assert hs==({str(R/'runtimes/physical-time-v2/include/atlas/schedule.hpp')} if target!='atlas_time_tests' else set())
 assert sorted(hs)==b['actual_schedule_headers'];assert b['versioned_schedule_sha256']=='fd05b08d422468802fb788386a2f19463dec65ca66e3cf2153f837a5db0d2702'
 flags=next((R/n).read_text() for n in b['files'] if n.endswith(target+'.dir/flags.make'));assert flags.index('runtimes/physical-time-v2/include')<flags.index('cpp/include') and '-ffp-contract=off' in flags
assert 'Ran 18 tests' in (A/'test-python.log').read_text() and (A/'test-python.log').read_text().strip().endswith('OK') and 'skipped' not in (A/'test-python.log').read_text().lower()
assert json.loads((A/'test-python.json').read_text())['environment']['ATLAS_TIME_SOLVER']==str(R/'build-time-v2/atlas_time_solver')
for n,needle in [('test-predictor.log','Prospective generic predictor boundary, fallback, mixed-rate and clock checks passed'),('test-time.log','Physical-time analytical solutions, stage histories, refinement, partitioning and rollback passed')]:assert (A/n).read_text().strip()==needle
for n in ['tests/test_time.cpp','tests/test_schedule_predictor.cpp']:assert 'throw std::runtime_error' in (R/n).read_text() and not re.search(r'\bassert\s*\(',(R/n).read_text())
for n in ['models.hpp','models.json']:assert (R/'build-time-v2/generated'/n).read_bytes()==(R/'build-profile-tests/time-generated'/n).read_bytes()
release=Path('/private/tmp/atlas-bingham-release-v2');E=release/'docs/ingestion/bingham-comsol63/current-generator-equivalence-v1';e=json.loads((E/'RESULT.json').read_text());assert e['returncode']==0 and e['source_unchanged'] and sha(E/'source-before.json')==e['source_before_sha256'];src=json.loads((E/'source-before.json').read_text());src=src.get('files',src);assert len(src)==68
for n,h in src.items():assert sha(release/n)==h,n
assert sha(E/'compiler.log')==e['compiler_log_sha256']
for n,v in e['comparison'].items():assert sha(E/'generated'/n)==v['generated_sha256']==v['tested_engine_generated_sha256']==sha(R/'build-bingham-native/generated'/n)
result={'decision':'accepted actual standalone native phase','operations':7,'artifact_inventories':3,'artifact_entries':159,'all12scalarobjects_and_deps_each':True,'pre_observation_inventory_chronology':'filesystem plus coordinator declaration; no invented timestamp','source_pins':185,'tool_pins':5,'python_tests':18,'skips':0,'binary_sha256':binaries,'current_release_generator_compatibility':'exact header/metadata only; not runtime rebuild','current_generator_sources':68,'compiled_calls_by_reviewer':0,'material_calls_by_reviewer':0}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
