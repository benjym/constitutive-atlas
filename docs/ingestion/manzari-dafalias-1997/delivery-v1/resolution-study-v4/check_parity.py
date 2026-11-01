#!/usr/bin/env python3
"""Compare saved reports only; never executes a material backend."""
import argparse
import hashlib
import json
import math
from pathlib import Path

D = Path(__file__).resolve().parent


def branch(z, parameters):
    if not isinstance(z, list) or len(z) != 14 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in z):
        return None
    p = sum(z[:3])/3
    if p <= 1e-6:
        return None
    relative = [(z[i]-(p if i < 3 else 0))/p-z[7+i] for i in range(6)]
    norm = math.sqrt(sum(x*x for x in relative))
    if norm <= 1e-10 or z[13] <= 1e-10:
        return None
    n = [x/norm for x in relative]
    matrix = [[n[0], n[3]/math.sqrt(2), n[5]/math.sqrt(2)], [n[3]/math.sqrt(2), n[1], n[4]/math.sqrt(2)], [n[5]/math.sqrt(2), n[4]/math.sqrt(2), n[2]]]
    cos = math.sqrt(6)*sum(matrix[i][j]*matrix[j][k]*matrix[k][i] for i in range(3) for j in range(3) for k in range(3))
    pat, pref, G, K, exponent, Mc, Me, lam, ec, kbc, kbe, kdc, kde, h, m, A, e0 = parameters
    psi = z[6]-ec+lam*math.log(p/pref)
    def image_ratio(c):
        return 2*c/((1+c)-(1-c)*cos)
    projection = sum(x*y for x, y in zip(z[7:13], n))
    bn = math.sqrt(2/3)*(image_ratio(Me/Mc)*Mc+image_ratio(kbe/kbc)*kbc*max(-psi, 0)-m)-projection
    draw = A*(math.sqrt(2/3)*(image_ratio(Me/Mc)*Mc+image_ratio(kde/kdc)*kdc*psi-m)-projection)
    alpha_bc = Mc+kbc*max(-psi, 0)-m
    if alpha_bc <= 1e-8 or 2*math.sqrt(2/3)*alpha_bc-abs(bn) <= 1e-8:
        return None
    if abs(psi) <= 1e-8 or abs(bn) <= 1e-8 or psi > 0 and abs(draw) <= 1e-8:
        return None
    return [psi > 0, bn > 0, draw > 0 if psi > 0 else None]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('native')
    parser.add_argument('wasm')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    plan_path = D / 'requests.json'
    assert sha(plan_path) == 'dc02829df6c1e1b3500781bb5c3c7dc6728897a64b2cd50bd56ef60d99a89d10'
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
        grid = c['coordinates'] if c['kind'] == 'chain' else c['controls'] if c['kind'] == 'controls' else [c['target']*i/c['steps'] for i in range(c['steps']+1)]
        for i, (x, y) in enumerate(zip(pa, pb)):
            prefix = name + '/' + str(i)
            # Public preset controls are generated internally; tolerate binary64
            # operation ordering there, while explicit request wires are exact.
            expected_coordinate = grid[i] if i < len(grid) else None
            coordinate_ok = all(isinstance(v, (int, float)) and math.isfinite(v) for v in (x.get('coordinate'), y.get('coordinate')))
            if coordinate_ok:
                coordinate_ok = x['coordinate'] == y['coordinate'] == expected_coordinate if c['kind'] != 'run' else max(abs(x['coordinate']-expected_coordinate), abs(y['coordinate']-expected_coordinate)) <= 1e-15
            add(prefix + '/coordinate', coordinate_ok)
            vector(prefix + '/state', x.get('state'), y.get('state'), 14)
            vector(prefix + '/strain', x.get('strain'), y.get('strain'), 6, 'strain')
        if c['group'] == 'restart':
            for backend, report, case in [('native', a, ca), ('wasm', b, cb)]:
                receipt = case.get('restart_receipt', {})
                add(name+'/'+backend+'/receipt-index', receipt.get('index') == c['restart_index'])
                original = report.get('cases', {}).get(c['compare_to'], {}).get('points', [])
                actual = case.get('points', [])
                index = c['restart_index']-1
                parent = original[index].get('state', []) if len(original) > index else []
                replay_parent = actual[index].get('state', []) if len(actual) > index else []
                vector(name+'/'+backend+'/receipt-parent', receipt.get('all_persistent_state'), parent[:13], 13)
                vector(name+'/'+backend+'/serialized-parent', receipt.get('all_persistent_state'), replay_parent[:13], 13)
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
    for backend, special in [('native', sa), ('wasm', sb)]:
        baseline = branch(special.get('linearize', {}).get('state'), plan['special']['parameters'])
        add(backend+'/AD/branch-away-boundaries', baseline is not None)
        for name in ['linearize'] + ['fd-'+str(j)+'-'+str(sign) for j in range(6) for sign in (-1, 1)]:
            diagnostics = special.get(name, {}).get('diagnostics', {})
            fractions = diagnostics.get('increment_fractions')
            valid_partition = isinstance(fractions, list) and len(fractions) > 0 and all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in fractions)
            add(backend+'/'+name+'/partition-complete', valid_partition and fractions == [1])
            if 'partition_committed' in diagnostics:
                add(backend+'/'+name+'/partition-committed', diagnostics['partition_committed'] is True)
        for j in range(6):
            for sign in (-1, 1):
                other = branch(special.get('fd-'+str(j)+'-'+str(sign), {}).get('state'), plan['special']['parameters'])
                add(backend+'/FD/branch-'+str(j)+'-'+str(sign), baseline is not None and other == baseline)
    result = {'identity': 'md1997-resolution-parity-v4', 'passed': all(c['passed'] for c in checks), 'failures': sum(not c['passed'] for c in checks), 'policy_sha256': sha(D/'parity-POLICY.md'), 'checker_sha256': sha(__file__), 'reports': [sha(args.native), sha(args.wasm)], 'checks': checks}
    out = Path(args.output)
    assert not out.exists(), 'preserve existing evidence'
    out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ('passed', 'failures')}))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
