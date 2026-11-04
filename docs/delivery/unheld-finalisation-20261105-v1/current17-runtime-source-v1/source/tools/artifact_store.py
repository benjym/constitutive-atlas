"""Consolidate immutable, untracked local artifacts without changing their bytes.

Plan first, then apply that exact plan. Existing paths become read-only hard links
to hash-addressed objects. Active work, tracked files and symlinks are excluded.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time

VERSION = 'local-artifact-store-0.1'
STORE = Path('.local/artifact-store')
SUFFIXES = {'.json', '.jsonl', '.csv', '.tsv', '.txt', '.log', '.pdf', '.png',
            '.jpg', '.jpeg', '.gif', '.webp', '.gz', '.zip', '.rar', '.xlsx', '.wasm', '.dat'}


def digest(path):
    sha = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(block)
    return sha.hexdigest()


def signature(path):
    s = Path(path).lstat()
    if not stat.S_ISREG(s.st_mode):
        raise ValueError(f'not a regular file: {path}')
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, stat.S_IMODE(s.st_mode)]


def contained(root, relative):
    """Reject traversal and symlinked ancestors; paths remain within this checkout."""
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('expected a repository-relative path')
    path = root / relative
    if path.resolve() != path.absolute() or not path.resolve().is_relative_to(root):
        raise ValueError(f'symlinked/escaping path: {relative}')
    return path


def tracked_paths(root):
    raw = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z'])
    return {os.fsdecode(p) for p in raw.split(b'\0') if p}


def plan(root, roots, *, minimum_bytes=65536, minimum_age_hours=2):
    root = Path(root).resolve()
    tracked = tracked_paths(root)
    cutoff = time.time_ns() - int(minimum_age_hours * 3600 * 1e9)
    stored_sizes = set()
    store = root / STORE / 'sha256'
    if store.exists():
        for path in store.glob('*/*'):
            if path.is_file() and not path.is_symlink():
                s = path.stat()
                stored_sizes.add((s.st_size, stat.S_IMODE(s.st_mode)))
    sizes = {}
    seen = set()
    for relative in roots:
        base = contained(root, relative)
        if not base.is_dir() or base.is_relative_to(root / STORE):
            raise ValueError('scan roots must be existing directories outside the object store')
        for directory, directories, files in os.walk(base, followlinks=False):
            directories[:] = [name for name in directories if name not in
                              {'.git', 'node_modules', '__pycache__', 'emscripten-cache', 'CMakeFiles'}
                              and not Path(directory, name).is_symlink()
                              and not Path(directory, name).is_relative_to(root / STORE)]
            for name in files:
                path = Path(directory, name)
                relative = path.relative_to(root).as_posix()
                if relative in seen or relative in tracked or path.suffix.lower() not in SUFFIXES:
                    continue
                seen.add(relative)
                try:
                    s = path.lstat()
                    if (not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or s.st_size < minimum_bytes
                            or s.st_mode & 0o111 or s.st_mtime_ns > cutoff or s.st_ctime_ns > cutoff):
                        continue
                    # Different read permissions remain separate, including private 0600 data.
                    mode = stat.S_IMODE(s.st_mode) & ~0o222
                    sizes.setdefault((s.st_size, mode), []).append((relative, signature(path), s.st_nlink, s.st_blocks * 512))
                except FileNotFoundError:
                    continue
    groups = []
    for (size, mode), candidates in sizes.items():
        if len({tuple(row[1][:2]) for row in candidates}) < 2 and (size, mode) not in stored_sizes:
            continue
        hashes = {}
        for relative, before, links, blocks in candidates:
            path = root / relative
            sha = digest(path)
            if signature(path) != before:
                raise RuntimeError(f'file changed during scan: {relative}')
            hashes.setdefault(sha, []).append({'path': relative, 'signature': before,
                                              'original_links': links, 'allocated_bytes': blocks})
        for sha, entries in hashes.items():
            group = {'sha256': sha, 'size': size, 'mode': mode, 'entries': entries}
            group['object_exists'] = object_path(root, group).is_file()
            if len({tuple(entry['signature'][:2]) for entry in entries}) > 1 or group['object_exists']:
                groups.append(group)
    groups.sort(key=lambda group: (-group['size'] * len(group['entries']), group['sha256']))
    return {'version': VERSION, 'root': str(root), 'created_at': time.time(),
            'minimum_bytes': minimum_bytes, 'minimum_age_hours': minimum_age_hours,
            'scan_roots': list(roots), 'groups': groups}


def object_path(root, group):
    sha = group['sha256']
    if len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
        raise ValueError('invalid SHA-256')
    mode = group['mode']
    if type(mode) is not int or mode & ~0o444 or not mode & 0o400:
        raise ValueError('invalid read-only access mode')
    return contained(root, STORE / 'sha256' / sha[:2] / f'{sha}.{mode:o}')


def copy_independent(source, destination):
    """APFS copy-on-write where available; otherwise a normal independent copy."""
    if sys.platform == 'darwin':
        library = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
        clone = library.clonefile
        clone.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        clone.restype = ctypes.c_int
        if clone(os.fsencode(source), os.fsencode(destination), 0) == 0:
            return
    shutil.copyfile(source, destination)


def apply(document, receipt_path):
    if document['version'] != VERSION:
        raise ValueError('unsupported plan')
    root = Path(document['root']).resolve()
    tracked = tracked_paths(root)
    # Complete preflight before any mutation, including all original SHA bindings.
    for group in document['groups']:
        obj = object_path(root, group)
        if obj.exists() and (digest(obj) != group['sha256'] or obj.stat().st_mode & 0o222):
            raise ValueError(f'invalid existing object: {obj}')
        for entry in group['entries']:
            path = contained(root, entry['path'])
            if entry['path'] in tracked or signature(path) != entry['signature'] or digest(path) != group['sha256']:
                raise ValueError(f'tracked or changed since plan: {entry["path"]}')
    receipt = {'version': VERSION, 'root': str(root), 'plan_sha256': hashlib.sha256(
        json.dumps(document, sort_keys=True).encode()).hexdigest(), 'entries': [], 'complete': False}
    receipt_path = Path(receipt_path)
    with receipt_path.open('x') as output:
        json.dump(receipt, output, indent=2)
    try:
        for group in document['groups']:
            obj = object_path(root, group)
            obj.parent.mkdir(parents=True, exist_ok=True)
            if not obj.exists():
                temporary = obj.with_name(obj.name + f'.{os.getpid()}.tmp')
                try:
                    copy_independent(root / group['entries'][0]['path'], temporary)
                    if digest(temporary) != group['sha256']:
                        raise ValueError('object copy hash mismatch')
                    temporary.chmod(group['mode'])
                    os.replace(temporary, obj)
                finally:
                    if temporary.exists(): temporary.unlink()
            for entry in group['entries']:
                path = contained(root, entry['path'])
                if signature(path) != entry['signature']:
                    raise ValueError(f'changed during apply: {entry["path"]}')
                descriptor, temporary_name = tempfile.mkstemp(prefix='.atlas-link-', dir=path.parent)
                os.close(descriptor)
                temporary = Path(temporary_name)
                try:
                    temporary.unlink()
                    os.link(obj, temporary)
                    if signature(path) != entry['signature']:
                        raise ValueError(f'changed before replacement: {entry["path"]}')
                    os.replace(temporary, path)
                    receipt['entries'].append({**entry, 'sha256': group['sha256'],
                                               'object': obj.relative_to(root).as_posix()})
                finally:
                    if temporary.exists(): temporary.unlink()
        receipt['complete'] = True
    finally:
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def verify(receipt):
    root = Path(receipt['root']).resolve()
    checked = set()
    for entry in receipt['entries']:
        path, obj = contained(root, entry['path']), contained(root, entry['object'])
        if not os.path.samestat(path.stat(), obj.stat()) or path.stat().st_mode & 0o222:
            raise ValueError(f'not an immutable object link: {entry["path"]}')
        if obj not in checked:
            if digest(obj) != entry['sha256']: raise ValueError('object hash mismatch')
            checked.add(obj)
    return {'complete': receipt['complete'], 'verified_paths': len(receipt['entries']), 'verified_objects': len(checked)}


def detach(root, relative):
    """Make a private writable copy before editing an archived materialization."""
    root = Path(root).resolve()
    path = contained(root, relative)
    if path.is_relative_to(root / STORE): raise ValueError('cannot detach a canonical object')
    before = signature(path)
    descriptor, name = tempfile.mkstemp(prefix='.atlas-detach-', dir=path.parent)
    os.close(descriptor)
    temporary = Path(name)
    temporary.unlink()
    try:
        copy_independent(path, temporary)
        if digest(path) != digest(temporary) or signature(path) != before:
            raise ValueError('file changed during detach')
        shutil.copystat(path, temporary)
        temporary.chmod(stat.S_IMODE(before[-1]) | 0o200)
        os.replace(temporary, path)
    finally:
        if temporary.exists(): temporary.unlink()


def summary(document):
    return {'groups': len(document['groups']), 'paths': sum(len(g['entries']) for g in document['groups']),
            'duplicate_logical_bytes': sum(g['size'] * (len(g['entries']) - (0 if g.get('object_exists') else 1))
                                           for g in document['groups'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    scan = sub.add_parser('plan'); scan.add_argument('--root', default='.')
    scan.add_argument('--scan', action='append', required=True); scan.add_argument('--output', required=True)
    scan.add_argument('--minimum-bytes', type=int, default=65536)
    scan.add_argument('--minimum-age-hours', type=float, default=2)
    run = sub.add_parser('apply'); run.add_argument('plan'); run.add_argument('--receipt', required=True)
    check = sub.add_parser('verify'); check.add_argument('receipt')
    edit = sub.add_parser('detach'); edit.add_argument('path'); edit.add_argument('--root', default='.')
    args = parser.parse_args()
    if args.command == 'plan':
        document = plan(args.root, args.scan, minimum_bytes=args.minimum_bytes, minimum_age_hours=args.minimum_age_hours)
        with Path(args.output).open('x') as stream: json.dump(document, stream, indent=2)
        print(json.dumps(summary(document)))
    elif args.command == 'apply': print(json.dumps(verify(apply(json.loads(Path(args.plan).read_text()), args.receipt))))
    elif args.command == 'verify': print(json.dumps(verify(json.loads(Path(args.receipt).read_text()))))
    else: detach(args.root, args.path); print(args.path)


if __name__ == '__main__': main()
