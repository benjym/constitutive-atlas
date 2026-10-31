import json
import math
from pathlib import Path
import unittest
import fixtures
import prototype

class TraceDesign(unittest.TestCase):
    def test_frozen_fraction_corpus(self):self.assertEqual(fixtures.build(),json.loads(Path(__file__).with_name('corpus.json').read_text()))
    def test_random_exact_binary64(self):self.assertEqual(fixtures.random_check()['trials'],12000)
    def test_jet_all38_columns(self):
        d=[[0.]*38 for _ in range(3)]
        for j in range(38):
            d[0][j]=500.;d[1][j]=1e-130 if j%2==0 else -1e-130;d[2][j]=-500.
        v,got=prototype.jet_trace([1.,2.,3.],d)
        self.assertEqual(v,6.)
        for j in range(38):self.assertEqual(got[j],fixtures.rational([d[i][j]for i in range(3)]))
    def test_jet_identity_directions(self):
        for seed in range(6):
            d=[[0.]*38 for _ in range(3)]
            if seed<3:d[seed][seed]=1.
            _,got=prototype.jet_trace([0.,0.,0.],d)
            self.assertEqual(got[seed],1. if seed<3 else 0.)
    def test_derivative_overflow_rejects(self):
        d=[[0.]*38 for _ in range(3)]
        d[0][37]=d[1][37]=float.fromhex('0x1.fffffffffffffp1023')
        with self.assertRaises(OverflowError):prototype.jet_trace([1.,2.,3.],d)
    def test_nonfinite_inputs_and_seeds(self):
        for x in [math.inf,-math.inf,math.nan,True,1]:
            with self.assertRaises(ValueError):prototype.sum3(0.,0.,x)
        d=[[0.]*38 for _ in range(3)];d[2][37]=math.nan
        with self.assertRaises(ValueError):prototype.jet_trace([0.,0.,0.],d)
    def test_signedzero_policy(self):
        for xs in [[-0.,-0.,-0.],[-1.,1.,0.]]:self.assertEqual(prototype.bits(prototype.sum3(*xs)),0)
    def test_historical_witness(self):
        x=[500.,1e-130,-500.]
        self.assertEqual((x[0]+x[1])+x[2],0.)
        self.assertEqual(prototype.sum3(*x),1e-130)
        self.assertEqual(-(1+.75)*prototype.sum3(*x),-1.7500000000000002e-130)

if __name__=='__main__':unittest.main()
