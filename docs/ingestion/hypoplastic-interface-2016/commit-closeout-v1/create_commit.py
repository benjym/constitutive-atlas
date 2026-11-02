"""Create only the frozen evidence delta on an alternate index/new local ref."""
from pathlib import Path
import hashlib, json, os, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PLAN = HERE / 'commit-plan.json'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args, data=None, env=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=data, env=env)

def main():
    plan = json.loads(PLAN.read_text())
    parent, ref = plan['parent'], plan['ref']
    head = git('rev-parse', 'HEAD').decode().strip()
    index = ROOT / '.git/index'
    old_index = sha(index.read_bytes())
    assert head == plan['root_head'] and old_index == plan['root_index_sha256']
    assert git('rev-parse', parent).decode().strip() == parent
    rows = plan['entries']
    assert len({r['path'] for r in rows}) == len(rows)
    contents = []
    for row in rows:
        p = ROOT / row['path']
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(ROOT)
        data = p.read_bytes()
        assert sha(data) == row['sha256'] and len(data) == row['bytes'], row['path']
        assert row['mode'] in ('100644', '100755')
        contents.append((row['path'], row['mode'], data))
    # The plan's own bytes are retained without a recursive hash entry.
    contents.append((str(PLAN.relative_to(ROOT)), '100644', PLAN.read_bytes()))
    if '--execute' not in sys.argv:
        print(json.dumps(dict(status='read-only preflight passed', files=len(contents), parent=parent, ref=ref)))
        return
    assert subprocess.run(['git', 'show-ref', '--verify', '--quiet', ref], cwd=ROOT).returncode == 1
    fd, alternate = tempfile.mkstemp(prefix='atlas-interface2016-evidence-index-', dir='/private/tmp')
    os.close(fd)
    os.unlink(alternate)
    env = os.environ.copy()
    env['GIT_INDEX_FILE'] = alternate
    result = dict(parent=parent, ref=ref, alternate_index=alternate,
                  plan_sha256=sha(PLAN.read_bytes()), root_head_before=head, root_index_before=old_index)
    try:
        git('read-tree', parent, env=env)
        payload = bytearray()
        for name, mode, data in contents:
            oid = git('hash-object', '-w', '--stdin', data=data, env=env).decode().strip()
            payload.extend(f'{mode} {oid}\t{name}\0'.encode())
        git('update-index', '-z', '--index-info', data=bytes(payload), env=env)
        changed = set(git('diff', '--cached', '--name-only', '-z', parent, env=env).decode().strip('\0').split('\0'))
        assert changed == {name for name, _, _ in contents}, 'Unexpected alternate-index delta'
        tree = git('write-tree', env=env).decode().strip()
        commit = git('commit-tree', tree, '-p', parent,
                     data=b'Retain independently accepted Interface2016 package and browser delivery evidence\n', env=env).decode().strip()
        assert git('rev-parse', 'HEAD').decode().strip() == head and sha(index.read_bytes()) == old_index
        git('update-ref', ref, commit, '0' * 40, env=env)
        result.update(status='local-only commit created', commit=commit, tree=tree,
                      files=len(contents), root_head_after=head, root_index_after=old_index,
                      pushed=False, deployed=False)
        os.unlink(alternate)
    except Exception as error:
        result.update(status='failed-retained', error=str(error))
        raise
    finally:
        (HERE / 'actual-commit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
