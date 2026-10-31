"""Synthetic witnesses for the prospective numerical-separation decision."""
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-initialization-refinement-v1/assess.py'
SPEC=importlib.util.spec_from_file_location('initialization_refinement_assessor',PATH)
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)
POLICY={'gate':{'separation_fraction':0.01,'nonincrease_absolute_floor':1e-12}}


class RefinementSeparationTests(unittest.TestCase):
    def test_resolved_signal_with_smaller_adjacent_changes_passes(self):
        result=MODULE.separation_gate(0.0001,0.00002,0.1,POLICY)
        self.assertTrue(result['both_below_separation_threshold'])
        self.assertTrue(result['adjacent_change_nonincreasing'])

    def test_smaller_but_unresolved_change_does_not_pass_separation(self):
        result=MODULE.separation_gate(0.002,0.001,0.1,POLICY)
        self.assertFalse(result['both_below_separation_threshold'])
        self.assertTrue(result['adjacent_change_nonincreasing'])

    def test_small_but_growing_changes_do_not_pass_nonincrease(self):
        result=MODULE.separation_gate(0.00001,0.0001,0.1,POLICY)
        self.assertTrue(result['both_below_separation_threshold'])
        self.assertFalse(result['adjacent_change_nonincreasing'])

    def test_exact_threshold_and_zero_change_are_allowed(self):
        result=MODULE.separation_gate(0.001,0.001,0.1,POLICY)
        self.assertTrue(result['both_below_separation_threshold'])
        self.assertTrue(result['adjacent_change_nonincreasing'])
        result=MODULE.separation_gate(0,0,0.1,POLICY)
        self.assertTrue(result['both_below_separation_threshold'])
        self.assertTrue(result['adjacent_change_nonincreasing'])

    def test_explicit_roundoff_floor_is_not_a_signal_tolerance(self):
        result=MODULE.separation_gate(0,1e-12,0.1,POLICY)
        self.assertTrue(result['adjacent_change_nonincreasing'])
        result=MODULE.separation_gate(0,1.01e-12,0.1,POLICY)
        self.assertFalse(result['adjacent_change_nonincreasing'])
        result=MODULE.separation_gate(0,1e-12,1e-12,POLICY)
        self.assertFalse(result['both_below_separation_threshold'])

    def test_zero_signal_and_invalid_magnitudes_reject(self):
        for signal in (0,-1,True,float('inf'),float('nan')):
            with self.subTest(signal=signal),self.assertRaises(ValueError):
                MODULE.separation_gate(0,0,signal,POLICY)
        for value in (-1,False,float('inf'),float('nan')):
            with self.subTest(value=value),self.assertRaises(ValueError):
                MODULE.separation_gate(value,0,1,POLICY)


if __name__=='__main__':unittest.main()
