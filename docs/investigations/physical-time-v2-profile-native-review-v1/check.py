"""Saved actual evidence/hash/dependency checks; no executable invocations."""
from pathlib import Path
import hashlib,json,datetime,re
R=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;P=OUT.parent/'physical-time-v2-profile-v1';A=P/'actual-native-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'NATIVE-RESULTS-v1.json';assert sha(f)=='a052de9811f66d0e8255f01c2787832600d8c53d7821af3f4fb296f2bc83af02'
summary=json.loads(f.read_text())
for n,h in summary['files'].items():assert sha(R/n)==h,n
freeze=P/'FREEZE.json';assert sha(freeze)=='b308f1e965c9c28affeae89a6a47fb3be944313dc5f3593e51b351d40cddcca6'
for n,h in json.loads(freeze.read_text())['files'].items():assert sha(R/n)==h,n
for n,h in json.loads((P/'TOOLS.json').read_text())['binary_files'].items():assert sha(Path(n))==h,n
names=['configure','build-boundary','boundary-tests','build-time-tests','time-tests','build-time-solver','existing-regressions'];prev=None
for n in names:
 p=A/(n+'.json');b=json.loads(p.read_text());assert b['returncode']==0 and b['preverified'] and b['postverified'];assert b['source_freeze_sha256']==sha(freeze);assert b['recorder_sha256']==sha(P/'run_operation.py');assert b['tools_sha256']==sha(P/'TOOLS.json');assert b['log_sha256']==sha(A/(n+'.log'));assert b['cwd']==str(R)
 start=datetime.datetime.fromisoformat(b['start']);end=datetime.datetime.fromisoformat(b['end']);assert start<end and (prev is None or start>prev);prev=end
 if n.startswith('build-'):assert b['argv']==['cmake','--build','build-profile-tests','--target',{'build-boundary':'atlas_schedule_predictor_tests','build-time-tests':'atlas_time_tests','build-time-solver':'atlas_time_solver'}[n],'--parallel','1']
assert json.loads((A/'existing-regressions.json').read_text())['environment']['ATLAS_TIME_SOLVER']==str(R/'build-profile-tests/atlas_time_solver')
expected=str(R/'runtimes/physical-time-v2/include/atlas/schedule.hpp');common=str(R/'cpp/include/atlas/schedule.hpp');total=0;bins={}
for prefix,target,execution,build in [('boundary','atlas_schedule_predictor_tests','boundary-tests','build-boundary'),('time-tests','atlas_time_tests','time-tests','build-time-tests'),('time-solver','atlas_time_solver','existing-regressions','build-time-solver')]:
 artifact=A/(prefix+'-artifacts.json');b=json.loads(artifact.read_text());assert len(b['files'])==15
 for n,h in b['files'].items():assert sha(R/n)==h,n
 total+=len(b['files']);bins[target]=b['files']['build-profile-tests/'+target]
 # Independent exact actual header dependency parsing (including continuations).
 deps=[R/n for n in b['files'] if n.endswith('.o.d')];assert len(deps)==1
 headers={str(Path(w).resolve()) for d in deps for w in d.read_text().replace('\\\n',' ').split() if w.endswith('/atlas/schedule.hpp')}
 assert headers==({expected} if prefix!='time-tests' else set());assert common not in headers
 assert b['actual_schedule_headers']==sorted(headers);assert b['versioned_schedule_sha256']==sha(Path(expected))
 flags=next((R/n).read_text() for n in b['files'] if n.endswith('/flags.make'));assert flags.index('runtimes/physical-time-v2/include')<flags.index('cpp/include');assert '-O3 -DNDEBUG -std=gnu++20 -ffp-contract=off' in flags
 # Filesystem chronology corroborates coordinator's pre-observation declaration; not a signed timestamp.
 end=datetime.datetime.fromisoformat(json.loads((A/(build+'.json')).read_text())['end']).timestamp();start=datetime.datetime.fromisoformat(json.loads((A/(execution+'.json')).read_text())['start']).timestamp();assert end<artifact.stat().st_mtime<start
assert (A/'boundary-tests.log').read_text().strip()=='Prospective generic predictor boundary, fallback, mixed-rate and clock checks passed'
assert (A/'time-tests.log').read_text().strip()=='Physical-time analytical solutions, stage histories, refinement, partitioning and rollback passed'
log=(A/'existing-regressions.log').read_text();assert 'Ran 18 tests' in log and log.strip().endswith('OK') and 'skipped' not in log.lower()
for n in ['tests/test_schedule_predictor.cpp','tests/test_time.cpp']:
 t=(R/n).read_text();assert 'throw std::runtime_error' in t and not re.search(r'\bassert\s*\(',t)
# Generated test model/header must match retained original generic implementation study.
G=Path('/private/tmp/atlas-schedule-predictor-v1/build-predictor/time-generated')
for n in ['models.hpp','models.json']:assert (R/'build-profile-tests/time-generated'/n).read_bytes()==(G/n).read_bytes(),n
result={'decision':'accepted actual native generic profile regressions','operations':7,'summary_pins':len(summary['files']),'source_pins':183,'tool_pins':5,'artifact_entries':total,'python_tests':18,'python_skips':0,'schedule_dependency_required_and_proved':['atlas_schedule_predictor_tests','atlas_time_solver'],'time_unit_test_schedule_dependency':False,'runtime_checks_not_removed_by_NDEBUG':True,'binary_sha256':bins,'compiled_calls_by_reviewer':0,'material_calls_by_reviewer':0}
(OUT/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
