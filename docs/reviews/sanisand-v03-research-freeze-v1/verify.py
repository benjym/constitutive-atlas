"""Saved evidence integrity plus normal validation; no build or integration."""
import json
from prepare import HERE, ROOT, digest, validate_inputs

if __name__ == '__main__':
    manifest = json.loads((HERE / 'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        if digest(HERE / name) != expected:
            raise ValueError('packet mismatch: ' + name)
    actual = validate_inputs()
    saved = json.loads((HERE / 'preflight.json').read_text())
    for key, value in actual.items():
        assert saved[key] == value, key
    print(json.dumps({'ok': True, 'packet_files': len(manifest['files']),
                      'requests': actual['requests_checked'],
                      'initialization_accepts': actual['initialization_calls_accepted'],
                      'initialization_rejects': len(actual['initializer_rejections']),
                      'candidate_integrations': 0, 'compiled_builds': 0}, indent=2))
