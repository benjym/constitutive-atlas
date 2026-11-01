"""Provenance checks only. Never builds or executes compiled artifacts."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import sys
import tarfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
HISTORY = Path('/Users/bmar5496/code/constitutive-atlas')
sys.path.insert(0, str(ROOT))
from tools.build_maxwell_laboratory import source_manifest, REFERENCE, DEFINITION
from atlas.compiler import generate
from atlas.evidence import checked_receipt

def sha(b): return hashlib.sha256(b).hexdigest()
pins = {}
def pin(path, expected=None):
    path = Path(path)
    selected = path if path.is_absolute() else ROOT/path
    if not selected.exists() and not path.is_absolute(): selected = HISTORY/path
    digest = sha(selected.read_bytes())
    assert expected is None or digest == expected, str(selected)
    key = str(selected.relative_to(ROOT)) if selected.is_relative_to(ROOT) else str(selected)
    pins[key] = digest
    return selected

def load(path, expected=None): return json.loads(pin(path, expected).read_text())
def receipt(node): return load(node['path'], node['sha256'])
base = Path('docs/reviews/ci-followup-v3/maxwell-rebind-v2')
prior = Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/maxwell-rebind-v1')
proposal = load(base/'PROPOSAL.json')
pin(base/'ASSESSMENT.md')
old = load(prior/'current-source-manifest.json')
current = load(base/'current-source-manifest.json')
assert current == source_manifest()
for manifest in (old, current):
    assert len(manifest['files']) == 149
    assert manifest['sha256'] == sha(json.dumps(manifest['files'], sort_keys=True, separators=(',', ':')).encode())
assert old['sha256'] == proposal['old_source_manifest_sha256']
assert current['sha256'] == proposal['new_source_manifest_sha256']
changes = [dict(path=p, old_sha256=old['files'].get(p), new_sha256=current['files'].get(p)) for p in sorted(set(old['files']) | set(current['files'])) if old['files'].get(p) != current['files'].get(p)]
assert changes == proposal['delta'] and len(changes) == 1
assert changes[0]['path'] == 'atlas/measurement_units.py'
for p, digest in current['files'].items(): pin(p, digest)
before = pin(base/'measurement-units-before.py', changes[0]['old_sha256']).read_text()
after = pin('atlas/measurement_units.py', changes[0]['new_sha256']).read_text()
assert after == before.replace("    (['dny'], 's', 86400, 0),", "    (['dny'], 's', 86400, 0),\n    (['kPa/h'], 'Pa/s', 1000/3600, 0),").replace("(['V'], 'V', 1, 0), (['cycles'", "(['V'], 'V', 1, 0), (['Hz'], 'Hz', 1, 0), (['cycles'")
(HERE/'measurement-units.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before', tofile='current')))

# Conservative AST traversal includes imports in unexecuted branches/functions.
def imports(module):
    p = ROOT/(module.replace('.', '/')+'.py')
    if not p.exists(): p = ROOT/module.replace('.', '/')/'__init__.py'
    if not p.exists(): return set()
    tree = ast.parse(pin(p).read_text())
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): result.update(x.name for x in node.names)
        if isinstance(node, ast.ImportFrom):
            prefix = '.'.join(module.split('.')[:-node.level]) if node.level else ''
            name = '.'.join(x for x in (prefix, node.module or '') if x)
            result.add(name)
            result.update(name+'.'+x.name for x in node.names)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == '__import__':
            assert node.args and isinstance(node.args[0], ast.Constant), module
            result.add(node.args[0].value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr != 'import_module', module
    return {m for m in result if (ROOT/(m.replace('.', '/')+'.py')).exists() or (ROOT/m.replace('.', '/')/'__init__.py').exists()}
reach = set()
todo = ['atlas.compiler', 'atlas.model', 'atlas.path', 'atlas', 'tools.build_maxwell_laboratory']
while todo:
    module = todo.pop()
    if module in reach: continue
    reach.add(module)
    todo.extend(imports(module)-reach)
assert 'atlas.measurement_units' not in reach
# Check observed generation imports as well as the conservative source traversal.
generate(HERE/'generated', [ROOT/DEFINITION])
assert 'atlas.measurement_units' not in sys.modules
qual = receipt(proposal['prior_qualification'])
review = receipt(proposal['prior_review'])
assert qual['binding'] == review['binding']
assert qual['binding']['source_manifest_sha256'] == old['sha256']
assert qual['status'] == 'passed' and review['status'] == 'accepted'
assert qual['independent_review']['sha256'] == proposal['prior_review']['sha256']
assert review['reviewer_run'] != qual['implementation_run']
assert qual['gates'] == review['gates'] and len(review['gates']) == 5 and all(x is True for x in review['gates'].values())
for node in review['evidence'].values(): pin(node['path'], node['sha256'])
original = receipt(review['evidence']['prior_review'])
assert original['status'] == 'accepted' and original['gates'] == review['gates']
assert {k:v for k,v in original['binding'].items() if k != 'source_manifest_sha256'} == {k:v for k,v in review['binding'].items() if k != 'source_manifest_sha256'}
for node in original['evidence'].values(): pin(node['path'], node['sha256'])
bindings_node = original['evidence']['review_bindings']
bindings = receipt(bindings_node)
assert bindings['decision'].startswith('accept') and not bindings['blockers']
historical = 0
for p, digest in bindings['files'].items():
    if Path(p).is_absolute(): selected = Path(p)
    else: selected = checked_receipt(HISTORY, bindings_node['path'], p, digest)
    pin(selected, digest)
    historical += 1
archive = pin(proposal['compiled_archive']['path'], proposal['compiled_archive']['sha256'])
with tarfile.open(archive) as tar:
    members = tar.getmembers()
    assert len(members) == 3 and all(m.isfile() for m in members)
    hashes = {m.name: sha(tar.extractfile(m).read()) for m in members}
binding = dict(review['binding'], source_manifest_sha256=current['sha256'])
assert hashes == {'wasm/maxwell.js': binding['module_sha256'], 'wasm/maxwell.wasm': binding['wasm_sha256'], 'wasm/generated/models.json': binding['catalogue_file_sha256']}
assert sha((HERE/'generated/models.json').read_bytes()) == binding['catalogue_file_sha256']
assert sha((ROOT/DEFINITION).read_bytes()) == binding['model_sha256']
assert sha((ROOT/REFERENCE).read_bytes()) == binding['reference_policy_sha256']
for name in ('models.hpp', 'models.json'):
    assert (HERE/'generated'/name).read_bytes() == pin(prior/'independent-review/generated'/name).read_bytes()
impact = prior.parent/'maxwell-impact-v1'
deps = load(impact/'dependency-verification.json')
counts = {}
for backend in deps['backends']:
    side = backend['backend']
    commands = load(impact/'saved-build-metadata'/side/'compile_commands.json')
    assert len(commands) == 13 and not any('measurement_units' in json.dumps(c) for c in commands)
    assert len(backend['dependency_files']) == 13
    build = Path(commands[0]['directory'])
    for depname, digest in backend['dependency_files'].items():
        saved = pin(impact/'saved-build-metadata'/side/Path(depname).relative_to(build), digest)
        assert 'measurement_units' not in saved.read_text()
    for relative, values in backend['source_dependency_hashes'].items():
        assert values['retained'] == values['current']
        pin(relative, values['retained'])
    for name, digest in backend['generated'].items(): pin(HERE/'generated'/name, digest)
    counts[side] = dict(commands=13, dependency_files=13, unchanged_repository_dependencies=len(backend['source_dependency_hashes']))
result = dict(status='passed', scope='provenance-only inherited original numerical gates; no compiled execution', broad_manifest_entries=149, changes=changes, compiler_and_interpreter_import_closure=sorted(reach), observed_measurement_units_import=False, historical_evidence_bindings_verified=historical, backend_dependency_checks=counts, unchanged_archive_members=hashes, canonical_generation='exact original models.hpp and models.json bytes', binding=binding, inherited_gates=review['gates'], external_historical_root=str(HISTORY))
(HERE/'check-results.json').write_text(json.dumps(result, indent=2)+'\n')
(HERE/'checked-pins.json').write_text(json.dumps(dict(files=pins), indent=2)+'\n')
print(json.dumps(result, indent=2))
