#!/usr/bin/env python3
"""Strict saved-report verifier; no compiled calls or constitutive update kernel."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

D = Path(__file__).resolve().parent
REQUEST_HASH = 'efa5403f19c6013ddc1ecb6de17c89caf9a2cc102ae7df94dc4a080784c28302'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def strict(text):
    value = json.loads(text, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    json.dumps(value, allow_nan=False)
    return value


def finite(values, n):
    return isinstance(values, list) and len(values) == n and all(type(v) in (int, float) and math.isfinite(v) for v in values)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('native', type=Path)
    ap.add_argument('wasm', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    request_path = D.parent/'requests.json'
    assert sha(request_path) == REQUEST_HASH
    plan = strict(request_path.read_text())
    by_id = {c['id']: c for c in plan['cases']}
    execution = plan['cases'] + [by_id[name] for pair in plan['recovery_pairs'] for name in pair]
    checks, reports = [], []

    def add(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})

    for backend, path in [('native', args.native), ('wasm', args.wasm)]:
        try:
            report = strict(path.read_text())
            assert isinstance(report, dict)
        except Exception as error:
            add(backend+'/parse/'+str(error), False)
            reports.append({})
            continue
        reports.append(report)
        add(backend+'/status', report.get('status') == 'passed')
        add(backend+'/label', report.get('backend') == backend)
        add(backend+'/plan', report.get('request_sha256') == REQUEST_HASH)
        artifact = Path(report.get('engine_path', ''))
        add(backend+'/artifact', artifact.is_file() and sha(artifact) == report.get('engine_sha256'))
        rows = report.get('rows', [])
        add(backend+'/complete-count', isinstance(rows, list) and len(rows) == len(execution) == 19)
        if not isinstance(rows, list):
            continue
        previous = None
        for i, original in enumerate(execution):
            prefix = backend+'/'+str(i)+'/'+original['id']
            if i >= len(rows) or not isinstance(rows[i], dict):
                add(prefix+'/missing', False)
                continue
            row, expected_request = rows[i], copy.deepcopy(original)
            if original['id'] in ('unload', 'reload', 'hold'):
                valid = isinstance(previous, dict) and previous.get('ok') is True and finite(previous.get('state'), 8)
                add(prefix+'/chain-parent', valid)
                if not valid:
                    continue
                expected_request['initial'] = previous['state']
            add(prefix+'/exact-request', row.get('request') == expected_request)
            try:
                response = strict(row['stdout'])
                assert isinstance(response, dict)
                add(prefix+'/raw-response', response == row.get('response'))
                if backend == 'wasm':
                    wire = strict(row['wire'])
                    add(prefix+'/wire', wire.get('raw') == row['stdout'] and 'error' not in wire)
                else:
                    csv = lambda v: ','.join(format(x, '.17g') for x in v)
                    command = [str(artifact.resolve()), '--mode', 'integrate', '--model', expected_request['model'], '--parameters', csv(expected_request['parameters']), '--initial', csv(expected_request['initial']), '--strain', csv(expected_request['strain']), '--integration-settings', csv(expected_request['integration_settings'])]
                    add(prefix+'/argv', row.get('command') == command)
            except Exception as error:
                add(prefix+'/raw-parse/'+str(error), False)
                previous = None
                continue
            previous = response
            for name in ('model', 'parameters', 'initial', 'strain'):
                add(prefix+'/echo-'+name, response.get(name) == expected_request[name])
            settings = response.get('integration_settings', {})
            if not isinstance(settings, dict):
                settings = {}
            keys = ('residual_tolerance', 'rate_tolerance', 'max_iterations', 'max_depth', 'max_substeps', 'max_backtracks')
            add(prefix+'/settings', [settings.get(k) for k in keys] == expected_request['integration_settings'])
            z = response.get('state')
            add(prefix+'/complete-finite-state', finite(z, 8))
            wanted = expected_request['expected']['ok']
            add(prefix+'/decision', type(response.get('ok')) is bool and response['ok'] == wanted)
            K, Y, cap = expected_request['parameters']
            initial = expected_request['initial']
            pn = sum(initial[:3])/3
            trial = pn+K*sum(expected_request['strain'][:3])
            p = min(trial, Y)
            gamma = max((trial-Y)/K, 0)
            analytic_success = pn > 0 and p > 0 and p <= cap and original['id'] != 'budget-failure'
            add(prefix+'/analytical-decision', wanted == analytic_success)
            diagnostics = response.get('diagnostics', {})
            if not isinstance(diagnostics, dict):
                diagnostics = {}
            add(prefix+'/commit', diagnostics.get('partition_committed') is wanted)
            if wanted:
                add(prefix+'/single-partition', diagnostics.get('increment_fractions') == [1])
                expected = [p]*3+[0]*3+[initial[6]+gamma, gamma]
                add(prefix+'/analytic-state', finite(z, 8) and all(abs(v-w) <= (1e-8 if j < 6 else 1e-10) for j, (v, w) in enumerate(zip(z, expected))))
                if finite(z, 8):
                    pressure = sum(z[:3])/3
                    add(prefix+'/physical', pressure > 0 and pressure <= cap and (pressure-Y)/K <= 1e-10 and z[7] >= -1e-12)
            else:
                add(prefix+'/exact-rollback', z == initial)
    na, wa = [r.get('rows', []) for r in reports]
    if isinstance(na, list) and isinstance(wa, list):
        for i, (a, b) in enumerate(zip(na, wa)):
            ar = a.get('response') if isinstance(a, dict) else None
            br = b.get('response') if isinstance(b, dict) else None
            x = ar.get('state') if isinstance(ar, dict) else None
            y = br.get('state') if isinstance(br, dict) else None
            add('parity/'+str(i), finite(x, 8) and finite(y, 8) and all(abs(u-v) <= 1e-10 for u, v in zip(x, y)))
    result = {'identity': 'predictor-constraint-fixture-integrity-v2', 'passed': all(c['passed'] for c in checks), 'failures': sum(not c['passed'] for c in checks), 'request_sha256': REQUEST_HASH, 'checker_sha256': sha(__file__), 'policy_sha256': sha(D/'FIXTURE-CHECK-POLICY-v2.md'), 'checks': checks}
    assert not args.output.exists()
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ('passed', 'failures')}))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
