"""Score a complete saved calibration candidate after checking allocation metadata."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.study_objective import score_objective, validate_objective
from tools.strict_observation_json import loads


def check(policy, allocation, reservations, observations, predictions):
    allocation_bytes = Path(allocation).read_bytes()
    reservation_bytes = Path(reservations).read_bytes()
    policy_bytes = Path(policy).read_bytes()
    plan, reserve, objective = map(loads, (allocation_bytes, reservation_bytes, policy_bytes))
    hashes = {'allocation_sha256': hashlib.sha256(allocation_bytes).hexdigest(),
              'reservation_sha256': hashlib.sha256(reservation_bytes).hexdigest()}
    validate_objective(objective, plan, reserve, **hashes)
    # No response bytes are opened until both metadata contracts pass.
    observation_bytes = Path(observations).read_bytes()
    prediction_bytes = Path(predictions).read_bytes()
    observed = loads(observation_bytes)
    predicted = loads(prediction_bytes)
    result = score_objective(objective, plan, reserve, observed, predicted, **hashes)
    result['input_sha256'] = {name: hashlib.sha256(content).hexdigest() for name, content in
                             [('objective', policy_bytes), ('allocation', allocation_bytes),
                              ('reservations', reservation_bytes), ('observations', observation_bytes),
                              ('predictions', prediction_bytes)]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('policy', 'allocation', 'reservations', 'observations', 'predictions'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = check(args.policy, args.allocation, args.reservations,
                       args.observations, args.predictions)
        content = json.dumps(report, indent=2, allow_nan=False) + '\n'
        if args.output:
            with args.output.open('x') as stream:
                stream.write(content)
        print(content, end='')
        return 0
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as exc:
        print('Invalid complete candidate: ' + str(exc), file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
