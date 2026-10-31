"""Preserve the observed saved-only TMD7 audit read closure; never run a solver.

Capture requires the original private inputs. Verify needs only the copy and its
externally retained inventory hash. This is local preservation, not relocation.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = ROOT / 'docs/benchmarks/current-kfs-tmd7-v1'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(directory, expected):
    directory = Path(directory).resolve()
    raw = (directory / 'inventory.json').read_bytes()
    require(digest(raw) == expected, 'inventory differs from retained hash')
    inventory = json.loads(raw)
    require(inventory['id'] == 'current-kfs-tmd7-private-preservation-v1', 'wrong inventory')
    seen = set()
    for item in inventory['files']:
        relative = Path(item['stored_path'])
        require(not relative.is_absolute() and '..' not in relative.parts and
                relative.parts and relative.parts[0] == 'payload', 'unsafe stored path')
        name = relative.as_posix()
        require(name not in seen, 'duplicate stored path')
        seen.add(name)
        target = directory / relative
        require(target.resolve().is_relative_to(directory) and not target.is_symlink(), 'unsafe stored file')
        require(type(item['bytes']) is int and item['bytes'] >= 0 and
                re.fullmatch('[a-f0-9]{64}', item['sha256']) is not None, 'invalid file identity')
        content = target.read_bytes()
        require(len(content) == item['bytes'] and digest(content) == item['sha256'], 'stored file changed: ' + name)
    actual = {f.relative_to(directory).as_posix() for f in directory.rglob('*') if f.is_file() or f.is_symlink()}
    require(actual == seen | {'inventory.json'}, 'missing or unlisted files')
    return inventory


def capture(destination):
    destination = Path(destination).expanduser().resolve()
    require(not destination.exists(), 'destination already exists; never overwrite evidence')
    require(not destination.is_relative_to(ROOT), 'private snapshot must be outside repository')
    policy = json.loads((PACKET / 'policy.json').read_text())
    index = json.loads((PACKET / 'private-evidence-index.json').read_text())
    roots = [('repository', ROOT), ('current', Path(index['directory']).resolve()),
             ('baseline', Path(policy['baseline_directory']).resolve())]
    artifact = Path(policy['engines']['current']['path']).resolve()
    observed = {}
    tracing = False
    busy = False

    def identity(path):
        if path == artifact:
            return 'payload/artifacts/current-atlas_solver'
        for label, root in roots:
            if path.is_relative_to(root):
                require(not path.is_relative_to(ROOT / '.git'), 'Git internals are outside preservation scope')
                return 'payload/' + label + '/' + path.relative_to(root).as_posix()
        return None  # Standard-library/interpreter/OS inputs are not archived.

    def hook(event, args):
        nonlocal busy
        if not tracing or busy:
            return
        require(event not in ('subprocess.Popen', 'os.system', 'os.exec', 'os.posix_spawn'),
                'saved-only audit attempted process execution')
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        mode, flags = args[1:3]
        require(not (isinstance(mode, str) and any(c in mode for c in 'wax+')) and
                not (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)),
                'saved-only audit attempted file mutation')
        path = Path(os.fsdecode(args[0])).resolve()
        stored = identity(path)
        if stored is None:
            return
        busy = True
        try:
            content = path.read_bytes()
            item = {'original_path': str(path), 'stored_path': stored,
                    'bytes': len(content), 'sha256': digest(content)}
            require(str(path) not in observed or observed[str(path)] == item, 'input changed during audit')
            observed[str(path)] = item
        finally:
            busy = False

    # Avoid reading pre-existing Python bytecode instead of the preserved source.
    sys.dont_write_bytecode = True
    sys.pycache_prefix = str(destination.parent / '.unused-tmd7-source-cache')
    sys.addaudithook(hook)
    old_argv = sys.argv
    output = io.StringIO()
    try:
        sys.argv = [str(PACKET / 'check_saved.py'), '--private-dir', index['directory']]
        tracing = True
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(PACKET / 'check_saved.py'), run_name='__main__')
    finally:
        tracing = False
        sys.argv = old_argv
    require(output.getvalue().startswith('PASS: complete prediction/command reconstruction;'), 'audit did not complete')
    require(observed and str(artifact) in observed, 'missing observed current artifact')
    # Retain the public declarations even if a particular audit branch did not read them.
    for path in [PACKET / 'private-evidence-index.json', PACKET / 'manifest.json']:
        content = path.read_bytes()
        observed[str(path)] = {'original_path': str(path), 'stored_path': identity(path),
                               'bytes': len(content), 'sha256': digest(content)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = destination.with_name(destination.name + '.partial-' + str(os.getpid()))
    stage.mkdir(mode=0o700)
    files = sorted(observed.values(), key=lambda item: item['stored_path'])
    for item in files:
        content = Path(item['original_path']).read_bytes()
        require(digest(content) == item['sha256'], 'source changed after audit')
        target = stage / item['stored_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(0o600)  # Executable bytes are identity evidence, not runnable copies.
    inventory = {'id': 'current-kfs-tmd7-private-preservation-v1',
                 'python': sys.version, 'source_root': str(ROOT),
                 'audit_output': output.getvalue().strip(), 'new_native_calls': 0,
                 'scope': 'Observed study files plus declarations; excludes Python/OS runtime, unvisited branches and directory metadata. Not a relocation or restore audit.',
                 'files': files}
    encoded = (json.dumps(inventory, indent=2) + '\n').encode()
    (stage / 'inventory.json').write_bytes(encoded)
    (stage / 'inventory.json').chmod(0o600)
    expected = digest(encoded)
    verify(stage, expected)
    require(not destination.exists(), 'destination appeared during capture')
    stage.rename(destination)
    return {'directory': str(destination), 'inventory_sha256': expected,
            'files': len(files), 'bytes': sum(item['bytes'] for item in files),
            'new_native_calls': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='operation', required=True)
    take = commands.add_parser('capture'); take.add_argument('directory', type=Path)
    check = commands.add_parser('verify'); check.add_argument('directory', type=Path)
    check.add_argument('--inventory-sha256', required=True)
    args = parser.parse_args()
    if args.operation == 'capture':
        print(json.dumps(capture(args.directory), indent=2))
    else:
        item = verify(args.directory, args.inventory_sha256)
        print(json.dumps({'verification': 'pass', 'files': len(item['files']), 'new_native_calls': 0}))
