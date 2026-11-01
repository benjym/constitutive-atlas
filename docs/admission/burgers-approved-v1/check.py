"""Check bounded approval identities without material execution."""
import copy
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(record):
    assert record['status'] == 'approved'
    assert record['approval_authority']['kind'] == 'explicit-user-instruction'
    assert record['approval_authority']['instruction'] == "Ok my approval granted, let's add it"
    assert record['review']['human_scientific_signature'] is False
    assert record['experimental_validation'] == 'not_assessed'
    assert record['deployment_authorized'] is False
    d = record['definition']
    assert d['sha256'] == '1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c'
    assert digest(ROOT / d['path']) == d['sha256']
    m = json.loads((ROOT / d['path']).read_text())
    assert m['id'] == record['model_id'] and m['status'] == 'draft'
    s, f = record['scope'], m['formulation']
    for key, expected in [('kinematics','small_strain_3d'),('frame','fixed_spatial'),('objective_rate','none')]:
        assert s[key] == f[key] == expected
    assert s['stress_scope'] == f['stress']['scope'] == 'total'
    assert s['material_assumption'] == 'dry uncoupled material point'
    assert s['interfaces'] == ['native physical-time CLI','Wasm physical-time ABI','ordered timed strain/stress schedules']
    assert len(record['retained_findings']) == 2 and len(record['limitations']) == 6
    for item in record['supporting_files']:
        assert digest(ROOT / item['path']) == item['sha256']
    for path in s['examples'] + [record['dossier'], s['qualification_requests'], s['qualification_policy']]:
        assert (ROOT / path).is_file()

record = json.loads((BASE / 'approval.json').read_text())
validate(record)
registry = json.loads((ROOT / 'catalogue/approved-models.json').read_text())
assert [r for r in registry['models'] if r['model_id'] == record['model_id']] == [record]
counts = {}
for path, key in [('docs/ingestion/burgers-itasca900/manifest.json','packet_files'), ('docs/ingestion/burgers-itasca900/integration-v1/manifest.json','files'), ('docs/reviews/burgers-scientific-v1/manifest.json','files')]:
    p = ROOT / path
    manifest = json.loads(p.read_text())
    for name, sha in manifest[key].items():
        assert digest(p.parent / name) == sha
    counts[path] = len(manifest[key])
retention = json.loads((BASE / 'source-retention.json').read_text())
assert len(retention['sources']) == 3
for source in retention['sources']:
    assert digest(Path(source['durable_private_path'])) == source['sha256']
rejected = []
for label, mutate in [
    ('stale model', lambda r: r['definition'].update(sha256='0'*64)),
    ('fabricated signature', lambda r: r['review'].update(human_scientific_signature=True)),
    ('widened rotation scope', lambda r: r['scope'].update(objective_rate='jaumann')),
    ('altered evidence', lambda r: r['supporting_files'][0].update(sha256='0'*64)),
    ('unsupported browser interface', lambda r: r['scope']['interfaces'].append('browser timed controls')),
]:
    bad = copy.deepcopy(record)
    mutate(bad)
    try:
        validate(bad)
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError('Accepted corruption: ' + label)
result = dict(passed=True, approval=record['id'], model_sha256=record['definition']['sha256'], retained_manifest_bindings=counts, private_sources_verified=3, manufactured_corruptions_rejected=rejected, model_bytes_changed=False, compiled_calls=0, human_signature_inferred=False, experimental_validation='not_assessed')
(BASE / 'checks.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
