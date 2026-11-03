"""Closed current-sixteen fixture allocation preserves the strict historical gate."""
import unittest
from tools.check_native_fixture_contracts import (PRIOR_THIRTEEN,DUNCAN,DUNCAN_HASH,RAMBERG,RAMBERG_HASH,SCLAY,SCLAY_HASH,OCC,check_recorded_failure)

class SClay1FixtureContracts(unittest.TestCase):
    def test_fifteen_and_sixteen_contexts_retain_identical_strict_occ_failure(self):
        message='failed knot 1 residual 0.00086977407608239442 trials 1 de0 0.0001 de1 0\ndrained replay failed: '+OCC+' singular mixed-control system; last committed knot retained\n'
        prior={**PRIOR_THIRTEEN,DUNCAN:DUNCAN_HASH,RAMBERG:RAMBERG_HASH}
        self.assertIn('current-fifteen',check_recorded_failure(message,prior))
        current={**prior,SCLAY:SCLAY_HASH}
        self.assertIn('current-sixteen',check_recorded_failure(message,current))
        for bad in [dict(current,**{SCLAY:'0'*64}),dict(current,**{'linear-elastic':'0'*64}),dict(current,unexpected='0'*64),{k:v for k,v in current.items() if k!='linear-elastic'}]:
            with self.subTest(definitions=bad),self.assertRaises(AssertionError):check_recorded_failure(message,bad)
        with self.assertRaises(AssertionError):check_recorded_failure(message.replace('trials 1','trials 2'),current)
