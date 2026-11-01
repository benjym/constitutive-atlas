"""Pure helper/early-rejection tests. No build, compiled execution or package creation."""
from pathlib import Path
import json
import tempfile
from tools import build_implicit_path_laboratory as b

HERE = Path(__file__).resolve().parent
checks = []
def test(name, fn):
    try:
        fn()
        checks.append(dict(name=name, passed=True))
    except Exception as exc:
        checks.append(dict(name=name, passed=False, error=repr(exc)))
def expect_rejection(fn, fragment):
    try:
        fn()
    except (ValueError, FileNotFoundError) as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError('Expected rejection')
valid = dict.fromkeys(b.GATES, True)
test('complete frozen gate set passes predicate', lambda: (_ for _ in ()).throw(AssertionError()) if not b.passed_gates(valid) else None)
for name in b.GATES:
    def missing(name=name):
        assert not b.passed_gates({k:v for k,v in valid.items() if k != name})
    def failed(name=name):
        assert not b.passed_gates({**valid, name:False})
    test('reject absent '+name, missing)
    test('reject failed '+name, failed)
def truthy():
    assert not b.passed_gates({**valid, b.GATES[0]:1})
    assert not b.passed_gates({**valid, 'unfrozen_gate':True})
test('truthy and extra gates cannot satisfy exact policy', truthy)
with tempfile.TemporaryDirectory(dir=HERE) as temporary:
    root = Path(temporary)
    (root/'ok').write_text('saved fixture')
    test('safe artifact resolves', lambda: b.local_file(root,'ok'))
    for name in ['../ok', '/tmp/not-qualified', 'absent']:
        test('reject unsafe or missing path '+name, lambda name=name:expect_rejection(lambda:b.local_file(root,name),'Unsafe or missing'))
    def no_e5():
        entries=json.loads((b.ROOT/'catalogue/approved-models.json').read_bytes())['models']
        assert not [m for m in entries if m.get('model_id')==b.MODEL_ID and m.get('status')=='approved'], 'E5 state changed: this retained early-rejection fixture needs a new identity'
        expect_rejection(lambda:b.bundle(root/'never-created',root/'no-build'),'Exactly one independently approved')
        assert not (root/'never-created').exists()
    test('real unapproved current model blocks before any package write', no_e5)
output=dict(scope='pure policy/path guards and real missing-E5 rejection; no build, compiled calls or valid package',passed=all(c['passed'] for c in checks),checks=checks)
(HERE/'builder-guards-results.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
assert output['passed']
