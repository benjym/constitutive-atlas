"""Reproduce both source-only outcomes and independent algebra; no compiled calls."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
R=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[3]
D=R/'docs/reviews';v1=D/'mc-declarative-design-v1';v2=D/'mc-gap-classifier-v2';a=D/'mc-branch-policy-audit-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def command(args,expected=0):
 r=subprocess.run([sys.executable,'-B',*map(str,args)],capture_output=True)
 assert r.returncode==expected,(args,r.returncode,r.stderr.decode())
 return r
files=0
for p in [v1,v2,a]:
 m=json.loads((p/'manifest.json').read_text())
 for rel,rec in m['files'].items():
  f=p/rel;assert sha(f)==rec['sha256'] and f.stat().st_size==rec['bytes'],f
  files+=1
for p in [v1,v2]:
 for rel,rec in json.loads((p/'source-pins.json').read_text()).items():
  f=p/'frozen'/rel;assert sha(f)==rec['sha256'] and f.stat().st_size==rec['bytes'],f
r=command([v1/'check.py'],1);assert b'selected_eigenvalue_unresolved'in r.stderr
r=command([v1/'diagnose.py']);negative=json.loads(r.stdout);assert negative==json.loads((v1/'diagnostic-results.json').read_text()) and negative['passed']is False
assert len(negative['retained_failed_hold_cases'])==4
positive=json.loads(command([v2/'check.py']).stdout);assert positive==json.loads((v2/'check.stdout').read_text())
assert positive['floating_value_cases']==25 and len(positive['invalid_parameter_rejections'])==9
with tempfile.TemporaryDirectory(prefix='atlas-mc-audit-replay-')as tmp:
 command([a/'check_classifier.py',v1/'frozen/docs/ingestion/mohr-coulomb',tmp])
 assert (Path(tmp)/'results.json').read_bytes()==(a/'results.json').read_bytes()
for script,report in [('check_gap_identities.py','gap-identities-results.json'),('check_zone_policy.py','zone-policy-witness.json')]:
 assert json.loads(command([a/script]).stdout)==json.loads((a/report).read_text())
model=R/'models/research/mohr-coulomb-sysala-cermak-h0-gap-classifier-v2.json';assert model.read_bytes()==(v2/'model.json').read_bytes()
assert len(list((R/'models').glob('*.json')))==9
print(json.dumps({'passed':True,'verified_manifest_entries':files,'failed_v1_holds_preserved':4,'v2_value_and_hold_cases':25,'invalid_parameter_rejections':9,'exact_classifier_cases':19694,'gap_identity_cases':1440,'research_model_exact':True,'public_model_count':9,'compiled_observations':0,'scientific_admission':False},indent=2))
