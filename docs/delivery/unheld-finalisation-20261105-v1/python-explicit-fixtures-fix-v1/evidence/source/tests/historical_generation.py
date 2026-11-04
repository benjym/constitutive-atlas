"""Exact historical inputs for byte-preservation tests, separate from live coverage.

The ledger identifies original receipt bytes and their source/model hashes. It is
never derived from the current glob during a test. Expected outputs stay frozen.
Only the historical emitter is loaded here; current DSL/validation dependencies
remain exercised, as do the current-generation tests in each feature module.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from atlas.model import ROOT, load

LEDGER = ROOT / 'tests/fixtures/historical-test-contexts.json'


def contexts():
    data = json.loads(LEDGER.read_text())
    if data['version'] != 'historical-test-contexts-1':
        raise ValueError('unknown historical test context version')
    return data


def verified(item):
    path = (ROOT / item['path']).resolve()
    if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
        raise ValueError('historical context hash mismatch: ' + item['path'])
    if 'receipt' in item:
        document = json.loads(verified(item['receipt']).read_text())
        for key in item.get('receipt_keys', [item.get('receipt_key')]):
            document = document[key]
        if document != item['sha256']:
            raise ValueError('historical source is not bound by its original receipt')
    return path


def public_paths():
    return [verified(item) for item in contexts()['models']]


def public_models():
    return [load(path) for path in public_paths()]


def catalogue(name):
    return json.loads(verified(contexts()['catalogues'][name]).read_text())


def generate(destination, paths, context):
    path = verified(contexts()['compilers'][context])
    spec = importlib.util.spec_from_file_location('atlas._historical_' + context.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate(destination, paths)


def compare_public_generation(test, directory, packet, context, previous_files):
    """Keep the original pre/post byte comparison on its original nine inputs."""
    directory = Path(directory)
    shutil.copytree(ROOT / 'atlas', directory / 'atlas', ignore=shutil.ignore_patterns('__pycache__'))
    (directory / 'models').mkdir()
    for path in public_paths():
        shutil.copyfile(path, directory / 'models' / path.name)
    (directory / 'schemas').symlink_to(ROOT / 'schemas', target_is_directory=True)
    previous = json.loads((packet / 'previous-sources.json').read_text())
    for name in previous_files:
        item = previous[name]
        source = verified({'path': item['archived_path'], 'sha256': item['sha256']})
        shutil.copyfile(source, directory / name)
    result = subprocess.run([sys.executable, '-B', '-c',
                             "from atlas.compiler import generate;generate('old-generated')"],
                            cwd=directory, env=dict(os.environ, PYTHONPATH=str(directory)),
                            capture_output=True, text=True, timeout=30)
    test.assertEqual(result.returncode, 0, result.stderr)
    models = generate(directory / 'new-generated', public_paths(), context)
    test.assertEqual(len(models), 9)
    for name in ('models.hpp', 'models.json'):
        test.assertEqual((directory / 'old-generated' / name).read_bytes(),
                         (directory / 'new-generated' / name).read_bytes(), name)
