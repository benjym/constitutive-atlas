import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,shutil
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
BASE=D.parent/'native-ci-dispatch-plan-v2'
DEST=Path('/private/tmp/atlas-md1997-ci-dispatch-v1/source')
SOURCE=Path('/private/tmp/atlas-control-partition-v1/source')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((BASE/'manifest.json').read_bytes())=='27325aae9a3f5f0d2ea7c4b7cc30ff6ccf80cd5ac454f14bbc234e14bfeb8710'
original=json.loads((D.parent/'implementation-v1/source-freeze.json').read_text())['source_files']
assert len(original)==582
assert not DEST.exists()
for name,digest in original.items():
    data=(SOURCE/name).read_bytes();assert sha(data)==digest
    p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
overlays={}
for name in ['tools/check_native_fixture_contracts.py','catalogue/laboratory-package-policy.json','.github/workflows/verify.yml','tests/test_ci_profiles.py']:
    data=(BASE/'published-37d'/name).read_bytes()
    overlays[name]={'before_sha256':original.get(name),'published_sha256':sha(data)}
    p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
assert all(sha((SOURCE/n).read_bytes())==h for n,h in original.items())
(D/'preparation.json').write_text(json.dumps({'identity':'native-ci-dispatch-implementation-v1-preparation','original_source':str(SOURCE),'destination':str(DEST),'original582':original,'published_overlays':overlays,'other_overlays':[],'builds':0,'compiled_calls':0,'fixture_integration':'Pending; test_solver.cpp is untouched original582, not a positive admissible fixture.'},indent=2)+'\n')
