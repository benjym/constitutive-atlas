"""One-sided hardening-product limit, with no compiler or native execution."""
import math
import random
import unittest

from atlas.dsl import Sym, ValidationError
from tools.inspect_sanisand_original import load_fragment as load_original, evaluate_fragment as original
from tools.inspect_sanisand_limit import load_fragment, evaluate_fragment as scaled


def dot(a,b):return sum(x*y for x,y in zip(a,b))


def state(n,distance=.03,back=.15,p=1e5):
    length=math.sqrt(dot(n,n));n=[x/length for x in n]
    alpha=[back*x for x in n]
    radius=math.sqrt(2/3)*.01
    return dict(sigma=Sym(tuple(p*(alpha[i]+radius*n[i]+(1 if i<3 else 0)) for i in range(6))),
                alpha=Sym(tuple(alpha)),alpha_in=Sym(tuple(a-distance*x for a,x in zip(alpha,n))),
                z=Sym(tuple(-.4*x for x in n)),e=.7,
                d_epsilon=Sym(tuple(1e-4*x+(1e-5 if i<3 else 0) for i,x in enumerate(n))))


class SANISANDLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.fragment=load_fragment();cls.original=load_original()

    def assertNear(self,a,b,atol=1e-12):
        av=a.v if isinstance(a,Sym) else (a,);bv=b.v if isinstance(b,Sym) else (b,)
        for x,y in zip(av,bv):self.assertLessEqual(abs(x-y),atol+2e-11*abs(y))

    def test_equivalent_to_finite_original_in_loading_and_unloading(self):
        rng=random.Random(200420)
        for i in range(20):
            v=[rng.uniform(-1,1) for _ in range(5)];n=[v[0],v[1],-v[0]-v[1],*v[2:]]
            for distance in [1e-6,.001,.03]:
                for sign in [-1,1]:
                    x=state(n,distance,back=.15 if i%2 else .9,p=1e4 if i%3 else 1e6)
                    x['d_epsilon']=x['d_epsilon']*sign
                    a=scaled(self.fragment,**x);b=original(self.original,**x)
                    for name in ['plastic_multiplier','plastic_strain_increment','backstress_increment','fabric_increment']:
                        self.assertNear(a[name],b[name])
                    self.assertNear(a['stress_increment'],b['stress_increment'],atol=1e-8)
                    self.assertNear(a['multiplier_times_h'],b['plastic_multiplier']*b['h'])

    def test_zero_limit_from_yield_consistency_and_no_hardening_cap(self):
        for n in [[2,-1,-1,0,0,0],[-2,1,1,0,0,0],[.4,-.1,-.3,.7,-.2,.1]]:
            x=state(n,0.)
            a=scaled(self.fragment,**x)
            self.assertEqual(a['plastic_multiplier'],0.)
            elastic=[2*a['G']*v+(a['K']*a['volumetric_increment'] if i<3 else 0.) for i,v in enumerate(a['de'].v)]
            self.assertNear(a['stress_increment'],Sym(tuple(elastic)),atol=1e-8)
            b=[v-w for v,w in zip(a['alpha_b'].v,x['alpha'].v)]
            N=[v-(dot(a['n'].v,a['r'].v)/3 if i<3 else 0.) for i,v in enumerate(a['n'].v)]
            projection=dot(N,elastic)
            self.assertGreater(projection,0.)
            expected=[v*projection/(a['p']*dot(b,a['n'].v)) for v in b]
            self.assertNear(a['backstress_increment'],Sym(tuple(expected)))
            self.assertNear(dot(N,a['stress_increment'].v),a['p']*dot(a['n'].v,a['backstress_increment'].v),atol=1e-8)
            self.assertEqual(a['fabric_increment'].v,(0.,)*6)
            # This limit cancels b0, so h0 must not introduce a finite-cap artifact.
            for h0 in [1e-6,1e6]:
                other=scaled(self.fragment,**dict(x,h0=h0))
                self.assertNear(other['backstress_increment'],a['backstress_increment'])
            reverse=scaled(self.fragment,**dict(x,d_epsilon=-x['d_epsilon']))
            self.assertEqual(reverse['backstress_increment'].v,(0.,)*6)
            for pressure_scale in [1e-3,1e3]:
                other=scaled(self.fragment,**dict(x,sigma=x['sigma']*pressure_scale,p_at=1e5*pressure_scale))
                self.assertNear(other['backstress_increment'],a['backstress_increment'])
                self.assertNear(other['stress_increment']/pressure_scale,a['stress_increment'],atol=1e-8)

    def test_one_sided_convergence_to_zero_and_overflow_avoidance(self):
        n=[.4,-.1,-.3,.7,-.2,.1]
        limit=scaled(self.fragment,**state(n,0.,back=0.))
        errors=[]
        for distance in [1e-3,1e-5,1e-7,1e-9,1e-12,1e-100,1e-305]:
            x=state(n,distance,back=0.)
            a=scaled(self.fragment,**x)
            self.assertGreater(a['plastic_multiplier'],0.)
            self.assertGreater(a['hardening_distance'],0.)
            err=math.sqrt(sum((v-w)**2 for v,w in zip(a['backstress_increment'].v,limit['backstress_increment'].v)))
            errors.append(err)
        for before,after in zip(errors[:4],errors[1:5]):self.assertLess(after,before*.02)
        self.assertLess(errors[-1],1e-14)
        with self.assertRaises(ValidationError):original(self.original,**state(n,1e-305,back=0.))

    def test_negative_distance_and_invalid_zero_limits_are_not_regularized(self):
        with self.assertRaises(ValidationError):scaled(self.fragment,**state([2,-1,-1,0,0,0],-.01))
        with self.assertRaises(ValidationError):scaled(self.fragment,**state([2,-1,-1,0,0,0],0.,back=2.))
        # Algebraic double zero: at psi=0 and M=m, alpha_b=alpha=0.
        # This is not a proposed physical calibration; it must remain undefined.
        with self.assertRaises(ValidationError):
            scaled(self.fragment,**dict(state([0,0,0,1,0,0],0.,back=0.),
                                       M=.01,c=1.,lambda_c=0.,e0=.7))
        # Positive distance still preserves softening rather than enforcing positive Kp.
        x=state([2,-1,-1,0,0,0],.03,back=2.)
        a=scaled(self.fragment,**x);b=original(self.original,**x)
        self.assertLess(a['hardening_numerator'],0.)
        self.assertNear(a['stress_increment'],b['stress_increment'],atol=1e-8)


if __name__=='__main__':unittest.main()
