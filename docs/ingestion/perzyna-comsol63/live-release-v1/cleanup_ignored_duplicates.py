"""Remove only exact archived task-owned duplicate roots, with fresh hash checks."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('roots', nargs='+')
    args = parser.parse_args()
    assert not args.receipt.exists()
    original = json.loads((HERE / 'PRIVATE-CACHE-RETENTION.json').read_text())
    index_path = args.private / 'TASK-CACHE-INDEX.json'
    assert sha(index_path.read_bytes()) == original['index_sha256']
    index = json.loads(index_path.read_text())
    archive = Path(original['archive'])
    assert sha(archive.read_bytes()) == original['archive_sha256']
    assert set(args.roots) <= set(original['roots'])
    assert len(args.roots) == len(set(args.roots))
    expected = {n: item for n, item in index['files'].items() if any(n.startswith(r + '/') for r in args.roots)}
    recovered = set()
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            if member.name in expected:
                assert member.isfile()
                data = tar.extractfile(member).read()
                assert len(data) == expected[member.name]['bytes']
                assert sha(data) == expected[member.name]['sha256']
                recovered.add(member.name)
    assert recovered == set(expected)
    actual = {}
    for name in args.roots:
        folder = ROOT / name
        assert folder.is_dir() and not folder.is_symlink()
        assert subprocess.check_output(['git', 'ls-files', '--', name], cwd=ROOT) == b''
        for path in folder.rglob('*'):
            assert not path.is_symlink()
            if path.is_file():
                rel = str(path.relative_to(ROOT))
                assert rel in expected
                data = path.read_bytes()
                assert len(data) == expected[rel]['bytes'] and sha(data) == expected[rel]['sha256']
                actual[rel] = expected[rel]
    assert actual == expected
    before = shutil.disk_usage(ROOT)
    for name in args.roots:
        folder = ROOT / name
        for path in sorted(folder.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if path.is_file():
                path.unlink()
            else:
                path.rmdir()
        folder.rmdir()
    after = shutil.disk_usage(ROOT)
    result = dict(passed=True, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  removed_roots=args.roots, verified_archive=str(archive),
                  archive_sha256=original['archive_sha256'],
                  regular_files=len(actual), duplicate_bytes_removed=sum(x['bytes'] for x in actual.values()),
                  free_before=before.free, free_after=after.free,
                  all_files_recovered_and_reverified=True, all_files_untracked=True,
                  scope='Only the explicit task-owned roots; original archive retained, no coowner or paper path touched.')
    args.receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
