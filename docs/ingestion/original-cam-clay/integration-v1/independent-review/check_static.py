"""Independent read-only integration checks; no compiled artifacts loaded."""
import hashlib,json,math,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[5]
base=root/'docs/ingestion/original-cam-clay/integration-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((base/'before/catalogue/laboratory-package-policy.json').read_text())
new=json.loads((root/'catalogue/laboratory-package-policy.json').read_text())
assert len(old['models'])==12 and len(new['models'])==13
for mid,digest in old['models'].items():
 assert new['models'][mid]==digest==sha(root/'models'/f'{mid}.json')
assert old['declared_failures']==new['declared_failures']
a=json.loads((root/'docs/reviews/current-profile-parity-v1/cases.json').read_text())
b=json.loads((base/'scoped-cases.json').read_text())
assert len(a)==26 and len(b)==35 and b[:26]==a
mid='original-cam-clay-sw-electronic-log-recovery-v1'
assert sha(root/'models'/f'{mid}.json')=='637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34'
assert (root/'catalogue/agent-reviews/original-cam-clay-sw-electronic-log-recovery-agent-v1.json').read_bytes()==(root/'docs/ingestion/original-cam-clay/control-selection-v1/independent-review/e5-v1/proposed-agent-review.json').read_bytes()
# Mandel shear1000; normal deviations5000,-5000,0.
q=math.sqrt(1.5*(5000**2+5000**2+1000**2));p=100000.
f_old=q;f_new=q+1.2*p*math.log(p/150000.)
assert f_old>0 and f_new<0
run=subprocess.run(['node','--test','tests/test_laboratory_support.mjs','tests/test_laboratory_profile_policy.mjs'],cwd=root,capture_output=True,text=True)
assert run.returncode==0,run.stdout+run.stderr
paths=list(json.loads((base/'before-manifest.json').read_text()))+['web/laboratory-support.mjs','catalogue/laboratory-control-support.json','tests/test_laboratory_support.mjs','tools/check_native_fixture_contracts.py','models/'+mid+'.json','catalogue/agent-reviews/original-cam-clay-sw-electronic-log-recovery-agent-v1.json','docs/ingestion/original-cam-clay/integration-v1/scoped-cases.json']
result={'status':'passed','compiled_calls':0,'previous_model_hashes_verified':12,'previous_cases_unchanged':26,'current_cases':35,'fixture_F_old':f_old,'fixture_F_new':f_new,'unit_test_stdout':run.stdout,'reviewed_current_hashes':{s:sha(root/s) for s in paths}}
(base/'independent-review/static-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('Independent static integration checks passed; zero compiled calls.')
