#!/usr/bin/env python3
"""Compare saved reports only; never executes a material backend."""
import argparse
import hashlib
import json
import math
from pathlib import Path

D = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('native')
    parser.add_argument('wasm')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    plan_path = D.parent / 'execution-v1/requests.json'
    assert sha(plan_path) == '2365a2d8e175a88273747da6fd7c56afa0fe9f67ffb71aa1ea13c5efbf6ac0f5'
    plan = json.loads(plan_path.read_text())
    a, b = [json.loads(Path(p).read_text()) for p in (args.native, args.wasm)]
    checks = []

    def add(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})

    def vector(name, x, y, size, kind='state'):
        valid = all(isinstance(v, list) and len(v) == size and all(isinstance(z, (int, float)) and math.isfinite(z) for z in v) for v in (x, y))
        add(name + '/shape', valid)
        if not valid:
            return
        for i, (u, v) in enumerate(zip(x, y)):
            if kind == 'state':
                tol = 1e-6 + 1e-8 * max(1, abs(u), abs(v)) if i < 6 else 1e-10 if i in (6, 13) else 1e-9
            elif kind == 'tangent':
                tol = 1e-6 + 1e-7 * max(1, abs(u), abs(v))
            else:
                tol = 1e-12
            add(name + '/' + str(i), abs(u-v) <= tol)

    ia, ib = a.get('identity', {}), b.get('identity', {})
    add('backends', ia.get('backend') == 'native' and ib.get('backend') == 'wasm')
    for key in ('model_sha256', 'requests_sha256', 'policy_sha256', 'manifest_sha256'):
        add('identity/' + key, bool(ia.get(key)) and ia.get(key) == ib.get(key))
    for c in plan['cases']:
        name = c['id']
        ca, cb = [r.get('cases', {}).get(name, {}) for r in (a, b)]
        add(name + '/success', ca.get('ok') is True and cb.get('ok') is True)
        pa, pb = ca.get('points', []), cb.get('points', [])
        expected = len(c['coordinates']) if c['kind'] == 'chain' else len(c['controls']) if c['kind'] == 'controls' else c['steps']+1
        add(name + '/point-count', len(pa) == len(pb) == expected)
        for i, (x, y) in enumerate(zip(pa, pb)):
            prefix = name + '/' + str(i)
            add(prefix + '/coordinate', x.get('coordinate') == y.get('coordinate'))
            vector(prefix + '/state', x.get('state'), y.get('state'), 14)
            vector(prefix + '/strain', x.get('strain'), y.get('strain'), 6, 'strain')
    sa, sb = a.get('special', {}), b.get('special', {})
    names = ['zero', 'hold', 'clean-valid', 'invalid-negative-pressure', 'invalid-alpha', 'invalid-nan-parameter', 'forced-rollback', 'recovery-negative-pressure', 'recovery-alpha', 'recovery-nan-parameter', 'rollback-recovery', 'linearize']
    names += ['fd-' + str(j) + '-' + str(sign) for j in range(6) for sign in (-1, 1)]
    for name in names:
        x, y = sa.get(name, {}), sb.get(name, {})
        add('special/' + name + '/decision', type(x.get('ok')) is bool and x.get('ok') == y.get('ok') and 'harness_error' not in x and 'harness_error' not in y)
        if 'state' in x or 'state' in y:
            vector('special/' + name + '/state', x.get('state'), y.get('state'), 14)
        da, db = x.get('diagnostics', {}), y.get('diagnostics', {})
        if 'increment_fractions' in da or 'increment_fractions' in db:
            add('special/' + name + '/partition', da.get('increment_fractions') == db.get('increment_fractions'))
    ta, tb = sa.get('linearize', {}).get('state_tangent'), sb.get('linearize', {}).get('state_tangent')
    valid = isinstance(ta, list) and isinstance(tb, list) and len(ta) == len(tb) == 14
    add('AD/shape', valid)
    if valid:
        for i, (x, y) in enumerate(zip(ta, tb)):
            vector('AD/' + str(i), x, y, 6, 'tangent')
    result = {'identity': 'md1997-parity-v1', 'passed': all(c['passed'] for c in checks), 'failures': sum(not c['passed'] for c in checks), 'policy_sha256': sha(D/'POLICY.md'), 'checker_sha256': sha(__file__), 'reports': [sha(args.native), sha(args.wasm)], 'checks': checks}
    out = Path(args.output)
    assert not out.exists(), 'preserve existing evidence'
    out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ('passed', 'failures')}))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
