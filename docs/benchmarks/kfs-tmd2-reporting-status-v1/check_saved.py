"""Verify the coordinator integration and retained evidence identities. No execution."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    integration = json.loads((HERE / 'integration.json').read_text())
    for path, expected in integration['files'].items():
        assert digest(ROOT / path) == expected, path
    for path, expected in json.loads((HERE / 'parent-inputs.json').read_text()).items():
        assert digest(ROOT / path) == expected, path
    replay = json.loads((HERE / 'parent-replays.json').read_text())
    assert replay['all_pass'] is True and len(replay['results']) == 3
    assert all(row['returncode'] == 0 for row in replay['results'])
    result = json.loads((HERE / 'parent-review-check-private.json').read_text())
    assert result['status'] == 'PASS' and result['private']['status'] == 'PASS'
    assert result['material_calls'] == result['compiled_calls'] == result['new_fits'] == 0
    review = ROOT / 'docs/benchmarks/kfs-tmd2-reporting-agent-v1'
    decision = json.loads((review / 'decision.json').read_text())
    assert decision['verdict'] == 'accept-qualified-reporting'
    assert not decision['blocking_findings_for_stated_scope']
    assert len(decision['questions']) == 6
    assert all(q['outcome'] == 'accept-with-stated-qualifications' for q in decision['questions'])
    manifest = json.loads((review / 'manifest.json').read_text())
    for path, expected in manifest['public_inputs'].items():
        assert digest(ROOT / path) == expected, path
    for path, expected in manifest['outputs'].items():
        assert digest(review / path) == expected, path
    print('PASS: exact independent review, parent saved/private replay and unchanged source/input bindings; no model or milestone admission implied.')

if __name__ == '__main__':
    main()
