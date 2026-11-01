"""Prepare prospective ordinary-atlas inputs; refuse drift or repeated mutation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
def write(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

before = read(HERE/'frozen/bindings-before.json')
for row in before['live_source_identities']:
    if row['original_path'] != 'catalogue/approved-models.json':
        assert sha(ROOT/row['original_path']) == row['sha256'], row
model = read(ROOT/'models/duncan-chang-1970-endpoint-average.json')
digest = sha(ROOT/'models'/f"{model['id']}.json")
assert digest == '452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'
policy_path = ROOT/'catalogue/laboratory-package-policy.json'
policy = read(policy_path)
assert len(policy['models']) == 13
policy['id'] = 'supported-package-fourteen-duncan-v1'
policy['models'][model['id']] = digest
policy['limitations'].append('Duncan–Chang constant-nu endpoint-average: exact independently reviewed definition; source-coefficient presets are illustrative, with no calibration, experimental validation or FE-host tangent claim. Ordinary default is an additional software qualification.')
write(policy_path, policy)

cases = read(ROOT/'docs/ingestion/original-cam-clay/integration-v1/scoped-cases.json')
assert len(cases) == 35
settings = dict(version='incremental-settings-0.1', norm='scaled_component_max', residual_tolerance=2e-10, rate_tolerance=1e-6, max_iterations=45, max_depth=14, max_substeps=20000, max_backtracks=11)
parameters = [v['default'] for v in model['parameters'].values()]
initial = [100000,100000,100000,0,0,0,0]
# Strict cross-profile corpus checks an exact zero hold. Nonzero source presets
# retain their separately frozen E4 error budget and all-state comparisons.
hold = dict(response_contract='stress-scope-0.1',stress_scope='effective',model=model['id'],parameters=parameters,initial=initial,protocol=0,target=0,steps=4,cycles=0,integration_settings=settings)
hold['loading'] = dict(version='laboratory-controls-0.1', encoding='ieee754-binary64-hex',producer=dict(version='laboratory-waveform-0.1',algorithm='linear-rne-v1',target_bits='0000000000000000',steps=4,cycles=0), controls_bits=['0000000000000000']*5)
cases.append(dict(id='duncan/source-hydrostatic-hold', specification=hold, expected_ok=True, expected_message='', expected_points=5))
write(HERE/'scoped-cases.json', cases)
profile_path = ROOT/'catalogue/laboratory-profile-policy.json'
profile = read(profile_path)
profile['id'] = 'current-fourteen-duncan-profiles-v1'
profile['supported_policy']['sha256'] = sha(policy_path)
profile['cases'] = dict(path=str((HERE/'scoped-cases.json').relative_to(ROOT)),sha256=sha(HERE/'scoped-cases.json'))
profile['case_count'] = len(cases)
profile['limitations'].append('Duncan strict 1e-10 cross-profile parity covers an exact hydrostatic zero hold. Nonzero dense/loose source presets retain the independently reviewed E4 4e-8/p_ref state budget; no bitwise or uniform 1e-10 nonzero-path claim.')
write(profile_path, profile)

manifest_path = ROOT/'catalogue/manifest.json'
manifest = read(manifest_path)
family = next(m for m in manifest['models'] if m['id']=='duncan-chang-1970')
family['note'] = 'Original1970 constant-Poisson 3D formulation is implemented as the separately identified endpoint-average realization. Family discovery record; do not count as a second executable formulation.'
family.pop('capability_gap')
manifest['models'].insert(manifest['models'].index(family)+1,dict(id=model['id'],name=model['name'],family='nonlinear elasticity',status='draft',executable=True,dossier=f"docs/models/{model['id']}.md",discovery_url='https://doi.org/10.1061/JSFEAQ.0001458',note='Complete original constant-nu incremental3D closure with explicit Atlas finite endpoint averaging/history/branch/failure choices. Exact definition has accepted independent agent review and native/Wasm source qualification. Fixed spatial frame, effective stress, illustrative source coefficients; no pore-fluid/dilatancy/physical-time law, FE-host tangent qualification or experimental validation. Approval is determined by exact registry records; draft definition metadata is retained.'))
write(manifest_path, manifest)

requests = read(ROOT/'docs/ingestion/duncan-chang-1970/material-v1/execution-v2/requests.json')
write(HERE/'preset-inputs.json', requests['presets'])
print('Prepared prospective fourteen-model policies, 36 scoped cases and discovery entry.')
