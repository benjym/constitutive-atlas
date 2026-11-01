"""One-shot source/driver freeze. No configure, build or compiled execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DEST = Path('/private/tmp/atlas-maxwell-current-v1/source')
spec = importlib.util.spec_from_file_location('maxwell_package', ROOT/'tools/build_maxwell_laboratory.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)
assert not DEST.exists() and not (OUT/'freeze.json').exists(), 'Source freeze already exists'
before = package.source_manifest()
extras = ['tests/test_maxwell.py', 'tools/test_maxwell_wasm.mjs', 'tools/build_maxwell_laboratory.py',
          'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json',
          'docs/ingestion/maxwell-itasca900/integration-v1/check_transactions.py',
          'docs/ingestion/maxwell-itasca900/integration-v1/compare_backends_v2.py',
          'docs/ingestion/maxwell-itasca900/integration-v1/PLAN.md',
          'docs/ingestion/maxwell-itasca900/atlas-build-v1/PLAN.md',
          'docs/ingestion/maxwell-itasca900/atlas-build-v1/prepare.py']
extras += ['examples/maxwell/'+name+'.json' for name in ['relaxation', 'creep', 'oedometer', 'load-hold-reverse']]
captured = {name: (ROOT/name).read_bytes() for name in sorted(set(before['files']) | set(extras))}
for name, expected in before['files'].items():
    assert package.digest(captured[name]) == expected, name
assert package.source_manifest() == before, 'Source changed during capture'
rows, patches = [], []
for name, original in captured.items():
    data = original
    if name.endswith('/check_transactions.py'):
        old = b'/private/tmp/atlas-maxwell-execution-v1/cli'
        new = b'/private/tmp/atlas-maxwell-current-v1/cli'
        assert data.count(old) == 1
        data = data.replace(old, new)
        prior = OUT/'original-drivers/check_transactions.py'
        prior.parent.mkdir(parents=True, exist_ok=True)
        prior.write_bytes(original)
        patches.append({'path': name, 'original_sha256': package.digest(original), 'frozen_sha256': package.digest(data),
                        'change': 'Only hardcoded temporary CLI replay directory; numerical/reference behavior unchanged'})
    target = DEST/name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    rows.append({'path': name, 'sha256': package.digest(data), 'bytes': len(data)})
assert all(package.digest((DEST/row['path']).read_bytes()) == row['sha256'] for row in rows)
freeze = {'version': 'maxwell-current-source-freeze-1', 'source_root': str(DEST),
          'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'runtime_source_manifest': before, 'files': rows, 'driver_path_patches': patches,
          'compiled_calls': 0, 'build_slot': 'not claimed; prospective review required'}
(OUT/'freeze.json').write_text(json.dumps(freeze, indent=2)+'\n')
print(json.dumps({'frozen_files': len(rows), 'runtime_source_manifest_sha256': before['sha256'], 'source_root': str(DEST), 'compiled_calls': 0}))
