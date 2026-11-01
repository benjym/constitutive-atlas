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

base = Path('docs/reviews/ci-followup-v4/controlled-path-rebind-v1')
prior = Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/qualified-norsand')
qual = load(prior/'controlled-path-qualification.json')
review = load(prior/'build-review.json',qual['independent_review']['sha256'])
assert qual['independent_review']['path'] == 'build-review.json'
assert qual['schema_version'] == 'controlled-path-qualified-build-1' and qual['status'] == 'passed'
assert review['schema_version'] == 'controlled-path-independent-build-review-1' and review['status'] == 'accepted'
assert qual['model'] == review['model'] == 'norsand-jefferies-1993-active-axial'
assert qual['binding'] == review['binding'] and qual['gates'] == review['gates']
assert review['reviewer_run'] != qual['implementation_run']
gates = dict(native_requests=58,wasm_requests=58,native_successes=40,native_rejections=18,wasm_successes=40,wasm_rejections=18,source_analytical=True,parity=True)
assert review['gates'] == gates
required = {p.relative_to(ROOT).as_posix() for p in (ROOT/'cpp/include/atlas').rglob('*.hpp')}
required.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'cpp/scalar-functions').rglob('*') if p.is_file())
required.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'atlas').rglob('*.py') if '__pycache__' not in p.parts)
required.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'schemas').rglob('*.json'))
required.update(('cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'))
assert set(review['binding']['sources']) == required
current = {p:sha(pin(p).read_bytes()) for p in sorted(required)}
changes = [dict(path=p,old_sha256=review['binding']['sources'][p],new_sha256=current[p]) for p in sorted(required) if current[p] != review['binding']['sources'][p]]
assert len(changes) == 1 and changes[0]['path'] == 'atlas/measurement_units.py'
before = pin('docs/reviews/ci-followup-v3/maxwell-rebind-v2/measurement-units-before.py',changes[0]['old_sha256']).read_text()
after = pin(changes[0]['path'],changes[0]['new_sha256']).read_text()
assert after == before.replace("    (['dny'], 's', 86400, 0),", "    (['dny'], 's', 86400, 0),\n    (['kPa/h'], 'Pa/s', 1000/3600, 0),").replace("(['V'], 'V', 1, 0), (['cycles'", "(['V'], 'V', 1, 0), (['Hz'], 'Hz', 1, 0), (['cycles'")
(HERE/'measurement-units.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before',tofile='current')))
reach = set()
todo = ['atlas','atlas.compiler','atlas.path','atlas.model','tools.generate_controlled_path','tools.build_controlled_path_web']
while todo:
    module = todo.pop()
    if module in reach: continue
    reach.add(module)
    todo.extend(imports(module)-reach)
assert 'atlas.measurement_units' not in reach
paths=[ROOT/'models/research/norsand/norsand-jefferies-1993-active-axial.json',ROOT/'tests/fixtures/controlled-path/synthetic-curved.json',ROOT/'tests/fixtures/controlled-path/synthetic-model.json']
generate(HERE/'generated', paths)
assert 'atlas.measurement_units' not in sys.modules
for name,digest in review['binding']['generated'].items():
    assert pin(prior/'generated'/name,digest).read_bytes() == pin(HERE/'generated'/name,digest).read_bytes()
for name,digest in review['binding']['artifacts'].items(): pin(prior/name,digest)
for node in review['evidence'].values(): pin(node['path'],node['sha256'])
bindings_node = review['evidence']['review_bindings']
bindings = receipt(bindings_node)
assert bindings['decision'].startswith('accept') and not bindings['blockers']
historical = 0
for p,digest in bindings['files'].items():
    selected = Path(p) if Path(p).is_absolute() else checked_receipt(HISTORY,bindings_node['path'],p,digest)
    pin(selected,digest)
    historical += 1
binding = dict(review['binding'],sources=current)
assert binding['artifacts'] == review['binding']['artifacts'] and binding['generated'] == review['binding']['generated']
proposal = load(base/'PROPOSAL.json')
assert proposal['prior_directory'] == prior.as_posix()
pin(prior/'controlled-path-qualification.json',proposal['prior_qualification_sha256'])
pin(prior/'build-review.json',proposal['prior_review_sha256'])
assert proposal['source_delta'] == changes
result=dict(status='passed',scope='provenance-only gate inheritance for identical controlled-path engine; no numerical execution',required_source_count=len(required),changes=changes,compiler_interpreter_and_packager_import_closure=sorted(reach),observed_measurement_units_import=False,canonical_generation='all three original generated outputs byte-identical',historical_evidence_bindings_verified=historical,binding=binding,inherited_gates=gates,external_historical_root=str(HISTORY))
(HERE/'check-results.json').write_text(json.dumps(result,indent=2)+'\n')
(HERE/'checked-pins.json').write_text(json.dumps(dict(files=pins),indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k != 'binding'},indent=2))
