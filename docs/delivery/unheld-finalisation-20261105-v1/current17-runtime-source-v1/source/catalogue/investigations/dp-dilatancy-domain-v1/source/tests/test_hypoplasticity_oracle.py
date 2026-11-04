"""Independent coordinate/sign and integration checks for the VW96 oracle."""
import importlib.util
import math
import os
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('hypoplasticity_oracle',ROOT/'tools/verify_hypoplasticity.py')
oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
PARAMETERS=[1e5,math.pi/6,5.8e9,.28,.53,.84,1.,.13,1.05]


class HypoplasticityOracleTests(unittest.TestCase):
    def test_cartesian_mandel_shear_and_norm(self):
        v=[1,2,3,4,5,6];a=oracle.matrix(v)
        self.assertAlmostEqual(a[0][1],4/math.sqrt(2))
        self.assertAlmostEqual(oracle.inner(a,a),sum(x*x for x in v))
        for got,want in zip(oracle.mandel(a),v):self.assertAlmostEqual(got,want)

    def test_source_sign_conversion_and_positive_homogeneity(self):
        z=[1e5]*3+[0,0,0,.7];d=[.001]*3+[0]*3
        rate=oracle.reference_rate(z,d,PARAMETERS)
        self.assertGreater(rate[0],0)
        self.assertAlmostEqual(rate[6],-1.7*.003)
        scaled=oracle.reference_rate(z,[7*x for x in d],PARAMETERS)
        self.assertTrue(oracle.compare(scaled,[7*x for x in rate],1e-6,1e-12,1e-12)[0])
        reverse=oracle.reference_rate(z,[-x for x in d],PARAMETERS)
        self.assertGreater(abs(reverse[0]+rate[0]),1)

    def test_rk4_void_ratio_matches_continuity_solution(self):
        z=[1e5]*3+[0,0,0,.7];d=[.001]*3+[0]*3
        final=oracle.rk4(z,d,PARAMETERS,128)
        self.assertAlmostEqual(final[6],1.7*math.exp(-.003)-1,places=12)

    def test_comparison_rejects_shear_factor_and_nonfinite_errors(self):
        expected=oracle.reference_rate([1e5]*3+[0,0,0,.7],[0,0,0,.001,0,0],PARAMETERS)
        wrong=expected.copy();wrong[3]/=2
        self.assertFalse(oracle.compare(wrong,expected,1e-4,1e-11,1e-9)[0])
        self.assertFalse(oracle.compare([float('nan')],[0],1e-4,1e-11,1e-9)[0])

    def test_native_cartesian_rates_rk4_paths_and_rollback(self):
        report=oracle.execute(Path(os.environ.get('ATLAS_SOLVER',ROOT/'build/atlas_solver')))
        self.assertEqual(len(report['cases']),229)
        self.assertTrue(report['passed'],[c['id'] for c in report['cases'] if not c['passed']])
        for case in report['cases']:
            for segment in case.get('segments',[]):
                self.assertTrue(segment['reference_levels'][-1]['converged'])


if __name__=='__main__':unittest.main()
