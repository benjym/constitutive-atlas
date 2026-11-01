"""Restore exact E5-bound implicit-path assets; never build or invent qualification."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.agent_review import validate_review, approval_entry
from tools.build_implicit_path_laboratory import bundle

MODEL = 'lade-duncan-1975-midpoint-elastic-eq19-gap-v4'
REVIEW = 'catalogue/agent-reviews/' + MODEL + '-agent-v1.json'
PACKET = 'docs/ingestion/lade-duncan-1975/atlas-integration-v1/asset-provision-v1/'
INDEX = PACKET + 'INDEX.json'
ARCHIVE = PACKET + 'compiled-assets-v1.tar.gz'
MEMBERS = frozenset(('lade-domain.mjs', 'lade-domain.wasm', 'generated/models.json',
                     'implicit-path-qualification.json', 'build-review.json'))
MAX_MEMBER = 16 * 1024 * 1024
MAX_ARCHIVE = len(MEMBERS) * MAX_MEMBER + 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_json(data):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('Duplicate JSON field: ' + key)
            value[key] = item
        return value
    def bad_constant(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=unique, parse_constant=bad_constant)


def exact_fields(value, fields):
    return isinstance(value, dict) and set(value) == set(fields)


def is_hash(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def authorized_index():
    """Check canonical current E5 and registry before directly opening archive bytes.

    validate_review itself hashes the E5 artifacts, including the pinned archive;
    that mandatory integrity read is distinct from loading/parsing its contents.
    """
    review_path = ROOT / REVIEW
    record = validate_review(review_path, root=ROOT, for_approval=True)
    if record['model']['id'] != MODEL:
        raise ValueError('Wrong implicit-path E5 model')
    expected = approval_entry(review_path, root=ROOT)
    registry = parse_json((ROOT / 'catalogue/approved-models.json').read_bytes())
    entries = [item for item in registry['models']
               if item.get('model_id') == MODEL and item.get('status') == 'approved']
    if len(entries) != 1 or entries[0] != expected:
        raise ValueError('Exact current implicit-path E5 registry entry is required')
    pins = {item['path']: item['sha256'] for item in record['artifacts']}
    if not all(name in pins and is_hash(pins[name]) for name in (INDEX, ARCHIVE)):
        raise ValueError('Canonical E5 review must explicitly pin index and archive')
    index_bytes = (ROOT / INDEX).read_bytes()
    if digest(index_bytes) != pins[INDEX]:
        raise ValueError('Changed E5-bound implicit-path asset index')
    index = parse_json(index_bytes)
    if (not exact_fields(index, ('status', 'model', 'archive', 'files'))
            or index['status'] != 'passed' or index['model'] != MODEL
            or not exact_fields(index['archive'], ('path', 'sha256'))
            or index['archive']['path'] != ARCHIVE
            or index['archive']['sha256'] != pins[ARCHIVE]
            or not exact_fields(index['files'], MEMBERS)
            or not all(is_hash(value) for value in index['files'].values())):
        raise ValueError('Invalid or unbound implicit-path asset index')
    return index, digest(index_bytes)


def selected_bytes(archive, files):
    """Read exactly five regular allowlisted members; never extract filesystem paths."""
    if not exact_fields(files, MEMBERS) or not all(is_hash(value) for value in files.values()):
        raise ValueError('Require exact five-member implicit-path hashes')
    if len(archive) > MAX_ARCHIVE:
        raise ValueError('Implicit-path compressed archive exceeds bounded size')
    # Bound decompression too, including malicious zero padding/concatenated data.
    with gzip.GzipFile(fileobj=io.BytesIO(archive)) as compressed:
        raw = compressed.read(MAX_ARCHIVE + 1)
    if len(raw) > MAX_ARCHIVE:
        raise ValueError('Implicit-path decompressed archive exceeds bounded size')
    selected = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:', ignore_zeros=True) as source:
        for member in source:
            name = member.name
            if name not in MEMBERS or name in selected:
                raise ValueError('Unexpected, unsafe or duplicate archive member: ' + name)
            if member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE) or member.pax_headers:
                raise ValueError('Archive member must be an ordinary regular file: ' + name)
            if member.size < 0 or member.size > MAX_MEMBER:
                raise ValueError('Archive member exceeds 16 MiB: ' + name)
            stream = source.extractfile(member)
            if stream is None:
                raise ValueError('Unreadable archive member: ' + name)
            data = stream.read(MAX_MEMBER + 1)
            if len(data) != member.size or digest(data) != files[name]:
                raise ValueError('Changed implicit-path archive member: ' + name)
            selected[name] = data
    if set(selected) != MEMBERS:
        raise ValueError('Missing implicit-path archive members')
    return selected


def provision(destination):
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError('Refusing to replace existing implicit-path build directory')
    index, index_hash = authorized_index()
    archive_path = ROOT / ARCHIVE
    if archive_path.stat().st_size > MAX_ARCHIVE:
        raise ValueError('Implicit-path archive exceeds bounded size')
    archive = archive_path.read_bytes()
    if digest(archive) != index['archive']['sha256']:
        raise ValueError('Changed E5-bound implicit-path compiled archive')
    selected = selected_bytes(archive, index['files'])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.implicit-path-provision-', dir=destination.parent) as temporary:
        staging = Path(temporary) / 'build'
        for name, data in selected.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        # Mandatory source/model/artifact/gates/reviewer/interface guard, no material call.
        identity = bundle(Path(temporary) / 'verification-package', staging)
        if destination.exists() or destination.is_symlink():
            raise ValueError('Destination appeared while provisioning')
        staging.rename(destination)
    return {'status': 'passed', 'model': MODEL, 'index_sha256': index_hash,
            'archive_sha256': digest(archive), 'files': {name: digest(data) for name, data in selected.items()},
            'package_identity': identity,
            'scope': 'Exact independently approved retained assets; no build, material call or new qualification'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build-implicit-path-wasm')
    args = parser.parse_args()
    print(json.dumps(provision(args.output), indent=2))
