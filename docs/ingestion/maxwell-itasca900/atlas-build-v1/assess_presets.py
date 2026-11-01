"""Apply unchanged frozen analytical cases to actual CLI preset results."""
import importlib.util
import json
from pathlib import Path
import sys

root, results = map(Path, sys.argv[1:])
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location('maxwell_cases', root/'tests/test_maxwell.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
cases = json.loads((root/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json').read_text())['cases']
errors = {}
for name, case_id in [('relaxation','relaxation-schedule'), ('creep','creep-schedule'), ('oedometer','oedometer'), ('load-hold-reverse','load-hold-reverse')]:
    case = next(c for c in cases if c['id'] == case_id)
    source = json.loads((root/'examples/maxwell'/f'{name}.json').read_text())
    assert source == case['specification'], name+' source/reference case mismatch'
    data = json.loads((results/f'{name}.json').read_text())
    assert data['specification'] == source, name+' CLI source echo mismatch'
    errors[name] = checks.assess(case, data)
    for key in ['model', 'parameters', 'initial', 'initial_strain', 'initial_strain_rate', 'start_time', 'segments']:
        assert data[key] == source[key], name+' echo '+key
print(json.dumps({'passed': True, 'four_source_presets': True, 'errors_Pa': errors}, indent=2))
