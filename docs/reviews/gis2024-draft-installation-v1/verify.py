"""Saved-only Stage B identities/results; no engine, build or browser execution."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from atlas.evidence import checked_receipt
P = Path(__file__).resolve().parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
load = lambda name: json.loads((P/name).read_text())


def verify():
    for name in ('installed-source-pins.json', 'package-check-freeze.json', 'outcome-pins.json'):
        for path, digest in load(name)['files'].items():
            checked_receipt(ROOT, (P/name).relative_to(ROOT), path, digest)
    plan = load('archive-plan.json')
    for ref in plan['references']:
        checked_receipt(ROOT, ref['document'], ref['original_path'], ref['sha256'])
    for path, digest in plan['original_bytes'].items():
        checked_receipt(ROOT, (P/'archive-plan.json').relative_to(ROOT), path, digest)
    before = load('pre-install-identities.json')
    for name, digest in before['existing_models'].items():
        assert sha(ROOT/'models'/name) == digest, name
    assert len(before['existing_models']) == 10
    candidate = before['candidate']
    assert candidate['sha256'] == '439b785e1da3075209c6d5ca43a991a441463a915f31f2e9c77b5c6835e20dbc'
    report = load('checks/gis-installed-package-results.json')
    assert report['stage_b_status'] == 'passed'
    assert len(report['existing_ten']) == 10
    assert {row['id'] for row in report['existing_ten']} == {n[:-5] for n in before['existing_models']}
    for row in report['existing_ten']:
        result, spec = row['result'], row['specification']
        assert result['ok'] and len(result['points']) == 101
        assert result['catalogue_hash'] == report['catalogue_hash']
        assert result['points'][0]['state'] == spec['initial']
        assert spec['target'] == .01 and spec['steps'] == 100 and spec['integration_settings']['max_depth'] == 14
        assert all(len(point['state']) == len(spec['initial']) for point in result['points'])
    named = report['named_example']
    assert named['result']['ok'] and len(named['result']['points']) == 9
    assert named['specification']['initial'] == named['result']['points'][0]['state']
    assert len(named['specification']['initial']) == 14 and len(named['specification']['parameters']) == 19
    assert named['specification']['target'] == 1e-5 and named['specification']['integration_settings']['max_depth'] == 20
    original = json.loads((ROOT/'docs/reviews/gis2024-local-draft-v1/example-proposal.json').read_text())
    assert named['specification'] == original['specification']
    failed = report['ordinary_gis_default']
    assert failed['status'] == 'failed-retained' and not failed['result']['ok']
    assert len(failed['result']['points']) == 1
    assert failed['result']['points'][0]['state'] == failed['specification']['initial']
    assert len(failed['specification']['initial']) == 14
    assert failed['specification']['target'] == .01 and failed['specification']['steps'] == 100
    assert failed['specification']['integration_settings']['max_depth'] == 14
    assert report['all_eleven_ordinary_defaults'].startswith('failed;')
    return {'scope': 'Saved-only Stage B evidence; B01–B12 browser and scientific admission remain pending.',
            'passed': True, 'existing_defaults': 10, 'named_example_points': 9,
            'ordinary_gis_default': 'failed-retained', 'builds': 0, 'browser_cases_executed': 0}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
