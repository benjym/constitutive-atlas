"""Analytical point-set/ODE oracles, not an HCA constitutive validation suite."""
import copy
import decimal
import hashlib
import json
import math
import unittest
from pathlib import Path

from tools.hca_diagnostics import SOURCE, convert_mandel, g_a_increment, sampled_amplitude


def loop(n, major=2., minor=1.):
    return [[major*math.cos(2*math.pi*k/n), minor*math.sin(2*math.pi*k/n), 0.,0.,0.,0.]
            for k in range(n)]


class AmplitudeTests(unittest.TestCase):
    def assertMatrixClose(self, a, b, places=12):
        for ra, rb in zip(a, b):
            for x, y in zip(ra, rb): self.assertAlmostEqual(x, y, places=places)

    def test_cartesian_tensor_basis_and_metric(self):
        # Explicit symmetric Cartesian tensor, with unequal xz and yz components.
        T = [[1.,2.,3.],[2.,4.,5.],[3.,5.,6.]]
        atlas = [T[0][0],T[1][1],T[2][2],math.sqrt(2)*T[0][1],math.sqrt(2)*T[1][2],math.sqrt(2)*T[0][2]]
        source = [T[0][0],T[1][1],T[2][2],math.sqrt(2)*T[0][1],math.sqrt(2)*T[0][2],math.sqrt(2)*T[1][2]]
        self.assertEqual(convert_mandel(source,source='source_mandel',target='atlas_mandel'),tuple(atlas))
        self.assertAlmostEqual(sum(x*x for x in atlas),sum(x*x for row in T for x in row))
        s = sampled_amplitude([source,[-x for x in source]],basis='source_mandel')
        a = sampled_amplitude([atlas,[-x for x in atlas]])
        self.assertMatrixClose(s['amplitude_operator'],a['amplitude_operator'])
        self.assertEqual(s['sampled_rank'],1)
        self.assertAlmostEqual(s['epsilon_ampl'],math.sqrt(sum(x*x for row in T for x in row)))

    def test_rank_one_independent_outer_product(self):
        direction=[1.,-2.,3.,-4.,5.,-6.]; length=math.hypot(*direction)
        points=[[t*x for x in direction] for t in (-3.,0.,1.,2.)]
        result=sampled_amplitude(points)
        self.assertEqual(result['sampled_rank'],1)
        self.assertAlmostEqual(result['radii'][0],2.5*length)
        expected=[[2.5*x*y/length for y in direction] for x in direction]
        self.assertMatrixClose(result['amplitude_operator'],expected)

    def test_harmonic_axis_extrema_oracles(self):
        for a,b in [(2.,1.),(1.,1.)]:
            r=sampled_amplitude(loop(32,a,b))
            self.assertEqual(r['sampled_rank'],2)
            self.assertAlmostEqual(r['epsilon_ampl'],math.hypot(a,b))
            expected=[[0.]*6 for _ in range(6)];expected[0][0]=a;expected[1][1]=b
            self.assertMatrixClose(r['amplitude_operator'],expected)

    def test_translation_order_repetitions_and_zero(self):
        points=loop(24); original=copy.deepcopy(points); reference=sampled_amplitude(points)
        variants=[list(reversed(points)), points[7:]+points[:7],points+points,
                  [[x+(i+1)*.125 for i,x in enumerate(p)] for p in points]]
        for v in variants:
            self.assertMatrixClose(sampled_amplitude(v)['amplitude_operator'],reference['amplitude_operator'])
        self.assertEqual(points,original)
        zero=sampled_amplitude([[2.]*6]*3)
        self.assertEqual(zero['sampled_rank'],0);self.assertEqual(zero['directions'],[])
        self.assertIsNone(zero['normalized_operator']);self.assertEqual(zero['epsilon_ampl'],0.)

    def test_six_dimensional_point_set_and_exact_ties(self):
        points=[]
        for i in range(6):
            for sign in (-1.,1.): points.append([sign if j==i else 0. for j in range(6)])
        result=sampled_amplitude(points)
        self.assertEqual(result['sampled_rank'],6)
        self.assertEqual(result['radii'],[1.]*6)
        self.assertEqual(result['stages'][0]['selected_pair'],[0,1])
        self.assertEqual(len(result['stages'][0]['exact_tied_pairs']),6)
        self.assertMatrixClose(result['amplitude_operator'],[[float(i==j) for j in range(6)] for i in range(6)])
        self.assertAlmostEqual(result['epsilon_ampl'],math.sqrt(6))

    def test_sampling_convergence_is_not_continuous_exactness(self):
        errors=[abs(sampled_amplitude(loop(n))['epsilon_ampl']-math.sqrt(5)) for n in (10,30,90)]
        self.assertGreater(errors[0],errors[1]);self.assertGreater(errors[1],errors[2])
        self.assertGreater(errors[-1],0.)

    def test_rank_policy_and_domains(self):
        pts=[[x,y,0.,0.,0.,0.] for x,y in [(1,0),(-1,0),(0,1e-14),(0,-1e-14)]]
        self.assertEqual(sampled_amplitude(pts)['sampled_rank'],1)
        self.assertEqual(sampled_amplitude(pts,rank_relative_tolerance=1e-15)['sampled_rank'],2)
        for bad in ([],[[0.]*6],[[0.]*6]*129,[[0.]*5]*2,[[math.nan]*6]*2,[[True]*6]*2,
                    [[1e308]*6,[-1e308]*6],[[0.]*6,[5e-324,0,0,0,0,0]]):
            with self.assertRaises(ValueError): sampled_amplitude(bad)
        for tol in (0.,-1.,math.nan,True,.1):
            with self.assertRaises(ValueError): sampled_amplitude([[0.]*6]*2,rank_relative_tolerance=tol)


