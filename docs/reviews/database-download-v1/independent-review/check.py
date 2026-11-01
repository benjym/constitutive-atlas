"""Saved-only bindings/projection verification; never builds or runs material engines."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def main():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    for name, digest in manifest['inputs'].items():
        if sha((ROOT / name).read_bytes()) != digest:
            raise ValueError('Changed review input: ' + name)
    packet = HERE.parent
    delta = json.loads((packet / 'integration-delta.json').read_text())
    for name, record in delta['files'].items():
        base = subprocess.check_output(['git', 'show', delta['base_revision'] + ':' + name], cwd=ROOT)
        if sha(base) != record['head_sha256'] or base.count(record['before'].encode()) != 1:
            raise ValueError('Changed projection base: ' + name)
        proposed = (ROOT / record['proposed_path']).read_bytes()
        if proposed != base.replace(record['before'].encode(), record['after'].encode()):
            raise ValueError('Extra projected delta: ' + name)
        if sha(proposed) != record['proposed_sha256']:
            raise ValueError('Changed projection: ' + name)
    for name, record in json.loads((packet / 'before.json').read_text()).items():
        if sha((ROOT / record['archive']).read_bytes()) != record['sha256']:
            raise ValueError('Changed before archive: ' + name)
    for name, digest in manifest['outputs'].items():
        if sha((HERE / name).read_bytes()) != digest:
            raise ValueError('Changed review output: ' + name)
    return {'status': 'PASS', 'input_bindings': len(manifest['inputs']),
            'output_bindings': len(manifest['outputs']), 'exact_projected_deltas': 2,
            'before_archives': 2, 'compiled_calls': 0}

if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True))
