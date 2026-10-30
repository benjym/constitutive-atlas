"""Independent invariant checks on the verification calculations themselves."""
import importlib.util
from pathlib import Path
import unittest
import os

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('plasticity_oracle', ROOT/'tools/verify_plasticity.py')
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


class PlasticityOracleTests(unittest.TestCase):
    def test_dp_smooth_return_satisfies_yield_and_dilatancy(self):
        initial = [1e5]*3+[0, 0, 0, .7, 0]
        parameters = [1e5, 3e7, .25, 1.2, .2, 1e4]
        state, branch = oracle.dp_reference(initial, [.01, -.005, -.005, 0, 0, 0], parameters)
        self.assertEqual(branch, 'smooth-plastic')
        self.assertAlmostEqual(oracle.q_value(state)-1.2*oracle.mean(state)-1e4, 0, places=7)
        self.assertAlmostEqual(oracle.mean(state)-1e5, 2e7*.2*state[7], places=7)
        wrong = state.copy(); wrong[3] = 1000
        self.assertFalse(oracle.compare(wrong, state)[0])

    def test_dp_invalid_fixture_is_actually_outside_yield(self):
        initial = [4e5, 1e5, 1e5, 0, 0, 0, .7, 0]
        self.assertGreater(oracle.q_value(initial)-1.2*oracle.mean(initial)-1e4, 0)

    def test_mcc_isotropic_solution_consolidates_and_hardens(self):
        initial = [1e5]*3+[0, 0, 0, .7, 1e5, 0]
        state = oracle.mcc_reference(initial, [.001]*3+[0]*3, [1e5, 1.2, .2, .04, .25], 'isotropic-plastic')
        self.assertGreater(oracle.mean(state), 1e5)
        self.assertAlmostEqual(oracle.mean(state), state[7], places=7)
        self.assertLess(state[6], .7)
        self.assertGreater(state[8], 0)
        wrong = state.copy(); wrong[7] *= 1.001
        self.assertFalse(oracle.compare(wrong, state)[0])

    def test_native_dp_smooth_and_apex_returns(self):
        report = oracle.execute(Path(os.environ.get('ATLAS_SOLVER', ROOT/'build/atlas_solver')), 'drucker-prager')
        self.assertEqual(len(report['cases']), 73)
        self.assertTrue(report['passed'], [c['id'] for c in report['cases'] if not c['passed']])

    def test_scalar_root_rejects_unbracketed_inputs(self):
        with self.assertRaises(ValueError): oracle.bisect(lambda x: x+1, 0, 1)

    def test_comparison_rejects_nonfinite_and_wrong_shape(self):
        self.assertFalse(oracle.compare([float('nan')], [0])[0])
        self.assertFalse(oracle.compare([], [0])[0])


if __name__ == '__main__': unittest.main()
