"""Independent finite-difference derivative and algebraic density comparisons."""
import math
import unittest
from tools.clay2013_asbs_diagnostic import PARAMETERS,STRESS,describe,e_from_ratio,witness


class InitializationTests(unittest.TestCase):
    def test_ratio_density_roundtrip(self):
        for p in (1000.,50000.,100000.):
            for R in (.8,1.,2.,3.):
                e=e_from_ratio(p,R,N=.9,lambda_star=.1)
                iso=[[p*float(i==j) for j in range(3)] for i in range(3)]
                description=describe(iso,e,PARAMETERS)
                self.assertAlmostEqual(description['pe_over_p'],R,places=12)
                self.assertEqual(description['Fm'],0.)
                if R==1.:
                    self.assertLess(abs(description['asbs_residual']),1e-14)
                else:
                    self.assertEqual(description['asbs_residual']>0,R<1)

    def test_nonisotropic_density_boundary(self):
        d=describe(STRESS,.7,PARAMETERS)
        R=math.exp(-math.log1p(-d['Fm'])/d['omega'])
        boundary=e_from_ratio(d['p'],R,N=.9,lambda_star=.1)
        self.assertLess(abs(describe(STRESS,boundary,PARAMETERS)['asbs_residual']),1e-14)
        self.assertLess(describe(STRESS,boundary-.01,PARAMETERS)['asbs_residual'],0)
        self.assertGreater(describe(STRESS,boundary+.01,PARAMETERS)['asbs_residual'],0)

    def test_negative_density_not_clipped(self):
        with self.assertRaises(ValueError):e_from_ratio(1e10,1.,N=.1,lambda_star=.1)
        for ratio in (0.,-1.,True,math.inf):
            with self.assertRaises(ValueError):e_from_ratio(1000.,ratio,N=.9,lambda_star=.1)

    def test_outward_asbs_derivative(self):
        evidence=witness()
        self.assertLess(abs(evidence['initial']['asbs_residual']),1e-14)
        exact=evidence['analytic_directional_derivative']['f_dot']
        self.assertGreater(exact,.06)
        for probe in evidence['directional_probes']:
            self.assertGreater(probe['f_plus'],0)
            self.assertAlmostEqual(probe['central_directional_difference'],exact,places=7)
        self.assertGreater(evidence['rate']['diagnostics']['fdA'],0)
        self.assertGreater(evidence['e'],0)


if __name__=='__main__':unittest.main()
