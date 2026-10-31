"""Prospective calibration-response separation gates; no native calls."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

PACKET=Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-propagation-refinement-v1'
SPEC=importlib.util.spec_from_file_location('propagation_refinement_assessor_test',PACKET/'assess.py')
A=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(A)


class RefinementTests(unittest.TestCase):
    def setUp(self):self.policy={'separation_fraction':.01,'nonincrease_absolute_floor':1e-12}

    def test_separation_boundary_is_inclusive_and_both_levels_required(self):
        value=A.gate(.01,.005,1,self.policy)
        self.assertTrue(value['both_below_separation_threshold'])
        self.assertTrue(value['adjacent_change_nonincreasing'])
        self.assertFalse(A.gate(.01000001,.005,1,self.policy)['both_below_separation_threshold'])
        self.assertFalse(A.gate(.005,.02,1,self.policy)['both_below_separation_threshold'])

    def test_nonincrease_has_only_declared_absolute_floor(self):
        self.assertTrue(A.gate(.001,.001+5e-13,1,self.policy)['adjacent_change_nonincreasing'])
        self.assertFalse(A.gate(.001,.001+2e-12,1,self.policy)['adjacent_change_nonincreasing'])

    def test_zero_invalid_and_nonfinite_signals_cannot_pass_relative_gate(self):
        for cm,mf,signal in [(0,0,0),(-1,0,1),(0,0,-1),(float('nan'),0,1),(0,float('inf'),1),(0,0,True)]:
            with self.assertRaises(ValueError):A.gate(cm,mf,signal,self.policy)

    def test_partial_or_failed_finer_replay_cannot_receive_metric(self):
        record={'coarse_case_index':0,'maximum_increment':.0001}
        oldpolicy={'cases':[{}]}
        for prediction in ({'status':'timeout','completed_observations':0},
                           {'status':'success','completed_observations':1}):
            with patch.object(A.RUN.RUN,'prepare',return_value=({},[{},{}],{})), \
                 patch.object(A.RUN.RUN,'predict',return_value=prediction), \
                 patch.object(A.OLD,'compare_acquisition_linear',side_effect=AssertionError('partial scored')):
                with self.assertRaises(ValueError):A.RUN.compute(record,oldpolicy,None,None,None,None)


if __name__=='__main__':unittest.main()
