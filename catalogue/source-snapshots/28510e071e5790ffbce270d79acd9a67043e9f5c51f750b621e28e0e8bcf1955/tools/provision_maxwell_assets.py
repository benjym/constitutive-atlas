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

PACKET = ROOT / 'docs/ingestion/maxwell-itasca900/atlas-build-v1'
ARCHIVE_SHA256 = '7595c20b97502e1f15354c07f4fcd7e54ef6f956283038330895934d9f02fd52'
QUALIFICATION_SHA256 = 'd989230df995a154ec721769bef3afd5d5347bc40d652af95229cdb5dab9433c'
REVIEW_SHA256 = '0fb88a7954f1f87682b8ee64b6e8538710c3b36ad359708431023aa550097914'
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
