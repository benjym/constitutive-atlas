"""Read-only fixture transport verification and saved-only unit replay."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
R=Path('/Users/bmar5496/code/constitutive-atlas');C=Path('/private/tmp/atlas-lade-release-v1');O=Path(__file__).resolve().parent;H=O.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[];pins={}
def ck(n,v):
 checks.append({'name':n,'passed':bool(v)});assert v,n
def pin(p):pins[str(p)]=sha(p)
x=json.loads((H/'CI_FIXTURE_TRANSPORT-v1.json').read_text());pin(H/'CI_FIXTURE_TRANSPORT-v1.json');ck('exact sixteen transported members',len(x['files'])==16)
total=0;rows={}
for n,h in x['files'].items():
 p=C/n;ck('candidate/donor exact '+n,sha(p)==h==sha(R/n));pin(p);pin(R/n);total+=p.stat().st_size
 if p.suffix=='.py':
  tree=ast.parse(p.read_text());imports=[]
  for a in ast.walk(tree):
   if isinstance(a,ast.Import):imports.extend(z.name for z in a.names)
   if isinstance(a,ast.ImportFrom):imports.append(a.module)
  ck('pure standard-library/owned imports '+n,set(imports)<={'copy','json','sys','pathlib','decimal','math','fractions','assess'})
 if p.suffix=='.jsonl':
  data=[json.loads(l,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s))) for l in p.read_text().splitlines()];rows[n]=len(data)
 if p.suffix=='.json':json.loads(p.read_text(),parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
modules=['tests.test_bounded_partition_evidence','tests.test_newton_endpoint_evidence','tests.test_spectral_multiplicity_evidence']
for module in modules:
 n=module.replace('.','/')+'.py';original=subprocess.check_output(['git','-C',str(C),'show',x['base']+':'+n]);ck('existing unit exact base '+n,hashlib.sha256(original).hexdigest()==sha(C/n));pin(C/n)
 # Every literal saved-file dependency has been manually inspected against these exact bytes.
 (O/Path(n).name).write_bytes((C/n).read_bytes())
run=subprocess.run([sys.executable,'-B','-m','unittest',*modules,'-v'],cwd=C,capture_output=True,text=True)
(O/'unittest.stdout.log').write_text(run.stdout);(O/'unittest.stderr.log').write_text(run.stderr);ck('twelve saved-only unit tests pass',run.returncode==0 and 'Ran 12 tests' in run.stderr)
for n,h in x['files'].items():ck('final exact '+n,sha(C/n)==h)
(O/'CI_FIXTURE_TRANSPORT-v1.json').write_bytes((H/'CI_FIXTURE_TRANSPORT-v1.json').read_bytes());(O/'missing-ci-fixtures-v1.log').write_bytes((H/'missing-ci-fixtures-v1.log').read_bytes());pin(H/'missing-ci-fixtures-v1.log')
result={'status':'passed','base':x['base'],'checks':checks,'bytes':total,'raw_jsonl_rows':rows,'pins':pins,'scope':'No compiled calls or new observations; exact existing pure assessors/references/saved backend data only.'}
(O/'CHECK_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','checks':len(checks),'bytes':total,'raw_jsonl_rows':rows}))
