"""Prepare the reviewed source commit in an alternate index and owned ref.
Default is read-only validation. Parent alone may invoke --execute after review.
Never checks out, pushes, writes the real index, or updates HEAD/main.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import tempfile

PARENT = '54f409b37deaed0ab82a85cdac9f489bc65e1309'
REF = 'refs/heads/delivery/interface2016-v1'
HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob_oid(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('/Users/bmar5496/code/constitutive-atlas'))
    parser.add_argument('--release', type=Path, default=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v2'))
    parser.add_argument('--inventory', type=Path, default=HERE/'inventory.json')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--message', default='Add source-reconciled fully rough HvWE interface model and atlas integration')
    parser.add_argument('--result', type=Path, default=HERE/'commit-result.json')
    args = parser.parse_args()
    repo, release = args.repo.resolve(), args.release.resolve()
    inventory = json.loads(args.inventory.read_text())
    assert inventory['parent'] == PARENT and inventory['owned_ref'] == REF
    def git(*words, data=None, env=None):
        return subprocess.check_output(['git', *words], cwd=repo, input=data, env=env)
    assert git('rev-parse', PARENT).decode().strip() == PARENT
    head_before = git('rev-parse', 'HEAD').decode().strip()
    index_name = Path(git('rev-parse', '--git-path', 'index').decode().strip())
    real_index = index_name if index_name.is_absolute() else repo/index_name
    index_before = sha(real_index.read_bytes()) if real_index.exists() else None
    expected = inventory['entries']
    assert expected and len({e['path'] for e in expected}) == len(expected)
    contents = []
    for entry in expected:
        relative = Path(entry['path'])
        assert not relative.is_absolute() and '..' not in relative.parts and '\n' not in entry['path'] and '\t' not in entry['path']
        path = release/relative
        assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(release), ('Missing copied isolated input', str(path))
        data = path.read_bytes()
        assert len(data) == entry['size'] and sha(data) == entry['sha256'] and blob_oid(data) == entry['git_blob_sha1'], ('Frozen source changed', entry['path'])
        assert entry['mode'] in ('100644', '100755')
        contents.append((entry, data))
    if not args.execute:
        print(json.dumps({'validated':True, 'mutation_executed':False, 'parent':PARENT, 'owned_ref':REF, 'files':len(expected), 'bytes':sum(len(data) for _,data in contents), 'real_HEAD':head_before, 'real_index_sha256':index_before}, indent=2))
        return
    # Ref creation must be additive. An existing ref requires a separately reviewed revision.
    existing = subprocess.run(['git','show-ref','--verify','--quiet',REF],cwd=repo,check=False).returncode
    assert existing == 1, 'Owned delivery ref already exists; refusing replacement'
    index_fd, index_path = tempfile.mkstemp(prefix='atlas-interface2016-source-index-', dir='/private/tmp')
    os.close(index_fd)
    os.unlink(index_path)
    env = os.environ.copy()
    env['GIT_INDEX_FILE'] = index_path
    result = {'parent':PARENT, 'ref':REF, 'alternate_index':index_path, 'files':len(expected), 'inventory_sha256':sha(args.inventory.read_bytes()), 'real_HEAD_before':head_before, 'real_index_sha256_before':index_before}
    try:
        git('read-tree', PARENT, env=env)
        payload = bytearray()
        for entry,data in contents:
            actual = git('hash-object', '-w', '--stdin', data=data, env=env).decode().strip()
            assert actual == entry['git_blob_sha1']
            payload.extend(f"{entry['mode']} {actual}\t{entry['path']}\0".encode())
        git('update-index', '-z', '--index-info', data=bytes(payload), env=env)
        staged = set(git('diff', '--cached', '--name-only', '-z', PARENT, env=env).decode().strip('\0').split('\0'))
        assert staged == {e['path'] for e in expected}, 'Alternate index contains unexpected changes'
        tree = git('write-tree', env=env).decode().strip()
        commit = git('commit-tree', tree, '-p', PARENT, data=(args.message+'\n').encode(), env=env).decode().strip()
        assert git('rev-parse', 'HEAD').decode().strip() == head_before, 'Concurrent HEAD change; own ref not installed'
        assert (sha(real_index.read_bytes()) if real_index.exists() else None) == index_before, 'Concurrent real-index change; own ref not installed'
        git('update-ref', REF, commit, '0'*40, env=env)
        result.update(status='local-owned-ref-created', tree=tree, commit=commit, real_HEAD_after=git('rev-parse','HEAD').decode().strip(), real_index_sha256_after=sha(real_index.read_bytes()) if real_index.exists() else None, pushed=False, deployed=False)
        assert result['real_HEAD_after'] == head_before and result['real_index_sha256_after'] == index_before
        args.result.write_text(json.dumps(result, indent=2)+'\n')
        os.unlink(index_path)
        print(json.dumps(result, indent=2))
    except Exception as error:
        result.update(status='failed-preserved', error=str(error))
        args.result.write_text(json.dumps(result, indent=2)+'\n')
        raise


if __name__ == '__main__':
    main()
