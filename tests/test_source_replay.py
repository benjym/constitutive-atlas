"""Registered historical source execution; no author binaries or compiler builds."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from atlas import source_replay as replay

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = 'catalogue/source-replays/transport-audit-v1.json'


class RegisteredReplay(unittest.TestCase):
    def export(self, target):
        spec = json.loads((ROOT / REGISTRY).read_bytes())
        names = {REGISTRY}
        for record in spec['replays'].values():
            names.add(record['capsule']['path'])
            names.update(p['path'] for p in record['documents'])
        for name in names:
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        return spec

    def test_export_without_git_or_current_sources_reproduces_both_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.export(root)
            # Current-source changes must not affect historical imported behavior.
            poison = root / 'tools/research_rate_observations.py'
            poison.parent.mkdir(exist_ok=True)
            poison.write_text('raise RuntimeError("current source must not execute")')
            for name, count in [('preliminary', 5), ('fixed', 0)]:
                with self.subTest(replay=name):
                    result = replay.registered(root, REGISTRY, name)
                    self.assertTrue(result['historical_output_reproduced'])
                    witnesses = json.loads(result['stdout'])['witnesses']
                    self.assertEqual(sum(x['vulnerable'] for x in witnesses), count)
            self.assertFalse((root / '.git').exists())

    def test_missing_corrupt_capsule_or_changed_original_document_rejects(self):
        for role in ('missing', 'corrupt', 'document'):
            with self.subTest(role=role), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); spec = self.export(root)
                record = spec['replays']['fixed']
                path = root / (record['documents'][0]['path'] if role == 'document' else record['capsule']['path'])
                if role == 'missing':
                    path.unlink()
                else:
                    path.write_bytes(path.read_bytes() + b' ')
                with self.assertRaises((ValueError, OSError)):
                    replay.registered(root, REGISTRY, 'fixed')

    def test_wrong_archived_source_binding_rejects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); spec = self.export(root)
            spec['replays']['fixed']['reviewed_source'] = 'atlas/__init__.py'
            (root / REGISTRY).write_text(json.dumps(spec))
            with self.assertRaises(ValueError):
                replay.registered(root, REGISTRY, 'fixed')

    def test_duplicate_json_members_reject(self):
        with self.assertRaises(ValueError):
            replay.strict_json('{"version": 1, "version": 2}')

    def test_capsule_validation_and_isolated_replay_contract(self):
        # Also exercise the independent synthetic rejection/mutation/exit cases
        # against the installed common implementation, rather than its prototype.
        import importlib.util
        path = ROOT / 'docs/reviews/frozen-source-evolution-v1/test_capsule.py'
        spec = importlib.util.spec_from_file_location('registered_capsule_checks', path)
        module = importlib.util.module_from_spec(spec)
        import sys
        from unittest.mock import patch
        with patch.dict(sys.modules, {'capsule': replay}):
            spec.loader.exec_module(module)
        result = unittest.TestResult()
        unittest.defaultTestLoader.loadTestsFromTestCase(module.Replay).run(result)
        self.assertEqual(result.testsRun, 7)
        self.assertEqual(result.errors + result.failures, [])


if __name__ == '__main__':
    unittest.main()
