"""Check historical input integrity and generate the current catalogue."""
import ast
import copy
import json
from pathlib import Path
import tempfile
import unittest

from atlas.compiler import generate
from atlas.model import ROOT, all_models
from atlas.stress import stress_scope
from tests.historical_generation_v03 import contexts, public_models, public_paths, verified

P = ROOT / 'docs/reviews/historical-test-context-v1'


class HistoricalGenerationTests(unittest.TestCase):
    def test_all_pinned_inputs_and_original_expected_artifacts_are_intact(self):
        data = contexts()
        for item in (data['models'] + list(data['compilers'].values()) +
                     list(data['catalogues'].values()) + data['expected_artifacts']):
            verified(item)
        self.assertEqual(len(public_paths()), 9)
        self.assertEqual(len({m['id'] for m in public_models()}), 9)
        self.assertTrue(all(stress_scope(m) == 'effective' for m in public_models()))

    def test_corrupt_or_unbound_context_is_rejected(self):
        item = copy.deepcopy(contexts()['models'][0])
        for mutation in ('source', 'receipt', 'binding', 'escape'):
            bad = copy.deepcopy(item)
            if mutation == 'source':bad['sha256'] = '0' * 64
            elif mutation == 'receipt':bad['receipt']['sha256'] = '0' * 64
            elif mutation == 'binding':bad['receipt_key'] = 'absent-model.json'
            else:bad['path'] = '../outside.json'
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, KeyError)):
                verified(bad)

    def test_current_generation_contains_every_live_definition_and_scope(self):
        models = all_models()
        expected_scope_counts = {
            scope: sum(stress_scope(model) == scope for model in models)
            for scope in ('total', 'effective')
        }
        with tempfile.TemporaryDirectory() as directory:
            emitted = generate(directory)
            metadata = json.loads((Path(directory) / 'models.json').read_text())
            self.assertEqual({m['id'] for m in emitted}, {m['id'] for m in models})
            self.assertEqual({m['id']: m for m in metadata['models']}, {m['id']: m for m in models})
            header = (Path(directory) / 'models.hpp').read_text()
            for scope, count in expected_scope_counts.items():
                self.assertEqual(header.count(f',StressScope::{scope}'), count)

    def test_original_methods_and_unmodified_gates_are_retained(self):
        failures = json.loads((P / 'original-failures.json').read_text())
        archive = json.loads((P / 'archive-result.json').read_text())
        allowed = {(row['file'], row['class'], row['method']) for row in failures['tests']}
        self.assertEqual(len(allowed), 20)
        sources = {Path(path).name: ROOT / path for path in archive['created_snapshots']
                   if '/tests/test_' in path}
        def methods(text):
            return {(cls.name, method.name): ast.dump(method, include_attributes=False)
                    for cls in ast.parse(text).body if isinstance(cls, ast.ClassDef)
                    for method in cls.body if isinstance(method, ast.FunctionDef)}
        for file in failures['original_test_files']:
            old = methods(sources[Path(file).name].read_text())
            new = methods((ROOT / file).read_text())
            self.assertEqual(set(old), set(new), file)
            for (cls, method), tree in old.items():
                if (file, cls, method) not in allowed:
                    self.assertEqual(tree, new[(cls, method)], (file, cls, method))


if __name__ == '__main__':unittest.main()
