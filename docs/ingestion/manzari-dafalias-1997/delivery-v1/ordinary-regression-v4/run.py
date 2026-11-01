#!/usr/bin/env python3
"""Run the complete frozen ordinary-default policy using generic APIs only."""
import argparse
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path

D = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--solver')
    group.add_argument('--wasm-engine')
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    for name, digest in json.loads((D/'manifest.json').read_text()).items():
        assert sha(D/name) == digest, 'frozen input mismatch: '+name
    policy_file = D.parent/'ordinary-regression-policy-v2.json'
    policy = json.loads(policy_file.read_text())
    source_receipt = D.parent/'source-freeze-v2.json'
    assert sha(source_receipt) == policy['source_freeze_sha256']
    source = json.loads(source_receipt.read_text())
    for name, digest in source['source_files'].items():
        assert sha(Path(source['source_directory'])/name) == digest, 'source drift: '+name
    module_spec = importlib.util.spec_from_file_location('generic_request_transport', D.parent/'execution-v2/run_native.py')
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    backend = module.Backend(args, out)
    report = {'identity': 'md1997-ordinary-regression-v4', 'backend': 'wasm' if args.wasm_engine else 'native', 'artifact_sha256': sha(args.wasm_engine or args.solver), 'policy_sha256': sha(policy_file), 'manifest_sha256': sha(D/'manifest.json'), 'cases': []}
    try:
        for c in policy['cases']:
            request = {'mode': 'run', 'model': c['model'], 'parameters': c['parameters'], 'initial': c['initial'], 'settings': c['integration_settings'], 'protocol': c['protocol'], 'target': c['target'], 'steps': c['steps'], 'cycles': c['cycles']}
            print('RUN '+report['backend']+' '+c['model'], flush=True)
            with gzip.open(out/(c['model']+'.jsonl.gz'), 'wt', encoding='utf-8') as log:
                response = backend.call(request, log)
            points = response.get('points', [])
            checks = {'decision': type(response.get('ok')) is bool and response['ok'] == c['expected_ok'], 'no_transport_error': 'harness_error' not in response}
            if c['expected_ok']:
                checks['all_points'] = isinstance(points, list) and len(points) == c['steps']+1
                if isinstance(points, list):
                    for i, point in enumerate(points):
                        for key, size in [('state', len(c['initial'])), ('strain', 6)]:
                            v = point.get(key)
                            checks[key+'/'+str(i)] = isinstance(v, list) and len(v) == size and all(isinstance(x, (int, float)) and math.isfinite(x) for x in v)
                        coordinate = point.get('control')
                        checks['control/'+str(i)] = isinstance(coordinate, (int, float)) and math.isfinite(coordinate) and abs(coordinate-c['target']*i/c['steps']) <= 1e-15
            else:
                expected = c['declared_failure']
                checks['exact_failure_message'] = response.get('message') == expected['message']
                checks['retained_committed_points'] = isinstance(points, list) and len(points) == expected['points']
                if isinstance(points, list) and len(points) == 1:
                    point = points[0]
                    checks['retained_initial_state'] = point.get('state') == c['initial']
                    checks['retained_zero_strain'] = point.get('strain') == [0.]*6
                    checks['retained_zero_control'] = point.get('control') == 0
                    checks['retained_finite_state'] = isinstance(point.get('state'), list) and len(point['state']) == len(c['initial']) and all(isinstance(v, (int, float)) and math.isfinite(v) for v in point['state'])
            report['cases'].append({'model': c['model'], 'passed': all(checks.values()), 'checks': checks, 'response': response})
            (out/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    finally:
        backend.close()
        report['passed'] = len(report['cases']) == len(policy['cases']) and all(c['passed'] for c in report['cases'])
        (out/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
