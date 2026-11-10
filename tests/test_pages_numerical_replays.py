"""Exercise the publication cache gate without compiling or invoking a solver."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import pages_numerical_replays as replays


class PagesNumericalReplaysTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.package = Path(directory.name) / 'site'
        self.receipt = Path(directory.name) / 'pass.json'
        self.revision = 'a' * 40
        for engine, _ in replays.SUITES.values():
            base = self.package / f'engine-{engine}'
            base.mkdir(parents=True)
            (base / 'test.wasm').write_bytes(b'wasm fixture')
            self.write_identity(base, self.revision)

    @staticmethod
    def write_identity(base, revision, model='fixture'):
        identity = replays.canonical({'model': model, 'release_revision': revision})
        (base / 'identity.json').write_bytes(identity)
        (base / 'package-manifest.json').write_bytes(replays.canonical({'files': {
            f'{base.name}/identity.json': replays.sha(identity),
            f'{base.name}/test.wasm': replays.sha((base / 'test.wasm').read_bytes()),
        }}))

    def fingerprint(self, runtime='node-a', root=replays.ROOT):
        return replays.fingerprint(root, self.package, self.revision, runtime)

    def test_fresh_release_stamp_and_unrelated_ui_reuse_key(self):
        first = self.fingerprint()
        self.revision = 'b' * 40
        for engine, _ in replays.SUITES.values():
            self.write_identity(self.package / f'engine-{engine}', self.revision)
        (self.package / 'unrelated-view.mjs').write_text('different UI')
        self.assertEqual(self.fingerprint(), first)
        self.assertNotEqual(self.fingerprint(runtime='node-b'), first)

    def test_changed_engine_identity_checker_and_reference_each_change_key(self):
        first = self.fingerprint()
        base = self.package / 'engine-sls'
        (base / 'test.wasm').write_bytes(b'changed')
        self.assertNotEqual(self.fingerprint(), first)
        (base / 'test.wasm').write_bytes(b'wasm fixture')
        self.write_identity(base, self.revision, model='different model')
        self.assertNotEqual(self.fingerprint(), first)

        # Shadow one source at a time while resolving the rest from the real checkout.
        for relative in (replays.REFERENCES[0], 'tools/check_perzyna_package.mjs'):
            with self.subTest(relative=relative):
                with tempfile.TemporaryDirectory() as scratch:
                    source = Path(scratch) / 'changed'
                    source.write_bytes((replays.ROOT / relative).read_bytes() + b'\n')
                    class Override:
                        def __truediv__(self, name):
                            return source if name == relative else replays.ROOT / name

                    self.assertNotEqual(self.fingerprint(root=Override()), self.fingerprint())

    def test_stale_release_and_retired_page_fail_on_warm_package(self):
        self.write_identity(self.package / 'engine-bingham', 'b' * 40)
        with self.assertRaisesRegex(ValueError, 'wrong release revision'):
            self.fingerprint()
        self.write_identity(self.package / 'engine-bingham', self.revision)
        (self.package / 'bingham.html').touch()
        with self.assertRaisesRegex(ValueError, 'Unexpected retired package page'):
            self.fingerprint()

    def test_only_complete_success_reuses_and_a_miss_runs_all_suites(self):
        digest = self.fingerprint()
        with patch.object(replays.subprocess, 'run') as run:
            replays.replay(self.package, self.receipt, digest, self.revision)
            self.assertEqual(len(run.call_args_list), len(replays.SUITES))
            self.assertEqual(json.loads(self.receipt.read_text())['passed'], list(replays.SUITES))
            run.reset_mock()
            replays.replay(self.package, self.receipt, digest, 'b' * 40)
            run.assert_not_called()
            replays.replay(self.package, self.receipt, self.fingerprint(runtime='node-b'), self.revision)
            self.assertEqual(len(run.call_args_list), len(replays.SUITES))

    def test_corrupt_receipt_and_failed_replay_leave_no_pass(self):
        digest = self.fingerprint()
        self.receipt.write_text('{bad cache')
        with patch.object(replays.subprocess, 'run',
                          side_effect=[None, subprocess.CalledProcessError(1, 'node')]):
            with self.assertRaises(subprocess.CalledProcessError):
                replays.replay(self.package, self.receipt, digest, self.revision)
        self.assertFalse(self.receipt.exists())


if __name__ == '__main__':
    unittest.main()
