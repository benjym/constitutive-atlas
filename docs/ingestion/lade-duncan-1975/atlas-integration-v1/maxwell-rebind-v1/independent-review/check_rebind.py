"""Read saved evidence and sources only; no artifact execution or production writes."""
from pathlib import Path
import hashlib
import json
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
from tools.build_maxwell_laboratory import source_manifest
from atlas.evidence import checked_receipt
from atlas.compiler import generate

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(Path(path).read_text())

pins = {}
def pin(path, expected=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT/path
    digest = sha(path.read_bytes())
    if expected is not None:
        assert digest == expected, str(path)
    pins[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)] = digest
    return path

proposal = load(pin(HERE.parent/'PROPOSAL.json'))
delta = load(pin(HERE.parent/'installed-delta.json'))
current = load(pin(HERE.parent/'current-source-manifest.json'))
old_input = load(pin(delta['retained_input_receipt']['path'], delta['retained_input_receipt']['sha256']))
old = old_input['source_manifest']
assert current == source_manifest()
for manifest in [old, current]:
    assert sha(json.dumps(manifest['files'], sort_keys=True, separators=(',', ':')).encode()) == manifest['sha256']
assert len(old['files']) == len(current['files']) == 149
changes = [dict(path=p, old_sha256=old['files'].get(p), new_sha256=current['files'].get(p))
           for p in sorted(set(old['files']) | set(current['files']))
           if old['files'].get(p) != current['files'].get(p)]
assert changes == delta['delta'] and len(changes) == 1
assert changes[0]['path'] == 'cpp/profiles/implicit-path-v1/include/atlas/solver.hpp'
assert proposal['old_binding']['source_manifest_sha256'] == old['sha256']
assert proposal['proposed_binding']['source_manifest_sha256'] == current['sha256']
assert {k:v for k,v in proposal['old_binding'].items() if k != 'source_manifest_sha256'} == {k:v for k,v in proposal['proposed_binding'].items() if k != 'source_manifest_sha256'}
for p, digest in current['files'].items():
    pin(p, digest)

qual = load(pin(**dict(path=proposal['prior_qualification']['path'], expected=proposal['prior_qualification']['sha256'])))
review_path = pin(proposal['prior_review']['path'], proposal['prior_review']['sha256'])
review = load(review_path)
assert qual['binding'] == review['binding'] == proposal['old_binding']
assert review['status'] == 'accepted' and qual['status'] == 'passed'
assert qual['gates'] == review['gates'] == proposal['inherited_gates']
assert len(qual['gates']) == 5 and all(v is True for v in qual['gates'].values())
assert review['reviewer_run'] != qual['implementation_run']
assert qual['independent_review']['sha256'] == sha(review_path.read_bytes())
for node in review['evidence'].values():
    pin(node['path'], node['sha256'])

# Preserve the original independent decision and verify its complete exact evidence,
# including archived historical pairs via the repository's unchanged receipt guard.
bindings_path = ROOT/review['evidence']['review_bindings']['path']
bindings = load(bindings_path)
assert bindings['decision'].startswith('accept') and not bindings['blockers']
historical_verified = 0
for p, digest in bindings['files'].items():
    selected = Path(p) if Path(p).is_absolute() else checked_receipt(ROOT, bindings_path.relative_to(ROOT), p, digest)
    pin(selected, digest)
    historical_verified += 1

packet = ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-v2'
provenance = load(pin(packet/'provenance.json'))
archive = pin(proposal['same_compiled_archive']['path'], proposal['same_compiled_archive']['sha256'])
with tarfile.open(archive) as tar:
    members = tar.getmembers()
    assert len(members) == 3 and all(m.isfile() for m in members)
    hashes = {m.name:sha(tar.extractfile(m).read()) for m in members}
assert hashes == provenance['archive_members']
assert hashes['wasm/maxwell.js'] == proposal['old_binding']['module_sha256']
assert hashes['wasm/maxwell.wasm'] == proposal['old_binding']['wasm_sha256']
assert hashes['wasm/generated/models.json'] == proposal['old_binding']['catalogue_file_sha256']

impact = ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/maxwell-impact-v1'
pin(proposal['impact_assessment']['path'], proposal['impact_assessment']['sha256'])
deps = load(pin(impact/'dependency-verification.json'))
dependency_counts = {}
for backend in deps['backends']:
    side = backend['backend']
    audit = load(pin(f'docs/reviews/common-scalar-functions-v1/consumer-results-v1/{side}/maxwell/build-audit.json'))
    commands = load(pin(impact/'saved-build-metadata'/side/'compile_commands.json'))
    assert commands == audit['commands'] and len(commands) == 13
    assert not any('cpp/profiles/' in json.dumps(c) for c in commands)
    source_root = Path('/private/tmp/atlas-common-scalar-functions-v1/consumer-source-v1')
    build = Path(commands[0]['directory'])
    assert len(backend['dependency_files']) == 13
    encountered = set()
    for depname, digest in backend['dependency_files'].items():
        dep = Path(depname)
        saved = pin(impact/'saved-build-metadata'/side/dep.relative_to(build), digest)
        assert dep.read_bytes() == saved.read_bytes()
        text = saved.read_text().replace('\\\n', ' ')
        assert 'cpp/profiles/' not in text
        for token in text.split():
            path = Path(token)
            if path.is_relative_to(source_root) and path.is_file():
                relative = path.relative_to(source_root).as_posix()
                assert sha(path.read_bytes()) == sha((ROOT/relative).read_bytes())
                encountered.add(relative)
    assert encountered == set(backend['source_dependency_hashes'])
    for relative, values in backend['source_dependency_hashes'].items():
        assert values['retained'] == values['current']
        pin(relative, values['retained'])
    for name, digest in backend['generated'].items():
        assert sha((build/'generated'/name).read_bytes()) == digest
    assert backend['generated']['models.json'] == proposal['old_binding']['catalogue_file_sha256']
    dependency_counts[side] = dict(commands=len(commands), dependency_files=13, unchanged_repository_dependencies=len(encountered))

# Normal compiler regeneration writes only this reviewer's owned output directory.
generate(HERE/'generated', list((ROOT/'models/research/maxwell').glob('*.json')))
for name, digest in deps['backends'][0]['generated'].items():
    pin(HERE/'generated'/name, digest)

result = dict(status='passed', scope='saved provenance only; no compiled execution or rebuild',
              broad_manifest_entries=149, changes=changes, historical_evidence_bindings_verified=historical_verified,
              backend_dependencies=dependency_counts, unchanged_archive_members=hashes,
              canonical_generation='exact saved header and catalogue bytes',
              binding=proposal['proposed_binding'], inherited_gates=proposal['inherited_gates'])
(HERE/'check-results.json').write_text(json.dumps(result, indent=2)+'\n')
(HERE/'checked-pins.json').write_text(json.dumps(dict(files=pins), indent=2)+'\n')
print(json.dumps(result, indent=2))
