"""Read-only compatibility assertion review; capacity uses syntax-only C++ tests."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
R=Path('/Users/bmar5496/code/constitutive-atlas');C=Path('/private/tmp/atlas-lade-release-v1');O=Path(__file__).resolve().parent;A=Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/ci-compat-v3');H=C/A
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[];pins={}
def ck(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
def pin(p):pins[str(p)]=sha(p)
x=json.loads((H/'PRIOR_INPUTS.json').read_text());pin(H/'PRIOR_INPUTS.json');names=[n for n in x['files'] if n.startswith('tests/')]
ck('exact six test files',len(names)==6)
for n in names:
 old=C/'catalogue/source-snapshots'/x['files'][n]/n;new=C/n;ck('canonical prior exact '+n,sha(old)==x['files'][n]);pin(old);pin(new)
 for label,p in [('prior',old),('candidate',new)]:
  target=O/label/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 methods=lambda p:{(c.name,m.name) for c in ast.parse(p.read_text()).body if isinstance(c,ast.ClassDef) for m in c.body if isinstance(m,ast.FunctionDef)}
 ck('all test methods retained '+n,methods(old)==methods(new))
old=(O/'prior/tests/test_capacity.py').read_text();new=(C/'tests/test_capacity.py').read_text();ck('capacity only missing dependency supplied',new==old.replace("'trace_accuracy.hpp')","'trace_accuracy.hpp', 'scalar_functions.hpp')"))
a=json.loads((C/'tests/fixtures/current-thirteen-occ-v1.json').read_text());b=json.loads((C/'tests/fixtures/current-fourteen-duncan-v1.json').read_text());am={i['path']:i['sha256'] for i in a['models']};bm={i['path']:i['sha256'] for i in b['models']}
ck('strict14 adds only Duncan to exact13',len(am)==13 and len(bm)==14 and all(bm.get(k)==v for k,v in am.items()) and set(bm)-set(am)=={'models/duncan-chang-1970-endpoint-average.json'})
ck('current14 exhaustive exact live bytes',set(bm)=={p.relative_to(C).as_posix() for p in (C/'models').glob('*.json')} and all(sha(C/n)==h for n,h in bm.items()))
for n in ['tests/fixtures/current-thirteen-occ-v1.json','tests/fixtures/current-fourteen-duncan-v1.json','catalogue/manifest.json','catalogue/publications.json','catalogue/approved-models.json','docs/ingestion/norsand-1993/supplied-original-v2/source-receipt.json','catalogue/investigations/tensor-trace-operator-v1/assess.py','catalogue/investigations/tensor-trace-operator-v1/protocol.json','catalogue/investigations/tensor-trace-operator-v1/assessment.json','atlas/evidence.py']:pin(C/n)
# Historical assay artifacts and old13 fixture remain exact committed identities.
for n in ['tests/fixtures/current-thirteen-occ-v1.json','catalogue/investigations/tensor-trace-operator-v1/assess.py','catalogue/investigations/tensor-trace-operator-v1/protocol.json','catalogue/investigations/tensor-trace-operator-v1/assessment.json','.github/workflows/verify.yml','.github/workflows/macos.yml']:
 ck('immutable historical/workflow unchanged '+n,sha(C/n)==hashlib.sha256(subprocess.check_output(['git','-C',str(C),'show','HEAD:'+n])).hexdigest())
modules=['tests.test_capacity','tests.test_catalogue','tests.test_publications','tests.test_classic_publications','tests.test_historical_generation','tests.test_trace_operator_evidence']
run=subprocess.run([sys.executable,'-B','-m','unittest',*modules,'-v'],cwd=C,capture_output=True,text=True);(O/'unittest.stdout.log').write_text(run.stdout);(O/'unittest.stderr.log').write_text(run.stderr);ck('twenty targeted compatibility tests pass',run.returncode==0 and 'Ran 20 tests' in run.stderr)
for n in names:ck('posttest exact candidate '+n,sha(C/n)==pins[str(C/n)])
for n in ['PRIOR_INPUTS.json','focused-tests.log','focused-tests-v2.log']:
 (O/n).write_bytes((H/n).read_bytes());pin(H/n)
(O/'CHECK_RESULTS.json').write_text(json.dumps({'status':'passed','checks':checks,'pins':pins,'execution_scope':'Pure Python/source/database/temp package replay; capacity only two fsyntax-only compiler rejections, no native/Wasm artifact execution.'},indent=2)+'\n');print('PASS',len(checks))
