import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib, json, subprocess, copy, ast
R = Path(__file__).resolve().parent
D = R.parent / 'native-ci-dispatch-plan-v2'
ROOT = R.parents[3]
sha = lambda b: hashlib.sha256(b).hexdigest()
checks = []
def check(name, condition):
    assert condition, name
    checks.append(name)
manifest = json.loads((D/'manifest.json').read_text())
check('manifest identity', sha((D/'manifest.json').read_bytes()) == '27325aae9a3f5f0d2ea7c4b7cc30ff6ccf80cd5ac454f14bbc234e14bfeb8710')
check('exact inventory', {str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()} == set(manifest)|{'manifest.json'})
for name, digest in manifest.items():
    check('packet '+name, sha((D/name).read_bytes()) == digest)
inputs = json.loads((D/'inputs.json').read_text())
for name, entry in inputs['published_snapshots'].items():
    result = subprocess.run(['git','show',entry['git_source']], cwd=ROOT, capture_output=True, check=True)
    check('git snapshot '+name, result.stdout == (D/name).read_bytes())
for name, digest in inputs['repository_dependencies'].items():
    check('dependency '+name, sha((ROOT/name).read_bytes()) == digest)
# Execute author pure mock suite with only its final evidence write redirected;
# forbid all subprocess calls throughout imported helper/mocks.
code = ast.parse((D/'check_prospective.py').read_text())
captured = {}
original_write = Path.write_text
original_run, original_popen = subprocess.run, subprocess.Popen
def capture(path, value, *args, **kwargs):
    assert path == D/'static-checks.json'
    captured['report'] = json.loads(value)
    return len(value)
def forbidden(*args, **kwargs):
    raise AssertionError('Live process prohibited during pure suite')
namespace = {'__file__':str(D/'check_prospective.py'),'__name__':'independent_mock_replay'}
try:
    Path.write_text = capture
    subprocess.run = subprocess.Popen = forbidden
    exec(compile(code, str(D/'check_prospective.py'), 'exec'), namespace)
finally:
    Path.write_text = original_write
    subprocess.run, subprocess.Popen = original_run, original_popen
check('saved mock report exact', captured['report'] == json.loads((D/'static-checks.json').read_text()))
def reject(name, fn):
    try: fn()
    except (AssertionError, ValueError, KeyError, TypeError): checks.append(name); return
    raise AssertionError('Accepted adversary '+name)
for size in [14,15,16]:
    b=namespace['catalogue'](size)
    check('independent catalogue '+str(size),namespace['classify'](b,namespace['source_hashes'])==str(size))
    for field in ['parameters','state']:
        bad=copy.deepcopy(b);bad['models'][0][field]={}
        reject(f'full object {size} {field}',lambda:namespace['classify'](bad,namespace['source_hashes']))
for index in range(8):
    for field, value in [('returncode',0),('stdout','extra\n'),('stderr',''),('timeout',True),('argv',[])]:
        rows=namespace['process_rows']();rows[index][field]=value
        reject(f'contract {index} {field}',lambda:namespace['verify_rows'](rows))
    for field in ['native_selector','numerical_selector']:
        rows=namespace['process_rows']();rows[index][field]='poison'
        reject(f'contract {index} {field}',lambda:namespace['verify_rows'](rows))
before=len(namespace['spy'])
bad=namespace['catalogue'](16);bad['models'][0]['parameters']={}
reject('no object mutation delegated',lambda:namespace['projected'](bad,namespace['source_hashes']))
check('spy unchanged after invalid generated object',len(namespace['spy'])==before)
for size in [14,15,16]:
    for suite in ['macos-main','linux-main','recorded']:
        env=namespace['env_for'](size,suite)
        check(f'env selectors {size} {suite}',env['ATLAS_NATIVE_FIXTURES']=='explicit-gis20-occ-restart-duncan-v5' and (env.get('ATLAS_NUMERICAL_FIXTURES')=='md1997-source-admissible-v1' if size==16 and suite!='recorded' else 'ATLAS_NUMERICAL_FIXTURES' not in env))
proof=json.loads((D/'workflow-diff-proof.json').read_text())
check('no failed CTest hiding',all(x not in proof['proposed_block'] for x in ['continue-on-error','|| true','--exclude-regex','-E ']))
# Exact filters are frozen in policy; implementation must generate these argv,
# not accept arbitrary caller filters. Workflow only delegates named suites.
check('separate recorded calls',proof['proposed_block'].count('--suite recorded')==2)
check('artifact preservation always',"if: always()" in proof['proposed_block'])
check('manifest unchanged after review',all(sha((D/n).read_bytes())==h for n,h in manifest.items()))
(R/'checks.json').write_text(json.dumps({'status':'passed','independent_checks':len(checks),'checks':checks,'author_mock_checks':captured['report']['count'],'compiled_calls':0,'live_material_processes':0},indent=2)+'\n')
print(json.dumps({'independent_checks':len(checks),'author_mock_checks':captured['report']['count'],'status':'passed'}))
