"""Execute one exact reviewed native stage, retaining complete process evidence."""
import datetime, hashlib, json, os, pathlib, shutil, subprocess, sys
if not __debug__:
    raise RuntimeError('Python optimization is forbidden')
D = pathlib.Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
freeze = read(D/'freeze.json')
plan = read(D.parent/'native-ci-fixture-composition-v3/execution-plan.json')
source = pathlib.Path(plan['source'])
tool = read(D/'toolchain.json')
env = {**os.environ, **tool['environment'], 'PATH': tool['PATH'], 'PYTHONDONTWRITEBYTECODE': '1'}
if env['PYTHONOPTIMIZE'] != '0':
    raise RuntimeError('Python optimization policy differs')
index = int(sys.argv[1]); step = plan['steps'][index]
env.update(step['env'])
out = pathlib.Path(plan['evidence'])/'processes'/step['id']
out.mkdir(parents=True, exist_ok=False)
def verify():
    for name, h in freeze['inputs'].items():
        assert sha(pathlib.Path(name)) == h, name
    f = read(D.parent/'native-ci-fixture-composition-v3/source-freeze.json')['files']
    assert {str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()} == f
    for name, row in tool['commands'].items():
        found = shutil.which(name, path=env['PATH'])
        assert found == (row['path'] if row else None), name
        if found: assert str(pathlib.Path(found).resolve()) == row['realpath'], name
    for name, row in tool['files'].items():
        p = pathlib.Path(name)
        assert str(p.resolve()) == row['realpath'] and sha(p) == row['sha256'], name
    for name, value in tool['ambient_exact'].items():
        assert env.get(name) == value, name
    return {'source_files':len(f), 'tool_files':len(tool['files'])}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt = {'identity':'md1997-native-ci-stage-v1', 'stage':step, 'index':index, 'start':now(), 'status':'started', 'freeze_sha256':sha(D/'freeze.json')}
def save(): (out/'process.json').write_text(json.dumps(receipt,indent=2)+'\n')
save()
try:
    receipt['pre'] = verify(); save()
    with (out/'stdout').open('wb') as stdout, (out/'stderr').open('wb') as stderr:
        proc = subprocess.Popen(step['argv'], cwd=step['cwd'], env=env, stdout=stdout, stderr=stderr)
        receipt['pid']=proc.pid; save()
        receipt['returncode']=proc.wait()
    receipt['stdout_sha256']=sha(out/'stdout'); receipt['stderr_sha256']=sha(out/'stderr')
    receipt['post'] = verify(); save()
    if receipt['returncode'] != 0: raise RuntimeError('Stage returned '+str(receipt['returncode']))
    receipt['status']='passed'
except BaseException as exc:
    receipt.update(status='failed', error_type=type(exc).__name__, error=str(exc))
    raise
finally:
    receipt['end']=now(); save()
    print(json.dumps({'stage':step['id'],'status':receipt['status'],'returncode':receipt.get('returncode'),'receipt':str(out/'process.json')}),flush=True)
