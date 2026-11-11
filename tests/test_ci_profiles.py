"""Test current qualification and the optional archival replay configuration."""
import json
from pathlib import Path
import unittest
from tools.build_ci_targets import commands
from tools.run_ci_tests import portable_suite

ROOT=Path(__file__).resolve().parents[1]


class ProfileTests(unittest.TestCase):
    def test_single_target_serial_builds_cover_native_tests_and_wasm_engines(self):
        native=commands('native');wasm=commands('wasm',True)
        for command in native+wasm:
            self.assertEqual(command[-2:],['--parallel','1'])
            self.assertEqual(command.count('--target'),1)
        native_targets={c[4] for c in native};wasm_targets={c[4] for c in wasm}
        self.assertEqual(len(native_targets),len(native))
        self.assertEqual(len(wasm_targets),len(wasm))
        self.assertTrue(wasm_targets < native_targets)
        self.assertIn('atlas_recorded_tests',native_targets)
        self.assertIn('atlas_clay2014_rate_probe',wasm_targets)

    def test_portable_projection_keeps_every_test_and_rejects_unknown_policy_ids(self):
        calls=[]
        class Example(unittest.TestCase):
            def test_current(self):calls.append('current')
            def test_exact(self):calls.append('exact')
        policy={'canonical_runner':'macos-26','canonical_python':'3.14',
                'exact_test_ids':[Example('test_exact').id()]}
        make=lambda:unittest.defaultTestLoader.loadTestsFromTestCase(Example)
        result=unittest.TestResult();portable_suite(make(),policy).run(result)
        self.assertEqual(result.testsRun,2);self.assertEqual(len(result.skipped),1)
        self.assertEqual(calls,['current'])
        for names in ([*policy['exact_test_ids'],'missing'],policy['exact_test_ids']*2):
            with self.assertRaises(ValueError):portable_suite(make(),policy|{'exact_test_ids':names})
        # Full canonical discovery is untouched and exercises the exact test.
        calls.clear();make().run(unittest.TestResult());self.assertCountEqual(calls,['current','exact'])

    def test_full_qualification_retains_both_platforms_and_replay_option(self):
        workflow=(ROOT/'.github/workflows/qualification.yml').read_text()
        for value in ['ubuntu-latest', 'macos-26', "3.14", 'atlas_recorded',
                      'explicit-gis20-occ-restart-duncan-sclay1-v6', 'run_ci_tests.py --portable',
                      'test_bingham_schedule.py', 'check_perzyna_ci.py --paired',
                      'run_historical_barodesy.py', 'schedule:', 'workflow_dispatch:',
                      'if: inputs.historical_replays', 'check_current_numerical_ci.py']:
            self.assertIn(value,workflow)
        self.assertNotIn('needs: [native, wasm, wasm-linux]',workflow)
        self.assertNotIn('actions/deploy-pages',workflow)
        self.assertFalse((ROOT/'.github/workflows/controlled-path.yml').exists())
        policy=json.loads((ROOT/'tools/ci_exact_replays.json').read_text())
        self.assertEqual(len(policy['exact_test_ids']),len(set(policy['exact_test_ids'])))

    def test_fast_checks_and_exact_artifact_publication_are_separate(self):
        fast=(ROOT/'.github/workflows/verify.yml').read_text()
        pages=' '.join((ROOT/'.github/workflows/pages.yml').read_text().split())
        self.assertIn('cancel-in-progress: true',fast)
        self.assertIn('ci_smoke.mjs',fast)
        self.assertNotIn('study.py',fast)
        self.assertNotIn('build_ci_targets.py',fast)
        self.assertIn('workflow_run:',pages)
        self.assertIn("github.event.workflow_run.event == 'push'",pages)
        self.assertIn("github.event.workflow_run.conclusion == 'success'",pages)
        self.assertIn('github.event.workflow_run.head_sha',pages)
        self.assertIn('ATLAS_PUBLICATION_REVISION',pages)
        self.assertIn('actions/upload-pages-artifact',pages)
        self.assertIn('needs: package',pages)
        self.assertNotIn('needs: qualification',pages)
        self.assertIn('test_supported_package.mjs',pages)


if __name__=='__main__':unittest.main()
