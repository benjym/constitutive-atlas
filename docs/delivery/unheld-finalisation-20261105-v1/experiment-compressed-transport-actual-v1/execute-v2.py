"""Coordinator: reviewed source install, standard measurement bundler, lossless checks."""
import gzip
import hashlib
import importlib.util
import json
import shutil
import sys
import tarfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = HERE.parent
REPO = N.parents[2]
SOURCE = Path('/private/tmp/atlas-baseline-delivery-20261105/source')
SITE = SOURCE.parent / 'site-compressed-v1'
PROPOSAL = N / 'experiment-compressed-transport-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    started = time.time()
    assert sha((HERE / 'plan.json').read_bytes()) == 'f6f96c47124d89c5a6075b9b052edc04ff9e35c14b1f61b01dc995924334a4b0'
    assert sha((PROPOSAL / 'manifest.json').read_bytes()) == 'f76734f7a1bf0661d25a27aadc77e9f41961b5a50dd1d9a298d1cca389b244c6'
    decision_path = N / 'experiment-compressed-transport-review-v1/decision.json'
    assert sha(decision_path.read_bytes()) == sys.argv[1]
    decision = read(decision_path)
    assert decision['status'] == 'accepted'
    assert decision['binding']['proposal_manifest_sha256'] == 'f76734f7a1bf0661d25a27aadc77e9f41961b5a50dd1d9a298d1cca389b244c6'
    for row in read(PROPOSAL / 'manifest.json')['files']:
        data = (PROPOSAL / row['path']).read_bytes()
        assert sha(data) == row['sha256'] and len(data) == row['bytes']
    delta = read(PROPOSAL / 'source-delta.json')['files']
    for row in delta:
        assert sha((SOURCE / row['path']).read_bytes()) == row['preimage_sha256']
        assert sha((PROPOSAL / row['proposal']).read_bytes()) == row['sha256']
    assert not (HERE / 'report.json').exists()
    for row in delta:
        (SOURCE / row['path']).write_bytes((PROPOSAL / row['proposal']).read_bytes())
    (HERE / 'installation.json').write_text(json.dumps({'review_sha256': sys.argv[1], 'files': delta}, indent=2) + '\n')
    sys.path.insert(0, str(SOURCE))
    spec = importlib.util.spec_from_file_location('compressed_experiment_builder', SOURCE / 'tools/build_experiments.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = module.bundle(SITE / 'experiments', root=SOURCE)
    shutil.copyfile(SOURCE / 'web/experiments.mjs', SITE / 'experiments.mjs')
    new_entries = manifest['experiments']
    assert len(new_entries) == 994
    expected = {row['path']: row for row in read(N / 'package-inventory-v1.json')['files']}
    entries = {entry['path']: entry for entry in new_entries}
    assert len(entries) == 994
    checked = []
    old_manifest = None
    with tarfile.open(REPO / '.local/retained-evidence/baseline-five-local-site-20261105-v1.tar.gz', 'r|gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.startswith('experiments/'):
                continue
            original = archive.extractfile(member).read()
            assert sha(original) == expected[member.name]['sha256']
            if member.name == 'experiments/index.json':
                old_manifest = json.loads(original)
                continue
            key = member.name.removeprefix('experiments/')
            entry = entries[key]
            assert entry['content_encoding'] == 'gzip'
            transport = entry['transport']
            assert transport['path'] == key + '.gz'
            compressed = (SITE / 'experiments' / transport['path']).read_bytes()
            assert len(compressed) == transport['size_bytes'] and sha(compressed) == transport['sha256']
            decoded = gzip.decompress(compressed)
            assert decoded == original
            assert len(decoded) == entry['size_bytes'] and sha(decoded) == entry['sha256']
            assert compressed[4:8] == b'\0\0\0\0'
            checked.append({'id': entry['id'], 'rows': entry['rows'], 'logical_bytes': len(decoded), 'logical_sha256': sha(decoded), 'transport_bytes': len(compressed), 'transport_sha256': sha(compressed)})
    assert len(checked) == 994 and old_manifest is not None
    logical_manifest = {**manifest, 'experiments': [{k: v for k, v in entry.items() if k not in ('content_encoding', 'transport')} for entry in new_entries]}
    assert logical_manifest == old_manifest
    expected_new_names = set(expected) - {'experiments/' + entry['path'] for entry in new_entries}
    expected_new_names |= {'experiments/' + entry['transport']['path'] for entry in new_entries}
    actual = []
    for path in sorted(SITE.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(SITE).as_posix()
        data = path.read_bytes()
        row = {'path': relative, 'bytes': len(data), 'sha256': sha(data)}
        if not relative.startswith('experiments/') and relative != 'experiments.mjs':
            assert row == expected[relative], relative
        actual.append(row)
    assert {row['path'] for row in actual} == expected_new_names
    size = sum(row['bytes'] for row in actual)
    assert size < 1_000_000_000
    (HERE / 'inventory.json').write_text(json.dumps({'site': str(SITE), 'files': actual}, indent=2) + '\n')
    report = {'status': 'passed-lossless-corpus-and-package-equivalence', 'review_sha256': sys.argv[1], 'experiment_records': len(checked), 'logical_metadata': 'entire original manifest unchanged after removing two transport fields', 'logical_bytes': sum(row['logical_bytes'] for row in checked), 'transport_bytes': sum(row['transport_bytes'] for row in checked), 'package_members': len(actual), 'package_bytes': size, 'other_package_assets_unchanged': len(expected) - 995 - 1, 'source_replacements': [row['path'] for row in delta], 'records': checked, 'elapsed_seconds': time.time() - started, 'scope': 'Standard measurement bundler and lossless byte checks only. Existing runtime assets retained; browser, hosted qualification and final deployment remain separate.'}
    (HERE / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'records'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        (HERE / 'failure-v2.json').write_text(json.dumps({'type': type(error).__name__, 'message': str(error)}, indent=2) + '\n')
        raise
