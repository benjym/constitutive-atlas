import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, read_json
from analysis.hca_normalization import change_void_reference, history_increment, rates, reference_scale


class HCAVoidReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        record = read_json(ROOT/'paper/study/source_formulations/hca-sand-2005.json')
        table = next(t for t in record['information_audit']['tables'] if t['table'] == '2')
        cls.parameters = {entry['symbol']: entry['value'] for entry in table['entries']}

    def assertClose(self, actual, expected):
        self.assertTrue(math.isclose(actual, expected, rel_tol=2e-12, abs_tol=1e-18), (actual, expected))

    def test_covariance_at_fresh_and_nonzero_history_in_both_amplitude_branches(self):
        p = self.parameters
        for history in (0.0, 2e-5, 1e-3):
            for amplitude in (0.0, 5e-5, 2e-4, 1e-3, 2e-3):
                for e in (.58, .70, .85):
                    for reference in (.75, 1.1):
                        with self.subTest(history=history, amplitude=amplitude, e=e, reference=reference):
                            q, transformed_history = change_void_reference(p, history, reference)
                            old = rates(p, history, amplitude, e)
                            new = rates(q, transformed_history, amplitude, e)
                            factor = reference_scale(p)/reference_scale(q)
                            self.assertClose(new['history_rate'], factor*old['history_rate'])
                            self.assertClose(new['accumulation_kernel'], old['accumulation_kernel'])

    def test_equation_37_update_preserves_mapping_across_amplitude_changes(self):
        p = self.parameters
        history = 2e-5
        q, other_history = change_void_reference(p, history, 1.1)
        factor = reference_scale(p)/reference_scale(q)
        for amplitude, cycles, e in ((5e-5, 20, .85), (2e-4, 1000, .80), (2e-3, 500, .75), (1e-4, 2000, .70)):
            delta = history_increment(p, history, amplitude, cycles)
            other_delta = history_increment(q, other_history, amplitude, cycles)
            self.assertClose(other_delta, factor*delta)
            history += delta
            other_history += other_delta
            self.assertClose(other_history, factor*history)
            self.assertClose(rates(p, history, amplitude, e)['accumulation_kernel'],
                             rates(q, other_history, amplitude, e)['accumulation_kernel'])

    def test_changing_reference_alone_changes_response(self):
        p = self.parameters
        q = dict(p, e_ref=1.1)
        self.assertNotEqual(rates(p, 2e-5, 2e-4, .7)['accumulation_kernel'],
                            rates(q, 2e-5, 2e-4, .7)['accumulation_kernel'])

    def test_nonzero_history_must_also_be_transformed(self):
        p = self.parameters
        q, _ = change_void_reference(p, 2e-5, 1.1)
        self.assertFalse(math.isclose(rates(p, 2e-5, 2e-4, .7)['accumulation_kernel'],
                                     rates(q, 2e-5, 2e-4, .7)['accumulation_kernel'], rel_tol=.001))

    def test_amplitude_reference_rescaling_is_not_global_with_literal_cap(self):
        p = self.parameters
        q = dict(p, epsilon_ampl_ref=2*p['epsilon_ampl_ref'], C_N1=4*p['C_N1'])
        self.assertClose(rates(p, 2e-5, 2e-4, .7)['accumulation_kernel'],
                         rates(q, 2e-5, 2e-4, .7)['accumulation_kernel'])
        self.assertFalse(math.isclose(rates(p, 2e-5, 2e-3, .7)['accumulation_kernel'],
                                     rates(q, 2e-5, 2e-3, .7)['accumulation_kernel'], rel_tol=.001))


if __name__ == '__main__':
    unittest.main()
