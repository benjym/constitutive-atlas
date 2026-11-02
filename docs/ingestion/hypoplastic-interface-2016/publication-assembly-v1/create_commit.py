"""Assemble reviewed branch additions with an alternate index; never touch HEAD/main."""
from pathlib import Path
import hashlib, json, os, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(data): return hashlib.sha256(data).hexdigest()
def git(*args, data=None, env=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=data, env=env)

def main():
    plan_path = HERE/'plan.json'
    plan = json.loads(plan_path.read_text())
    published, own = plan['published'], plan['own']
    head = git('rev-parse','HEAD').decode().strip()
    index = ROOT/'.git/index'
    index_hash = sha(index.read_bytes())
    assert head == plan['root_head'] and index_hash == plan['root_index_sha256']
    contents = []
    for row in plan['entries']:
        name = row['path']
        assert not Path(name).is_absolute() and '..' not in Path(name).parts and '\n' not in name and '\t' not in name
        data = git('show', row['git_source']) if 'git_source' in row else (ROOT/row['local_source']).read_bytes()
        assert sha(data) == row['sha256'] and len(data) == row['bytes'], name
        assert row['mode'] in ('100644','100755')
        contents.append((name,row['mode'],data))
    contents.append((str(plan_path.relative_to(ROOT)),'100644',plan_path.read_bytes()))
    assert len({n for n,_,_ in contents}) == len(contents)
    if '--execute' not in sys.argv:
        print(json.dumps(dict(status='read-only assembly preflight passed', files=len(contents), parents=[published,own])))
        return
    ref = plan['ref']
    assert subprocess.run(['git','show-ref','--verify','--quiet',ref],cwd=ROOT).returncode == 1
    fd, alternate = tempfile.mkstemp(prefix='atlas-interface2016-publication-index-',dir='/private/tmp')
    os.close(fd); os.unlink(alternate)
    env = os.environ.copy(); env['GIT_INDEX_FILE'] = alternate
    result = dict(parents=[published,own],ref=ref,plan_sha256=sha(plan_path.read_bytes()),alternate_index=alternate)
    try:
        git('read-tree',published,env=env)
        payload = bytearray()
        for name,mode,data in contents:
            oid = git('hash-object','-w','--stdin',data=data,env=env).decode().strip()
            payload.extend(f'{mode} {oid}\t{name}\0'.encode())
        git('update-index','-z','--index-info',data=bytes(payload),env=env)
        changed = set(git('diff','--cached','--name-only','-z',published,env=env).decode().strip('\0').split('\0'))
        assert changed == {n for n,_,_ in contents}, 'Unexpected publication delta'
        tree = git('write-tree',env=env).decode().strip()
        commit = git('commit-tree',tree,'-p',published,'-p',own,
                     data=b'Integrate independently qualified HvWE interface while preserving published Perzyna delivery\n',env=env).decode().strip()
        assert git('rev-parse','HEAD').decode().strip() == head and sha(index.read_bytes()) == index_hash
        git('update-ref',ref,commit,'0'*40,env=env)
        result.update(status='local-only publication composition committed',commit=commit,tree=tree,files=len(contents),
                      root_head_unchanged=head,root_index_unchanged=index_hash,pushed=False,deployed=False)
        os.unlink(alternate)
    except Exception as error:
        result.update(status='failed-retained',error=str(error)); raise
    finally:
        (HERE/'actual-commit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__': main()
