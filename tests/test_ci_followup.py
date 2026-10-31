"""CI drift regressions: preserve numerical gates and historical identities."""
import base64
import copy
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

from atlas.model import ROOT, all_models
from atlas import source_replay
from tests import test_recorded_restarts as restart_tests
from tools.run_historical_barodesy import CAPSULE, prepare, commands

RUNTIME = ROOT / 'catalogue/source-replays/source-rates-runtime-v2'


class FollowupTests(unittest.TestCase):
    def test_runtime_metadata_separate_but_every_other_report_field_exact(self):
        compare = runpy.run_path(str(RUNTIME / 'sand-entry.py'))['compare_reports']
        expected = {'python_version': 'original interpreter', 'records': [1.25], 'admission': False}
        actual = expected | {'python_version': sys.version}
        before = copy.deepcopy((actual, expected))
        self.assertFalse(compare(actual, expected)['runtime_metadata_equal'])
        self.assertEqual((actual, expected), before)
        for change in ({'records': [1.250000000000001]}, {'extra': 0},
                       {'admission': True}, {'python_version': 'spoofed'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                compare(actual | change, expected)

    def test_original_capsule_sources_retained_in_new_identity(self):
        old = json.loads((ROOT / 'catalogue/source-replays/source-rates-v1/sand-capsule.json').read_bytes())
        new = json.loads(gzip.decompress((RUNTIME / 'sand-capsule.json.gz').read_bytes()))
        self.assertNotEqual(new['entrypoint'], old['entrypoint'])
        self.assertEqual(len(new['files']), len(old['files']) + 1)
        for name, blob in old['files'].items():
            self.assertEqual(blob, new['files'][name], name)
        self.assertEqual(base64.b64decode(new['files'][new['entrypoint']]['base64']),
                         (RUNTIME / 'sand-entry.py').read_bytes())

    def test_replay_failure_includes_interpreter_exit_and_stderr(self):
        failure = dict(expected_exit_matched=False, returncode=1, expected_exit=0,
                       python='diagnostic interpreter', stderr='exact underlying failure')
        with patch.object(source_replay, 'replay', return_value=failure):
            with self.assertRaisesRegex(ValueError, 'diagnostic interpreter.*exact underlying failure'):
                source_replay.registered(ROOT, 'catalogue/source-replays/source-rates-runtime-v2/registry.json', 'sand')

    def test_legacy_comparison_checks_current_identity_and_rejects_state_change(self):
        with gzip.open(ROOT / 'catalogue/investigations/recorded-replay-api-v1/responses.json.gz', 'rt') as f:
            expected = json.load(f)[0]['response']
        actual = copy.deepcopy(expected)
        current_hash = hashlib.sha256(json.dumps(all_models(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        actual['catalogue_hash'] = current_hash
        case = restart_tests.RestartNativeTests('runTest')
        case.assert_legacy(actual, expected)
        # JSON may encode physical values as an integer on one backend and as
        # a nearby double on another; retain the existing numerical tolerance.
        integer_expected=copy.deepcopy(expected);integer_expected['state']=[100000]*len(actual['state'])
        floating_actual=copy.deepcopy(actual);floating_actual['state']=[100000.00000000001]*len(actual['state'])
        case.assert_legacy(floating_actual,integer_expected)
        for bad in (actual | {'catalogue_hash': '0' * 64},
                    actual | {'state': [v + 100 for v in actual['state']]}):
            with self.assertRaises(AssertionError):
                case.assert_legacy(bad, expected)

    def test_historical_context_does_not_read_live_compiler_and_is_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            fixture = folder / 'fixture'
            (fixture / CAPSULE).parent.mkdir(parents=True)
            (fixture / CAPSULE).write_bytes((ROOT / CAPSULE).read_bytes())
            (fixture / 'atlas').mkdir()
            (fixture / 'atlas/compiler.py').write_text('raise RuntimeError("live source must not execute")')
            destination = folder / 'historical'
            archive, project, result = prepare(destination, fixture)
            self.assertNotIn('live source must not execute', (archive / 'atlas/compiler.py').read_text())
            self.assertFalse(result['compiled_execution'])
            self.assertFalse(result['current_engine_qualified'])
            builds = [c for c in commands(destination, archive, project) if '--build' in c]
            self.assertEqual(len(builds), 2)
            for c in builds:
                self.assertEqual(c[-4:], ['--target', 'atlas_barodesy_solver', '--parallel', '1'])
            with self.assertRaises(FileExistsError):
                prepare(destination, fixture)
            (fixture / CAPSULE).write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'capsule changed'):
                prepare(folder / 'corrupt', fixture)


if __name__ == '__main__':
    unittest.main()
