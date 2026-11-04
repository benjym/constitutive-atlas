"""Frozen draft laboratory integration evidence; no scientific admission."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'catalogue/investigations'
STUDY = BASE / 'barodesy2017-preview-v2'


def assessor(study):
    spec = importlib.util.spec_from_file_location('barodesy_preview', study / 'assess.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BarodesyPreviewEvidence(unittest.TestCase):
    def test_both_frozen_studies_pass_without_scientific_promotion(self):
        for version in (1, 2):
            with self.subTest(version=version):
                study = BASE / f'barodesy2017-preview-v{version}'
                result = assessor(study).assess(study)
                self.assertTrue(result['pass'], result['errors'])
                self.assertEqual(result, json.loads((study / 'assessment.json').read_text()))
                self.assertEqual(result['requests_per_backend'], 13)
                self.assertIs(result['scientific_admission'], False)
                self.assertIs(result['deployment'], False)
                for backend in ('native', 'wasm'):
                    receipt = json.loads((study / backend / 'receipt.json').read_text())
                    codes = [c['exit_code'] for c in receipt['commands']]
                    self.assertEqual(codes, [0] * 14 + [1, 1] if backend == 'native' else [0, 0, 0])
                    self.assertIn('finished_utc', receipt)
                    for command in receipt['commands']:
                        # Build warnings are retained; runtime collection must be quiet.
                        if command['label'] not in ('configure', 'build'):
                            self.assertEqual((study / backend / (command['label'] + '.stderr.txt')).read_bytes(), b'')

    def test_browser_default_request_and_artifacts(self):
        study = STUDY / 'browser-default-v1'
        result = assessor(study).assess(study)
        self.assertTrue(result['pass'], result['errors'])
        self.assertEqual(result, json.loads((study / 'assessment.json').read_text()))
        self.assertEqual(result['points_per_backend'], 101)
        self.assertIs(result['rendered_browser_qa'], False)
        request = json.loads((study / 'request.json').read_text())
        self.assertEqual((request['protocol'], request['target'], request['steps'], request['cycles']),
                         (1, .01, 100, 0))
        receipt = json.loads((study / 'receipt.json').read_text())
        self.assertEqual([c['exit_code'] for c in receipt['commands']], [0, 0])
        for backend in ('native', 'wasm'):
            parent = json.loads((STUDY / backend / 'receipt.json').read_text())
            for name, artifact in parent['artifacts'].items():
                self.assertEqual(receipt['artifacts'][backend + '/' + name], artifact['sha256'])

    def test_same_law_and_complete_six_model_catalogue(self):
        single = BASE / 'barodesy2017-preview-v1'
        draft = json.loads((STUDY / 'models/barodesy-clay-2017.json').read_text())
        original = json.loads((ROOT / 'models/research/barodesy2017/body-zero-spin.json').read_text())
        self.assertEqual((single / 'models/barodesy-clay-2017.json').read_bytes(),
                         (STUDY / 'models/barodesy-clay-2017.json').read_bytes())
        for field in ('parameters', 'derived', 'domain', 'equations'):
            self.assertEqual(draft[field], original[field], field)
        self.assertEqual(draft['schema_version'], '0.3')
        self.assertEqual(draft['status'], 'draft')
        self.assertNotIn('integration', draft)
        self.assertEqual(draft['initialization']['default_policy'], 'examples_only')
        self.assertIn('https://doi.org/10.1007/s11440-016-0458-4', [s['url'] for s in draft['sources']])
        models = list((STUDY / 'models').glob('*.json'))
        self.assertEqual(len(models), 6)
        requests = json.loads((STUDY / 'requests.json').read_text())
        runs = [r for r in requests if r['mode'] == 'run']
        self.assertEqual({(r['protocol'], r['cycles']) for r in runs},
                         {(p, c) for p in range(5) for c in (0, 1)})

    def test_corrupt_status_volume_parity_missing_and_duplicate_reject(self):
        for mutation in ('status', 'volume', 'parity', 'missing', 'duplicate-key'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                copy = Path(temp) / 'study'
                shutil.copytree(STUDY, copy)
                journal = copy / 'wasm/journal.json'
                rows = json.loads(journal.read_text())
                if mutation == 'missing':
                    rows.pop()
                else:
                    response = json.loads(rows[1]['raw'])
                    if mutation == 'status':
                        response['ok'] = 1  # A numeric alias is not Boolean true.
                    elif mutation == 'volume':
                        response['points'][1]['state'][6] += .001
                    elif mutation == 'parity':
                        response['points'][1]['p'] += 1
                    rows[1]['raw'] = json.dumps(response)
                    if mutation == 'duplicate-key':
                        rows[1]['raw'] = '{"ok":true,' + rows[1]['raw'][1:]
                journal.write_text(json.dumps(rows))
                if mutation == 'duplicate-key':
                    with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                        assessor(STUDY).assess(copy)
                else:
                    result = assessor(STUDY).assess(copy)
                    self.assertFalse(result['pass'])
                    expected = {'status': 'status', 'volume': 'volume closure',
                                'parity': 'channel parity', 'missing': 'ordered calls'}[mutation]
                    self.assertTrue(any(expected in error for error in result['errors']), result['errors'])

    def test_changed_producer_rejects(self):
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / 'study'
            shutil.copytree(STUDY, copy)
            source = copy / 'frozen/cpp/main.cpp'
            source.write_bytes(source.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'changed frozen input'):
                assessor(STUDY).assess(copy)

    def test_isolated_compiler_regenerates_exact_combined_catalogue(self):
        code = '''import sys, pathlib
frozen=pathlib.Path(sys.argv[1]).resolve();sys.path.insert(0,str(frozen))
import atlas.compiler
assert pathlib.Path(atlas.compiler.__file__).resolve().is_relative_to(frozen)
study=pathlib.Path(sys.argv[2]);output=pathlib.Path(sys.argv[3])
atlas.compiler.generate(output, sorted((study/'models').glob('*.json')))
'''
        with tempfile.TemporaryDirectory() as temp:
            env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'ATLAS'))}
            result = subprocess.run([sys.executable, '-I', '-S', '-B', '-c', code,
                                     str(STUDY / 'frozen'), str(STUDY), temp],
                                    env=env, cwd=temp, text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, '')
            for name in ('models.hpp', 'models.json'):
                self.assertEqual((Path(temp) / name).read_bytes(), (STUDY / 'generated' / name).read_bytes())
