"""Check actual live-browser downloads against frozen references and E7 results."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--upload-identity', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    policy = json.loads((PACKET / 'interface-v2/POLICY.json').read_text())
    cases = json.loads((PACKET / 'execution-v2/cases.json').read_text())['cases']
    identity = json.loads(args.upload_identity.read_text())
    assert identity['release_revision'] == '106a9cf8c327c9c262a97eb86aa04dae3f6cadb8'
    result = dict(passed=False, release=identity['release_revision'], comparisons=0, modes=[])
    try:
        for mode in policy['modes']:
            path = args.artifacts / (mode + '.json')
            run = json.loads(path.read_text())
            local = json.loads((PACKET / 'browser-v1/artifacts' / (mode + '.json')).read_text())
            reference = next(c for c in cases if c['id'] == 'public-' + mode)
            spec = reference['specification']
            assert run['provenance'] == identity
            assert run['controls'] == local['controls']
            assert run['request'] == local['request']
            assert run['result'] == local['result']
            assert run['result']['ok'] and len(run['result']['points']) == 6
            assert run['controls']['parameters'] == spec['parameters']
            assert run['controls']['initial'] == spec['initial']
            errors = dict(state=0., stress=0.)
            for point in run['result']['points']:
                expected = next(p for p in reference['references'] if p['time'] == point['time'])
                assert len(point['state']) == 13 and len(point['observables']) == 6
                for key, refkey, absolute in [('state', 'state', policy['accuracy']['state_absolute']),
                                             ('observables', 'stress', policy['accuracy']['stress_absolute_pa'])]:
                    for actual, want in zip(point[key], expected[refkey]):
                        error = abs(actual - want)
                        assert error <= max(absolute, policy['accuracy']['relative'] * abs(want))
                        result['comparisons'] += 1
                        kind = 'state' if key == 'state' else 'stress'
                        errors[kind] = max(errors[kind], error)
            result['modes'].append(dict(mode=mode, points=6, max_errors=errors, exact_E7_result=True,
                                       sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        assert result['comparisons'] == 342
        result['passed'] = True
    except Exception as error:
        result['error'] = repr(error)
        raise
    finally:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