class ScalarHistoryTests(unittest.TestCase):
    def test_independent_transformed_solution(self):
        # y=exp(g/b) obeys y'=C_N2; this oracle avoids the increment formula.
        g,a,c1,c2,N=.4,.2,3.,.7,12.
        b=a*c1; result=g_a_increment(g,a,c1,c2,N)
        expected=b*math.log(math.exp(g/b)+c2*N)
        self.assertAlmostEqual(result['g_A_out'],expected,places=14)
        self.assertAlmostEqual(math.exp(result['g_A_out']/b)-math.exp(g/b),c2*N,places=13)

    def test_fixed_amplitude_composition(self):
        whole=g_a_increment(.03,.1,.8,.2,17.)['g_A_out']; split=.03
        for delta in (1.,3.,.5,12.5): split=g_a_increment(split,.1,.8,.2,delta)['g_A_out']
        self.assertAlmostEqual(split,whole,places=14)

    def test_zero_limits_and_separate_count_origin(self):
        for args in ((.4,0.,2.,3.,4.),(.4,1.,2.,0.,4.),(.4,1.,2.,3.,0.)):
            self.assertEqual(g_a_increment(*args),{'delta_g_A':0.,'g_A_out':.4})
        # Reporting origin is absent from API: persistent g_A plus delta_N defines the update.
        for origin in (0.,1000.):
            self.assertEqual(g_a_increment(.4,.1,2.,3.,4.),g_a_increment(.4,.1,2.,3.,(origin+4)-origin))
        near=g_a_increment(0.,1e-12,2.,3.,4.)
        self.assertAlmostEqual(near['delta_g_A']/2e-12,math.log(13))

    def test_two_amplitudes_preserve_history(self):
        first=g_a_increment(.2,.1,2.,.3,4.)['g_A_out']
        result=g_a_increment(first,.4,2.,.3,7.)['g_A_out']
        expected=.8*math.log(math.exp(first/.8)+.3*7.)
        self.assertAlmostEqual(result,expected)
        self.assertNotEqual(result,g_a_increment(0.,.4,2.,.3,7.)['g_A_out'])

    def test_extreme_products_underflow_and_lost_increment(self):
        # Product C_N2*N overflows in naive arithmetic; finite log-domain result remains.
        result=g_a_increment(0.,1.,1.,1e308,1e308)
        self.assertAlmostEqual(result['g_A_out'],2*math.log(1e308))
        for args in ((0.,1e308,1e308,1.,1.),(0.,5e-324,.1,1.,1.),
                     (1000.,1.,1.,1.,1.),(1.,1.,1.,1e-20,1.)):
            with self.assertRaises(ValueError): g_a_increment(*args)
        for args in ((-1,1,1,1,1),(0,1,0,1,1),(0,1,1,-1,1),(0,1,1,1,-1),
                     (math.nan,1,1,1,1),(True,1,1,1,1)):
            with self.assertRaises(ValueError):g_a_increment(*args)

    def test_extreme_representable_increment_decimal_oracle(self):
        cases=[(0.,1e300,1.,1e-300,1e-100),
               (0.,1e250,1.,1e-280,1e-100),
               (0.,1e300,1.,1e-300,1e-300),
               (1e-200,1e300,1.,1e-300,1e-100),
               (0.,1e200,1e200,1e-300,1e-100),
               (0.,5e-324,.1,1e300,1.),
               (0.,5e-324,.6,1e300,1.),
               (0.,1e-300,1.,1e300,1.)]
        for args in cases:
            with self.subTest(args=args), decimal.localcontext() as context:
                context.prec=1200
                g,a,c1,c2,n=map(decimal.Decimal.from_float,args)
                b=a*c1
                exact=b*(1+c2*n*(-g/b).exp()).ln()
                expected=float(exact)
                self.assertGreater(expected,0.)
                actual=g_a_increment(*args)
                # Logs/exp are numerical, not a correctly-rounded result promise.
                tolerance=max(abs(expected)*5e-13,math.ulp(expected))
                self.assertLessEqual(abs(actual['delta_g_A']-expected),tolerance)
                self.assertLessEqual(abs(actual['g_A_out']-float(g+exact)),tolerance)


class RetainedEvidenceTests(unittest.TestCase):
    def test_manifest_and_retained_observations(self):
        root=Path(__file__).resolve().parents[1]
        directory=root/'catalogue/investigations/hca-diagnostics-v1'
        manifest=json.loads((directory/'manifest.json').read_text())
        self.assertEqual(set(manifest),{'tools/hca_diagnostics.py','tests/test_hca_diagnostics.py',
                                       'tests/test_hca_covariance.py',
                                       'docs/HCA_DIAGNOSTICS.md',
                                       'catalogue/investigations/hca-diagnostics-v1/evidence.json'})
        for name,digest in manifest.items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),digest,name)
        evidence=json.loads((directory/'evidence.json').read_text())
        self.assertEqual(evidence['source'],SOURCE)
        self.assertIs(evidence['source_hash_verified'],True)
        self.assertEqual(evidence['inputs_sha256'],{k:v for k,v in manifest.items() if not k.endswith('evidence.json')})
        errors=[evidence['harmonic_sampling'][str(n)]['absolute_norm_error'] for n in (10,30,90)]
        self.assertGreater(errors[0],errors[1]);self.assertGreater(errors[1],errors[2])
        self.assertLess(evidence['history_composition']['absolute_difference'],1e-14)
        self.assertEqual(len(evidence['extreme_scalar_cases']),5)
        for case in evidence['extreme_scalar_cases']:
            expected=case['decimal_1200_reference']
            self.assertLessEqual(case['absolute_error'],max(abs(expected)*5e-13,math.ulp(expected)))


if __name__=='__main__': unittest.main()
