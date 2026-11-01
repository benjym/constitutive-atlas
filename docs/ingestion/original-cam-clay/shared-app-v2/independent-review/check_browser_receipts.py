"""Read-only audit of retained browser exports and package identities; no engine calls."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
BROWSER = ROOT / 'output/playwright/occ-shared-app-v2'


def read(p):
    return json.loads(p.read_text())


def check():
    manifest = read(STAGE / 'package-manifest-v1.json')
    report = read(BROWSER / 'browser-results-v3.json')
    assert read(BROWSER / 'browser-process-v3.json')['returncode'] == 0
    assert not report['errors'] and not report['badResponses']
    for name, asset in report['assets'].items():
        assert asset['status'] == 200
        assert asset['sha256'] == manifest['files'][name]
    assert report['badge'] == 'Approved scope'
    assert 'fill in' in report['invalid']
    assert all(x['disabled'] for x in report['unsupported'] if x['value'] != '0')
    assert 'unsupported' in report['unsupportedReason']
    exports = {}
    for name in ['final-default-run', 'final-replayed-run', 'parameter-state-change',
                 'latest-request'] + [f'protocol-{i}' for i in range(5)]:
        d = read(BROWSER / ('v3-' + name + '.json'))
        assert d['result']['ok'] and len(d['result']['points']) == 101
        assert d['catalogue_hash'] == 'e50da3a8a40c8710bcb0446bf4b70f7accef0810ba40f90aa10dedcb5ab13f73'
        assert d['specification']['model'] == 'original-cam-clay-sw-electronic-log-recovery-v1'
        assert d['result']['catalogue_hash'] == d['catalogue_hash']
        exports[name] = d
    a, b = exports['final-default-run'], exports['final-replayed-run']
    assert a['specification'] == b['specification']
    assert a['result']['points'] == b['result']['points']
    assert all(a['result'][k] == b['result'][k] for k in a['result'] if k != 'elapsed_ms')
    assert exports['latest-request']['specification']['target'] == .004
    changed = exports['parameter-state-change']['specification']
    assert changed['parameters'][0] == 100 and changed['initial'][:3] == [90000]*3
    for i in range(5):
        s = exports[f'protocol-{i}']['specification']
        assert s['protocol'] == i and s['target'] == (10000 if i == 3 else .002)
    return {'passed': True, 'compiled_calls': 0, 'browser_asset_hash_matches': len(report['assets']),
            'successful_exports': len(exports), 'points_per_export': 101,
            'import_replay': 'all result fields exact except elapsed_ms',
            'latest_target': .004, 'parameter_and_initial_state_change_verified': True,
            'five_monotonic_protocols_verified': True, 'unsupported_cyclic_stress_disabled': True,
            'page_console_errors': report['errors'], 'http_errors': report['badResponses']}


if __name__ == '__main__':
    (HERE / 'browser-audit-v1.json').write_text(json.dumps(check(), indent=2)+'\n')
