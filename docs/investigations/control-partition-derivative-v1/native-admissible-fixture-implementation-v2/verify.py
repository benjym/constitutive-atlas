import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
PRIOR = D.parent / 'native-admissible-fixture-implementation-v1'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def inventory(root):
    paths = list(root.rglob('*'))
    assert not any(p.is_symlink() or '__pycache__' in p.parts or p.suffix in ('.pyc', '.pyo') for p in paths)
    return {p.relative_to(root).as_posix(): sha(p) for p in paths if p.is_file()}
freeze = json.loads((D / 'source-freeze.json').read_text())
old = json.loads((PRIOR / 'source-freeze.json').read_text())
assert sha(PRIOR / 'source-freeze.json') == freeze['prior_source_freeze_sha256']
assert sha(PRIOR / 'manifest.json') == freeze['prior_implementation_manifest_sha256']
assert inventory(Path(old['source_directory'])) == old['source_files']
assert inventory(Path(freeze['source_directory'])) == freeze['source_files']
assert len(freeze['source_files']) == 582
assert [p for p, h in freeze['source_files'].items() if old['source_files'][p] != h] == ['tests/test_solver.cpp']
assert sha(D / 'test_solver.cpp') == freeze['source_files']['tests/test_solver.cpp']
text = (D / 'test_solver.cpp').read_text()
for before, after in reversed(json.loads((D / 'checks.json').read_text())['reversible_two_substitutions']):
    assert text.count(after) == 1
    text = text.replace(after, before)
assert text == (PRIOR / 'test_solver.cpp').read_text()
contracts = json.loads((D.parent / 'native-ci-dispatch-plan-v2/process-contracts.json').read_text())
assert contracts['proposed_new_positive_stdout'].removesuffix('; models=16\n') in (D / 'test_solver.cpp').read_text()
for row in contracts['cases']:
    if row['id'] in ('missing-native', 'incompatible-native'):
        assert row['stderr'].rstrip('\n') in (D / 'test_solver.cpp').read_text()
if (D / 'manifest.json').exists():
    manifest = json.loads((D / 'manifest.json').read_text())
    assert manifest == {p.relative_to(D).as_posix(): sha(p) for p in D.rglob('*') if p.is_file() and p != D / 'manifest.json'}
print(json.dumps({'passed': True, 'source_files': 582, 'numerical_bytes_unchanged': True, 'legacy_labels_unchanged': True, 'new_labels_match_accepted_ci_plan': True, 'builds': 0, 'compiled_calls': 0}))
