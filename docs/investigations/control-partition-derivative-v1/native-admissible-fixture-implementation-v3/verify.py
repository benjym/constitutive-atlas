import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
PRIOR = D.parent / 'native-admissible-fixture-implementation-v2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(root):
    paths = list(root.rglob('*'))
    assert not any(p.is_symlink() or '__pycache__' in p.parts or p.suffix in ('.pyc', '.pyo') for p in paths)
    return {p.relative_to(root).as_posix(): sha(p) for p in paths if p.is_file()}
f = json.loads((D / 'source-freeze.json').read_text())
old = json.loads((PRIOR / 'source-freeze.json').read_text())
assert sha(PRIOR / 'manifest.json') == f['prior_manifest_sha256']
assert sha(PRIOR / 'source-freeze.json') == f['prior_source_freeze_sha256']
assert inventory(Path(old['source_directory'])) == old['source_files']
assert inventory(Path(f['source_directory'])) == f['source_files']
assert len(f['source_files']) == 582
assert [p for p, h in f['source_files'].items() if old['source_files'][p] != h] == ['tests/test_solver.cpp']
assert sha(D / 'test_solver.cpp') == f['source_files']['tests/test_solver.cpp']
assert sha(D / 'published37d-test_solver.cpp') == f['published_test_solver_sha256']
block = f['exact_published_block']
text = (D / 'test_solver.cpp').read_text()
assert len(block.splitlines()) == 6 and text.count(block) == 1
assert (D / 'published37d-test_solver.cpp').read_text().count(block) == 1
assert text.replace(block, '', 1) == (PRIOR / 'test_solver.cpp').read_text()
if (D / 'manifest.json').exists():
    assert json.loads((D / 'manifest.json').read_text()) == {p.relative_to(D).as_posix(): sha(p) for p in D.rglob('*') if p.is_file() and p != D / 'manifest.json'}
print(json.dumps({'passed': True, 'source_files': 582, 'exact_published_lines_added': 6, 'prior_source_immutable': True, 'all_md_bytes_unchanged': True, 'builds': 0, 'compiled_calls': 0}))
