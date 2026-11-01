from pathlib import Path
import ast,hashlib,json,subprocess
R=Path('/Users/bmar5496/code/constitutive-atlas');C=Path('/private/tmp/atlas-lade-release-v1');O=Path(__file__).resolve().parent;H=O.parents[1];BASE='515b39c98176af5578bb29ee29d9e1a9e0ed834f'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[];pins={}
def check(n,v):
 checks.append({'name':n,'passed':bool(v)});assert v,n
def pin(p):pins[str(p)]=sha(p);return p.read_text()
def git(n):return subprocess.check_output(['git','-C',str(C),'show',BASE+':'+n]).decode()
norm=lambda s:s.replace('explicit-gis20-occ-restart-v4','explicit-gis20-occ-restart-duncan-v5').replace('explicit-gis20-occ-v3','explicit-gis20-occ-restart-duncan-v5').replace(' --fixture-contract catalogue/native-fixture-contracts-thirteen-occ-v1.json','')
x=json.loads(pin(H/'CI_GATE_FOLLOWUP-v3.json'))
for n,h in x['files'].items():check('candidate hash '+n,sha(C/n)==h);pin(C/n)
w=pin(H/'verify-candidate-v3.yml');m=pin(H/'macos-candidate-v1.yml');t=pin(H/'test_ci_profiles-v3.py');b=git('.github/workflows/verify.yml');bm=git('.github/workflows/macos.yml');bt=git('tests/test_ci_profiles.py')
for n,s in [('remote-verify.yml',b),('remote-macos.yml',bm),('remote-test_ci_profiles.py',bt),('candidate-verify.yml',w),('candidate-macos.yml',m),('candidate-test_ci_profiles.py',t)]: (O/n).write_text(s)
check('snapshots match release',w==(C/'.github/workflows/verify.yml').read_text() and m==(C/'.github/workflows/macos.yml').read_text() and t==(C/'tests/test_ci_profiles.py').read_text())
check('test exactly two literal substitutions',t==bt.replace('explicit-gis20-occ-restart-v4','explicit-gis20-occ-restart-duncan-v5').replace('explicit-gis20-occ-v3','explicit-gis20-occ-restart-duncan-v5'))
check('manual exact declared changes',m==norm(bm).replace('Qualified current13 native fixtures','Qualified current14 native fixtures'))
start='      - name: Native checks';end='      - name: Linux portable'
check('remote split CTest blocks exact apart accepted policy and CLI',w[w.index(start):w.index(end)]==norm(b[b.index(start):b.index(end)]))
check('accepted v2 Wasm and deployment blocks unchanged',w.split('\n  wasm:')[1]==(H/'verify-candidate-v2.yml').read_text().split('\n  wasm:')[1])
check('deploy exact remote',w.split('\n  deploy:')[1]==b.split('\n  deploy:')[1])
check('obsolete CLI absent','--fixture-contract' not in w+m)
s=pin(C/'tools/check_native_fixture_contracts.py');ast.parse(s)
check('checker CLI actual build/output',"add_argument('--build'" in s and "add_argument('--output'" in s and "add_argument('--fixture-contract'" not in s)
check('checker unchanged accepted shared source',sha(C/'tools/check_native_fixture_contracts.py')==sha(R/'tools/check_native_fixture_contracts.py'))
for n in ['tools/build_ci_targets.py','tools/run_ci_tests.py','tests/test_native_fixture_contracts.py','tools/ci_exact_replays.json','catalogue/laboratory-package-policy.json']:pin(C/n)
run=subprocess.run(['python3','-B','-m','unittest','tests.test_ci_profiles','tests.test_native_fixture_contracts','-v'],cwd=C,capture_output=True,text=True)
(O/'unittest.stdout.log').write_text(run.stdout);(O/'unittest.stderr.log').write_text(run.stderr);check('six pure tests pass',run.returncode==0 and 'Ran 6 tests' in run.stderr)
for n in ['CI_GATE_FOLLOWUP-v3.json','fixture-v2-failure.log','MANUAL_WORKFLOW-v1.json']:(O/n).write_bytes((H/n).read_bytes());pin(H/n)
for n,h in x['files'].items():check('final candidate hash '+n,sha(C/n)==h)
(O/'CHECK_RESULTS.json').write_text(json.dumps({'status':'passed','base':BASE,'checks':checks,'pins':pins},indent=2)+'\n');print('PASS',len(checks))
