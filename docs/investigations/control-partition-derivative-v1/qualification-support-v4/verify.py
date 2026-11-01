"""Read-only support closure verification; no backend execution or package claim."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
PRIOR = D.parent / 'qualification-support-v3'
ROOT = D.parents[3]
OLD = Path('/private/tmp/atlas-control-partition-support-v2/source')
NEW = Path('/private/tmp/atlas-control-partition-support-v3/source')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(root):
    paths = list(root.rglob('*'))
    assert not any(p.is_symlink() or '__pycache__' in p.parts or p.suffix in ('.pyc', '.pyo') for p in paths)
    return {p.relative_to(root).as_posix(): sha(p) for p in paths if p.is_file()}

prep = json.loads((D / 'preparation.json').read_text())
assert sha(PRIOR / 'manifest.json') == prep['prior_manifest_sha256']
assert sha(PRIOR / 'source-freeze.json') == prep['prior_source_freeze_sha256']
assert sha(PRIOR / 'availability-addendum-v1.json') == prep['availability_sha256']
old = json.loads((PRIOR / 'source-freeze.json').read_text())['files']
assert inventory(OLD) == old and len(old) == 2614
new = json.loads((D / 'source-freeze.json').read_text())['files']
assert inventory(NEW) == new and len(new) == 2628
assert all(new[p] == h for p, h in old.items())
installed = {r['required_path']: r['required_sha256'] for r in prep['installed']}
assert len(installed) == 14
assert {p: new[p] for p in set(new) - set(old)} == installed
runtime = json.loads((ROOT / 'docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v5/source-freeze.json').read_text())
assert len(runtime['source_files']) == 582
for p, h in runtime['source_files'].items():
    assert sha(Path(runtime['source_directory']) / p) == h
    assert new[p] == h or p == 'tests/test_j2_main_routing.mjs'
assert json.loads((D / 'patched-source-manifests.json').read_text())['profiles'] == json.loads((PRIOR / 'patched-source-manifests.json').read_text())['profiles']
original = (PRIOR / 'audit_guards.py').read_text()
adapted = (D / 'audit_guards.py').read_text()
assert adapted.replace('/private/tmp/atlas-control-partition-support-v3/source', '/private/tmp/atlas-control-partition-support-v2/source').replace('actual-nine-builder-source-guard-audit-v4', 'actual-nine-builder-source-guard-audit-v3') == original
closure = json.loads((D / 'guard-closure.json').read_text())
assert len(closure['results']) == 9
assert all(r['source_guard_passed'] and r['evaluated_guard_stages_passed'] and not r['missing_literal_source_inputs'] for r in closure['results'])
if (D / 'manifest.json').exists():
    manifest = json.loads((D / 'manifest.json').read_text())
    actual = {p.relative_to(D).as_posix(): sha(p) for p in D.rglob('*') if p.is_file() and p != D / 'manifest.json'}
    assert actual == manifest
print(json.dumps({'passed': True, 'source_files': 2628, 'prior_files_unchanged': 2614, 'added_exact_dependencies': 14, 'original582_immutable': True, 'source_guards_passed': 9, 'literal_gaps': 0, 'runtime_matchers_unchanged': True, 'compiled_calls': 0, 'builds': 0, 'qualified_package_ready': False}))
