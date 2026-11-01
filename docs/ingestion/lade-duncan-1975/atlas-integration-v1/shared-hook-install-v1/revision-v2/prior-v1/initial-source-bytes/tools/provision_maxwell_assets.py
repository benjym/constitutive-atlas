"""Restore exact independently reviewed Maxwell assets; never build or invent review."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_maxwell_laboratory import bundle

PACKET = ROOT / 'docs/ingestion/maxwell-itasca900/atlas-ci-v2'
ARCHIVE_SHA256 = '2ae27721254cabed74b289c9692d0286fda71bd9eab92933d736d74904f4c9dd'
QUALIFICATION_SHA256 = '2bfe6239807e33a55e9800df831c333b21ead5ba4d1c8720c947d7a89e0080c2'
REVIEW_SHA256 = '7c240bbad74a80d1d3c754711f1b41c5d690d07d53663cd2565f2767357e31d0'
MEMBERS = {
    'wasm/maxwell.js': ('maxwell.js', 'module_sha256'),
    'wasm/maxwell.wasm': ('maxwell.wasm', 'wasm_sha256'),
    'wasm/generated/models.json': ('generated/models.json', 'catalogue_file_sha256'),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def selected_bytes(archive, binding):
    """Read only allowlisted regular files, without filesystem extraction."""
    if digest(archive.read_bytes()) != ARCHIVE_SHA256:
        raise ValueError('Changed reviewed Maxwell compiled archive')
    selected = {}
    with tarfile.open(archive, 'r:gz') as source:
        members = source.getmembers()
        names = [m.name for m in members]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive member')
        for name, (target, key) in MEMBERS.items():
            member = source.getmember(name)
            if not member.isfile() or member.size > 16 * 1024 * 1024:
                raise ValueError('Invalid selected archive member: ' + name)
            data = source.extractfile(member).read()
            if digest(data) != binding[key]:
                raise ValueError('Changed qualified artifact: ' + name)
            selected[target] = data
    return selected


def provision(destination):
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError('Refusing to replace existing Maxwell build directory')
    qualification_bytes = (PACKET/'maxwell-qualification.json').read_bytes()
    review_bytes = (PACKET/'independent-review/final-v1/build-review.json').read_bytes()
    if digest(qualification_bytes) != QUALIFICATION_SHA256 or digest(review_bytes) != REVIEW_SHA256:
        raise ValueError('Changed retained qualification or independent review')
    qualification = json.loads(qualification_bytes)
    selected = selected_bytes(PACKET/'compiled-closure-v1.tar.gz', qualification['binding'])
    selected['maxwell-qualification.json'] = qualification_bytes
    selected['build-review.json'] = review_bytes
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.maxwell-provision-', dir=destination.parent) as temporary:
        staging = Path(temporary)/'build'
        for relative, data in selected.items():
            target = staging/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        # Existing guard checks current source, generated metadata, approval,
        # actual separate review, all five gates and reviewed interface bytes.
        bundle(Path(temporary)/'verification-package', staging)
        if destination.exists() or destination.is_symlink():
            raise ValueError('Destination appeared while provisioning')
        staging.rename(destination)
    return {'status': 'passed', 'files': {p: digest(b) for p,b in selected.items()},
            'scope': 'Exact retained reviewed engine; no new compilation or qualification'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'build-maxwell-wasm')
    args = parser.parse_args()
    print(json.dumps(provision(args.output), indent=2))
