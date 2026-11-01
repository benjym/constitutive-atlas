"""Read-only closeout audit; writes only this review's result file."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
PACKET = ROOT/'docs/ingestion/original-cam-clay'
B = PACKET/'control-selection-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = []
bindings = {}
def bind(path, expected=None):
    actual = sha(path)
    if expected is not None:
        assert actual == expected, str(path)
    bindings[str(path.relative_to(ROOT))] = actual
    return actual

for name in ('README.md', 'verification.json', 'verify.py', 'constraint-results.json', 'baseline-DELIVERY.md'):
    bind(HERE.parent/name)
for name in ('source-receipt.json', 'delivery-source-v1/source-follow-up.json'):
    bind(PACKET/name)
for name in ('docs/MODEL_DELIVERY_CHECKLIST.md', 'docs/FORMULATION_CONTRACT.md', 'docs/AGENT_REVIEW_POLICY.md', 'schemas/model-v0.3.schema.json', 'atlas/initialization.py'):
    bind(ROOT/name)
manifest_path = HERE.parent/'manifest.json'
bind(manifest_path)
closeout_manifest = json.loads(manifest_path.read_text())
for name, expected in closeout_manifest['files'].items():
    bind(HERE.parent/name, expected)
checks.append({'name': 'final closeout manifest', 'count': len(closeout_manifest['files']), 'status': 'pass'})
v = json.loads((HERE.parent/'verification.json').read_text())
for name, expected in v['bindings'].items():
    bind(ROOT/name, expected)
checks.append({'name': 'closeout exact bindings including retained private source', 'count': len(v['bindings']), 'status': 'pass'})
for name in ('review-bindings.json', 'candidate-review-v2-manifest.json', 'execution-plan-v1/update-v2-bindings.json'):
    p = B/'independent-review'/name
    bind(p)
    manifest = json.loads(p.read_text())
    for file, digest in manifest.items():
        bind(ROOT/file, digest)
    checks.append({'name': name, 'count': len(manifest), 'status': 'pass'})
f = PACKET/'execution-v1/freeze-manifest-v2.json'
freeze = json.loads(f.read_text())
assert freeze['compiled_numerical_observations'] == 0
assert freeze['native_build_already_completed'] is True
for name, expected in freeze['files'].items():
    bind(f.parent/name, expected)
checks.append({'name': 'additive pre-observation freeze identity (not pre-build)', 'count': len(freeze['files']), 'status': 'pass'})
receipt = json.loads((PACKET/'source-receipt.json').read_text())['source']
follow = json.loads((PACKET/'delivery-source-v1/source-follow-up.json').read_text())['retained_source']
source = ROOT/'.local/private-sources/original-cam-clay/schofield-wroth-electronic-transcription.pdf'
assert source.stat().st_size == receipt['bytes'] == follow['bytes'] == 7886630
assert receipt['sha256'] == follow['sha256'] == sha(source)
assert receipt['pdf_pages'] == follow['pages'] == 229
assert receipt['edition_fidelity_verified'] is False
checks.append({'name': 'source receipts/retention identity and unauthenticated edition distinction', 'status': 'pass'})
from atlas.model import load
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError
m = load(B/'candidate-v03-v2.json')
assert m['schema_version'] == '0.3' and 'integration' not in m
for field in ('formulation', 'initialization', 'parameters', 'state'):
    assert m[field] == v[field]
assert m['id'] == 'original-cam-clay-sw-electronic-log-recovery-v1'
assert [s['name'] for s in m['state']] == ['sigma', 'v']
assert sum(6 if s['shape']=='sym' else 1 for s in m['state']) == 7
assert set(m['equations']) == {'sigma', 'v'}
assert m['equations'] == {'sigma': 'sigma - sigma_end', 'v': 'v - v_end'}
p = {k: d['default'] for k, d in m['parameters'].items()}
s = {d['name']: d['initial'] for d in m['state']}
prepared = initialize_state(m, s, p)
assert prepared['initial'] == s['sigma'] + [s['v']]
rejects = []
for label, state, params in (
    ('missing specific volume', {'sigma': s['sigma']}, p),
    ('missing resolved parameter', s, {k: x for k,x in p.items() if k!='pref'}),
    ('nonpositive specific volume', {**s,'v':0}, p),
    ('nonpositive pressure', {**s,'sigma':[-1,-1,-1,0,0,0]}, p),
    ('inadmissible yield', {**s,'sigma':[100000,100000,100000,1e6,0,0]}, p),
):
    try:
        initialize_state(m, state, params)
    except (ValidationError, ArithmeticError, ValueError):
        rejects.append(label)
    else:
        raise AssertionError(label)
checks.append({'name': 'current v0.3 schema/profile/state/parameter mapping and explicit initialization', 'status':'pass', 'initialization_rejections': rejects})
results = json.loads((B/'independent-review/candidate-review-results-36012205c441.json').read_text())
# This audit consumes the bound independent report; it does not rerun its writer.
assert '2e-10' in (B/'independent-review/candidate-review-v2.md').read_text()
output = {'task':'CLOSE-occ-e1-e2-v1', 'reviewer':'/root/occ_e1_e2_closeout_review', 'status':'pass', 'checks':checks, 'bindings':bindings, 'compiled_calls':0, 'builds':0, 'E5_approval':False}
(HERE/'check-results.json').write_text(json.dumps(output, indent=2)+'\n')
print(json.dumps({'status':'pass','checks':len(checks),'unique_hashed_inputs':len(bindings),'compiled_calls':0}))
