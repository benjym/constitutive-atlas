"""Replay E1/E2 checks without altering historical or concurrently owned evidence."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    expected = json.loads((HERE/'verification.json').read_text())
    checked, private_unavailable = [], []
    for name, digest in expected['bindings'].items():
        path = ROOT/name
        if not path.exists() and name.startswith('.local/'):
            private_unavailable.append(name)
            continue
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
        checked.append(name)
    base = HERE.parent/'control-selection-v1'
    from atlas.model import load
    from atlas.compiler import generate
    model = load(base/'candidate-v03-v2.json')
    assert model['formulation'] == expected['formulation']
    assert model['initialization'] == expected['initialization']
    assert model['state'] == expected['state']
    assert model['parameters'] == expected['parameters']
    with tempfile.TemporaryDirectory(prefix='occ-e1-e2-check-') as tmp:
        tmp = Path(tmp)
        spec = importlib.util.spec_from_file_location('occ_constraints', base/'independent-review/check_constraints.py')
        ref = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ref)
        ref.HERE = tmp
        ref.CONTRACT = base/'CONTRACT.md'
        ref.main()
        replay = json.loads((tmp/'constraint-results.json').read_text())
        assert replay == json.loads((HERE/'constraint-results.json').read_text())
        generate(tmp/'generated', [base/'candidate-v03-v2.json'])
    result = dict(passed=True, checked_bindings=len(checked),
                  private_source_unavailable=private_unavailable,
                  decimal_cases=replay['count'], exact_saved_replay=True,
                  validated_generated_candidate=expected['candidate_hash'],
                  compiled_calls=0)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
