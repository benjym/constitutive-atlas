"""Validate saved final receipts and artifact hashes; no binary execution."""
from pathlib import Path
import collections,hashlib,json,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
B=HERE.parent/'release-host-fixes-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bindings={}
def bind(p,expected=None):
    v=sha(p)
    if expected is not None:assert v==expected,str(p)
    bindings[str(p)]=v
# Earlier substantive acceptance remains tied to unchanged source bytes.
prior=json.loads((HERE/'identity-results.json').read_text())
for name,digest in prior['bindings'].items():
    p=Path(name);p=p if p.is_absolute() else ROOT/p
    bind(p,digest)
for name in ['portable-ci-v1.json','portable-ci-v2.json','portable-ci-v3.json','time-fixture-build.json','canonical-exact-tests.json','canonical-exact-tests-v2.json','BROWSER-FINAL.md','final-package-manifest.json','browser-observed-assets.json','supported-package.json']:
    bind(B/name)
for p in [ROOT/'docs/ingestion/original-cam-clay/DELIVERY.md',HERE.parent/'README.md',HERE.parent/'RELEASE.md',ROOT/'tools/run_ci_tests.py',ROOT/'tools/ci_exact_replays.json',HERE/'final-package-check-results.json']:
    bind(p)
ci=json.loads((B/'portable-ci-v3.json').read_text())
assert ci['returncode']==0
assert re.search(r'Ran 1413 tests in [0-9.]+s\n\nOK \(skipped=63\)\n',ci['stderr'])
assert not re.search(r'^FAILED \(',ci['stderr'],re.M)
assert ci['environment']['ATLAS_TIME_SOLVER']=='/private/tmp/atlas-occ-release-native-v1/atlas_time_solver'
assert ci['environment']['ATLAS_SOLVER']=='/private/tmp/atlas-occ-integration-v1/build-native/atlas_solver'
# stdout contains expected nested negative-test output, not the suite status.
skips=collections.Counter(x.split(' ... skipped ')[1] for x in ci['stderr'].splitlines() if ' ... skipped ' in x)
assert sum(skips.values())==63
assert skips["'Exact archived macOS arithmetic; required macos-26 job runs the unchanged test'"]==31
exact=json.loads((B/'canonical-exact-tests-v2.json').read_text())
policy=json.loads((ROOT/'tools/ci_exact_replays.json').read_text())
assert set(exact['command'][4:-1])=={'tests.'+x for x in policy['exact_test_ids']}
assert exact['returncode']==0 and 'Ran 31 tests' in exact['stderr'] and exact['stderr'].endswith('OK\n')
time=json.loads((B/'time-fixture-build.json').read_text())
assert time['returncodes']==[0,0]
assert time['commands'][1].endswith('--target atlas_time_solver --parallel 1')
for name,digest in time['source_sha256'].items():bind(ROOT/name,digest)
bind(Path(time['executable']),time['executable_sha256'])
for name,digest in time['generated'].items():bind(Path(time['executable']).parent/'time-generated'/name,digest)
# Existing qualified ordinary artifact identity, read only.
source=Path('/private/tmp/atlas-occ-integration-v1/build-native/atlas_solver')
bind(source)
result={'status':'pass','portable_tests':1413,'portable_skips':63,'canonical_exact_recovered':31,'remaining_optional_skips':32,'skip_reasons':dict(skips),'earlier_substantive_inputs_unchanged':True,'fresh_time_artifact_verified':True,'compiled_calls':0,'builds':0,'bindings':bindings}
(HERE/'final-receipt-check-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','skip_reasons')},indent=2))
