"""Source-only explicit-target dependency audit; never calls build helper main."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path('/Users/bmar5496/code/constitutive-atlas');C=Path('/private/tmp/atlas-lade-release-v1');O=Path(__file__).resolve().parent;H=O.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[];pins={}
def ck(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
def pin(p):pins[str(p)]=sha(p)
x=json.loads((H/'CI_TARGET_REPAIR-v2.json').read_text());prior=H/'build_ci_targets-prior-v1.py';new=H/'build_ci_targets-candidate-v2.py'
ck('exact prior/new manifest',sha(prior)==x['prior_sha256'] and sha(new)==x['sha256']==sha(C/x['path']))
ck('single target insertion only',new.read_text()==prior.read_text().replace("    'atlas_power_creep_solver',","    'atlas_scalar_probe', 'atlas_power_creep_solver',",1))
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
old=load('old_targets',prior);candidate=load('new_targets',new)
ck('existing engine order/list preserved',candidate.ENGINES==('atlas_scalar_probe',)+old.ENGINES)
ck('native tests exact',candidate.NATIVE_TESTS==old.NATIVE_TESTS)
for wasm in [False,True]:
 a=old.commands('build',wasm);b=candidate.commands('build',wasm)
 ck('one additional command '+str(wasm),b[1:]==a and b[0]==['cmake','--build','build','--target','atlas_scalar_probe','--parallel','1'])
 ck('one explicit serial target per command '+str(wasm),all(c[-2:]==['--parallel','1'] and c.count('--target')==1 for c in b))
for n in ['CMakeLists.txt','tests/scalar_functions_probe.cpp','tools/test_scalar_functions.py','tools/collect_scalar_functions.py','.github/workflows/verify.yml','.github/workflows/macos.yml','tests/test_ci_profiles.py']:
 data=subprocess.check_output(['git','-C',str(C),'show','c6dfd937c30ac998693dbe41391c7d793b3719dc:'+n]);ck('unchanged existing wiring '+n,hashlib.sha256(data).hexdigest()==sha(C/n));pin(C/n)
cm=(C/'CMakeLists.txt').read_text();ck('native CTest target-file linkage existing','add_library(atlas_scalar_probe SHARED tests/scalar_functions_probe.cpp)' in cm and 'add_test(NAME atlas_scalar_functions COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/test_scalar_functions.py" "$<TARGET_FILE:atlas_scalar_probe>")' in cm)
ck('Wasm explicit target existing','add_executable(atlas_scalar_probe EXCLUDE_FROM_ALL tests/scalar_functions_probe.cpp)' in cm)
run=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_ci_profiles','-v'],cwd=C,capture_output=True,text=True);(O/'unittest.stdout.log').write_text(run.stdout);(O/'unittest.stderr.log').write_text(run.stderr);ck('three pure CI profile tests pass',run.returncode==0 and 'Ran 3 tests' in run.stderr)
f=H/'ci-fixture-review-v1/review-receipt.json';ck('accepted sixteen fixtures exact reviewer identity',sha(f)=='db0f2c40fd75c64bba78a2547946406d66ec0626dcb6ab96b3dd3a676ff988b8');pin(f)
for n in ['CI_TARGET_REPAIR-v2.json','build_ci_targets-prior-v1.py','build_ci_targets-candidate-v2.py','initial-linux-job.log']:
 pin(H/n);(O/n).write_bytes((H/n).read_bytes())
for n,h in json.loads((H/'CI_FIXTURE_TRANSPORT-v1.json').read_text())['files'].items():ck('accepted dependency remains exact '+n,sha(C/n)==h)
ck('final helper exact',sha(C/x['path'])==x['sha256'])
(O/'CHECK_RESULTS.json').write_text(json.dumps({'status':'passed','checks':checks,'pins':pins},indent=2)+'\n');print('PASS',len(checks))
