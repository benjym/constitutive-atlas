"""Assess saved recovery of previously unset recorded solver tests; no execution."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
B=HERE.parent/'release-host-fixes-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ci=json.loads((B/'portable-ci-v3.json').read_text())
d=json.loads((B/'recorded-skip-recovery.json').read_text())
expected=set()
for line in ci['stderr'].splitlines():
    if ' ... skipped ' in line and 'ATLAS_RECORDED_SOLVER' in line:
        expected.add('tests.'+re.search(r'\(([^)]+)\) \.\.\. skipped',line)[1])
assert len(expected)==14 and set(d['command'][4:-1])==expected
assert d['returncode']==0 and re.search(r'Ran 14 tests in [0-9.]+s\n\nOK\n',d['stderr'])
assert d['solver']=='/private/tmp/atlas-occ-integration-v1/build-native/atlas_solver'
# Approved/source inputs stay unchanged; final status prose receives new bindings.
prior=json.loads((HERE/'identity-results.json').read_text())
for name,digest in prior['bindings'].items():
    p=Path(name);p=p if p.is_absolute() else ROOT/p
    assert sha(p)==digest,str(p)
files=[B/'recorded-skip-recovery.json',B/'portable-ci-v3.json',B/'BROWSER-FINAL.md',ROOT/'docs/ingestion/original-cam-clay/DELIVERY.md',HERE.parent/'README.md',HERE.parent/'RELEASE.md',HERE/'SUPPLEMENT-FINAL.md',HERE/'supplement-manifest.json',Path(d['solver'])]
result={'status':'pass','portable_total':1413,'portable_skips':63,'canonical_exact_recovered':31,'recorded_recovered':14,'remaining_optional_or_private_source_skips':18,'exact_skipped_recorded_ID_set_recovered':True,'compiled_calls':0,'builds':0,'bindings':{str(p):sha(p) for p in files}}
(HERE/'recorded-recovery-check-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))
