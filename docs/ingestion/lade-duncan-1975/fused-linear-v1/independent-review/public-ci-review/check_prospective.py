"""Pure source/policy closure and adversarial helper checks; no package/material calls."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
checks = []

def test(name, value):
    assert value, name
    checks.append({'name': name, 'passed': True})

base = ROOT / 'docs/ingestion/lade-duncan-1975/atlas-integration-v1'
for relative in ['public-ci-v1/SOURCE_FREEZE.json', 'package-policy-v1/SOURCE_FREEZE.json',
                 'package-policy-v1/SOURCE_FREEZE-v2.json', 'package-policy-v1/SOURCE_FREEZE-v3.json', 'public-ci-v1/POLICY.json']:
    receipt = json.loads((base / relative).read_bytes())
    for name, pin in receipt.get('files', {}).items():
        source = ROOT / name
        if relative == 'package-policy-v1/SOURCE_FREEZE.json' and name == 'tools/test_implicit_path_package.py':
            source = base / 'package-policy-v1/checker-before-provenance-fix.py'
        if relative == 'package-policy-v1/SOURCE_FREEZE-v2.json' and name == 'tools/test_implicit_path_package.py':
            source = base / 'package-policy-v1/checker-before-review-link-fix.py'
        test(relative + ': ' + name, hashlib.sha256(source.read_bytes()).hexdigest() == pin)

spec = importlib.util.spec_from_file_location('reviewed_package_checker', ROOT / 'tools/test_implicit_path_package.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
review = {'checklist': [{'id': name, 'outcome': 'pass'} for name in sorted(module.DECISIONS)], 'blocking_findings': []}
test('exact nine decisions accepted', module.scientific_decisions(review))
for mode in ['duplicate', 'missing', 'NA', 'finding', 'wrong ID']:
    bad = copy.deepcopy(review)
    if mode == 'duplicate': bad['checklist'][-1] = bad['checklist'][0]
    if mode == 'missing': bad['checklist'].pop()
    if mode == 'NA': bad['checklist'][0]['outcome'] = 'not_applicable'
    if mode == 'finding': bad['blocking_findings'] = ['unresolved']
    if mode == 'wrong ID': bad['checklist'][0]['id'] = 'invented'
    test('reject scientific ' + mode, not module.scientific_decisions(bad))
expected = {'model_sha256': module.MODEL_SHA, 'runtime_sha256': 'runtime',
            'generated': {'models.hpp': 'header', 'models.json': 'catalogue'},
            'ordered_inputs': [{'path': 'model.json', 'sha256': 'input'}],
            'module_sha256': 'loader', 'wasm_sha256': 'wasm'}
qualification = {'schema_version': 'implicit-path-qualified-build-1', 'model': module.MODEL,
                 'status': 'passed', 'implementation_run': '/root', 'binding': expected,
                 'gates': dict.fromkeys(module.GATES, True)}
accepted = {'status': 'accepted', 'reviewer_run': '/root/independent', 'binding': expected,
            'gates': dict.fromkeys(module.GATES, True)}
test('complete numerical binding accepted', module.numerical_binding(qualification, accepted, expected))
for key, value in [('schema_version', 'wrong'), ('model', 'wrong'), ('status', 'failed'),
                   ('implementation_run', ''), ('binding', {})]:
    bad = copy.deepcopy(qualification); bad[key] = value
    test('reject qualification ' + key, not module.numerical_binding(bad, accepted, expected))
for name in module.GATES:
    bad = copy.deepcopy(qualification); bad['gates'][name] = False
    test('reject false gate ' + name, not module.numerical_binding(bad, accepted, expected))
for key in expected:
    bad = copy.deepcopy(accepted); bad['binding'][key] = 'drift'
    test('reject reviewer binding ' + key, not module.numerical_binding(qualification, bad, expected))
for key, value in [('reviewer_run', '/root'), ('reviewer_run', ''), ('status', 'pending')]:
    bad = copy.deepcopy(accepted); bad[key] = value
    test('reject reviewer ' + key + str(value), not module.numerical_binding(qualification, bad, expected))
result = {'passed': True, 'scope': 'Pure closure and helper predicates only; no regeneration, package or material execution', 'checks': checks}
(OUT / 'prospective-check-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': True, 'checks': len(checks)}))
