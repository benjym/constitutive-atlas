import json
import math
from pathlib import Path
import unittest
import algebra as a


class AlgebraTests(unittest.TestCase):
    def test_csl_origin(self):
        self.assertAlmostEqual(a.csl(0)[0],a.PARAMETERS['ec0'],places=15)

    def test_csl_derivative_independent_difference(self):
        # Symmetric finite difference of Eq26/27 vs derivative inverse Eq25.
        for sigma in [1.,100.,1000.,10000.]:
            step=1e-4*max(1.,sigma)
            fd=(a.csl(sigma+step)[0]-a.csl(sigma-step)[0])/(2*step)
            self.assertLess(abs(fd/a.csl(sigma)[1]-1),2e-8)

    def test_csl_monotonic_limit(self):
        vals=[a.csl(s)[0] for s in [0,1,100,10000,1e100]]
        self.assertTrue(all(x>y for x,y in zip(vals,vals[1:])))
        self.assertGreater(vals[-1],a.PARAMETERS['emin'])
        self.assertLess(vals[-1]-a.PARAMETERS['emin'],1e-4)

    def test_mass_balance(self):
        t,e,d=[-120,-80,-60],.75,[-.002,.0003,.0004]
        _,er=a.diagonal_rate(t,e,d)
        self.assertEqual(er,(1+e)*math.fsum(d))
        # Exact independent finite path volume solution, not a stress integration.
        v=math.fsum(d)
        target=(1+e)*math.exp(v)-1
        self.assertAlmostEqual(math.log1p(target)-math.log1p(e),v,places=15)

    def test_positive_homogeneity(self):
        t,e,d=[-120,-80,-60],.75,[-.002,.0003,.0004]
        r,er=a.diagonal_rate(t,e,d)
        r2,er2=a.diagonal_rate(t,e,[8*x for x in d])
        for x,y in zip(r,r2): self.assertEqual(8*x,y)
        self.assertEqual(8*er,er2)

    def test_stress_units(self):
        t,e,d=[-120,-80,-60],.75,[-.002,.0003,.0004]
        r,er=a.diagonal_rate(t,e,d)
        p=dict(a.PARAMETERS,c4=1000*a.PARAMETERS['c4'])
        r2,er2=a.diagonal_rate([1000*x for x in t],e,d,p)
        for x,y in zip(r,r2): self.assertAlmostEqual(y/(1000*x),1.,places=14)
        self.assertEqual(er,er2)

    def test_compression_positive_crosswalk(self):
        t,e,d=[-120,-80,-60],.75,[-.002,.0003,.0004]
        source,source_e=a.diagonal_rate(t,e,d)
        stress=[-x for x in t]
        load=[-x for x in d]
        n=math.hypot(*load)
        u=[x/n for x in load]
        v=math.fsum(u)
        p=a.PARAMETERS
        coefficient=p['c1']*math.exp(-p['c2']*v)
        tensor=[math.exp(-coefficient*x) for x in u]
        pn=math.hypot(*tensor)
        sn=math.hypot(*stress)
        ec=a.csl(sn)[0]
        k=(p['c4']+p['c5']*sn)/(e-p['emin'])
        result=[k*((v-p['c3']*ec)*x/pn+p['c3']*e*y/sn)*n for x,y in zip(tensor,stress)]
        for x,y in zip(result,source): self.assertEqual(x,-y)
        self.assertEqual(-(1+e)*math.fsum(load),source_e)

    def test_critical_state_cancellation(self):
        d=[-2.,1.,1.]
        dn=math.hypot(*d)
        raw=[-math.exp(a.PARAMETERS['c1']*x/dn) for x in d]
        t=[300*x/math.hypot(*raw) for x in raw]
        e=a.csl(math.hypot(*t))[0]
        r,er=a.diagonal_rate(t,e,d)
        self.assertLess(math.hypot(*r),1e-10)
        self.assertEqual(er,0.)

    def test_reversal_not_odd(self):
        t,e,d=[-120,-80,-60],.75,[-.002,.0003,.0004]
        r,_=a.diagonal_rate(t,e,d)
        rev,_=a.diagonal_rate(t,e,[-x for x in d])
        self.assertGreater(math.hypot(*(x+y for x,y in zip(r,rev))),1.)

    def test_matrix_not_componentwise_and_rotation(self):
        # Exact2x2 spectral identity, independent of generic expm implementations.
        x=.4
        ep,em=math.exp(x),math.exp(-x)
        c,s=math.cosh(x),math.sinh(x)
        self.assertAlmostEqual((ep+em)/2,c,places=15)
        self.assertAlmostEqual((ep-em)/2,s,places=15)
        self.assertNotEqual(c,math.exp(0))
        self.assertNotEqual(s,math.exp(x))
        # The45degree eigenbasis transforms diag(exp(x),exp(-x)) back.
        q=1/math.sqrt(2)
        got=[[q*q*(ep+em),q*q*(ep-em)],[q*q*(ep-em),q*q*(ep+em)]]
        self.assertAlmostEqual(got[0][0],c,places=15)
        self.assertAlmostEqual(got[0][1],s,places=15)

    def test_zero_stress_nonunique(self):
        self.assertGreater(a.stress_origin_witness()['difference_norm'],100.)
        ds=a.stress_origin_witness()['directions']
        for eps in [1e-3,1e-6,1e-9]:
            r1,_=a.diagonal_rate([eps*x for x in ds[0]],.75,[-1,0,0])
            r2,_=a.diagonal_rate([eps*x for x in ds[1]],.75,[-1,0,0])
            got=[x-y for x,y in zip(r1,r2)]
            expected=a.stress_origin_witness()['limiting_rate_difference']
            self.assertLess(math.hypot(*(x-y for x,y in zip(got,expected))),.1)

    def test_undefined_boundaries_not_silently_completed(self):
        for t,e,d in [([0,0,0],.75,[-1,0,0]),([-1,-1,-1],.75,[0,0,0]),([-1,-1,-1],.35,[-1,0,0])]:
            with self.assertRaises(ValueError): a.diagonal_rate(t,e,d)

    def test_frozen_fixture(self):
        self.assertEqual(json.loads(Path(__file__).with_name('fixtures.json').read_text()),json.loads(json.dumps(a.build_fixtures())))

if __name__=='__main__': unittest.main()
