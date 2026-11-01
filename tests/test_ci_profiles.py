"""Keep archival gates required while testing the portable projection separately."""
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

    def test_both_platforms_and_archival_checks_gate_deployment(self):
        workflow=(ROOT/'.github/workflows/verify.yml').read_text()
        self.assertIn('os: ubuntu-latest',workflow)
        self.assertIn('os: macos-26',workflow)
        self.assertIn("python: '3.14'",workflow)
        self.assertIn("if: runner.os == 'macOS'\n        run: |\n          ctest --test-dir build --output-on-failure -E \"^atlas_recorded$\"",workflow)
        self.assertIn('ATLAS_NATIVE_FIXTURES=explicit-gis20-occ-restart-v4 ctest --test-dir build --output-on-failure -R "^atlas_recorded$"',workflow)
        self.assertIn('ATLAS_NATIVE_FIXTURES: explicit-gis20-occ-v3',workflow)
        self.assertIn('needs: [native, wasm, wasm-linux]',workflow)
        self.assertIn('PYTHONDONTWRITEBYTECODE: "1"',workflow)
        policy=json.loads((ROOT/'tools/ci_exact_replays.json').read_text())
        self.assertEqual(len(policy['exact_test_ids']),len(set(policy['exact_test_ids'])))


if __name__=='__main__':unittest.main()
