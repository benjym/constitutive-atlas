"""Original SANISAND source identities; Python only, no native solver imports."""
import math
import random
import unittest

from atlas.dsl import Sym, ValidationError
from tools.inspect_sanisand_original import evaluate_fragment, load_fragment


def norm(v): return math.sqrt(sum(x*x for x in v))
def dot(a,b): return sum(x*y for x,y in zip(a,b))


class SANISANDOriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.fragment=load_fragment()

    def inputs(self,n,pressure=1e5,e=.8,back=.15):
        n=[v/norm(n) for v in n]
        alpha=[back*x for x in n]
        r=[a+math.sqrt(2/3)*.01*x for a,x in zip(alpha,n)]
        return dict(sigma=Sym(tuple(pressure*(r[i]+(1 if i<3 else 0)) for i in range(6))),
                    alpha=Sym(tuple(alpha)),alpha_in=Sym(tuple(a-.03*x for a,x in zip(alpha,n))),
                    z=Sym(tuple(.4*x for x in n)),e=e,
                    d_epsilon=Sym(tuple(1e-4*x+(2e-5 if i<3 else 0) for i,x in enumerate(n))))

    def test_triaxial_reductions_and_current_density_elasticity(self):
        # Appendix: Rdev=n in both triaxial limits and Kp=(2/3)*p*H.
        for sign,g in [(1,1.),(-1,.712)]:
            x=self.inputs([sign*2,-sign,-sign,0,0,0])
            a=evaluate_fragment(self.fragment,**x)
            self.assertAlmostEqual(a['g'],g,places=12)
            for v,w in zip(a['Rdev'].v,a['n'].v):self.assertAlmostEqual(v,w,places=12)
            eta=math.sqrt(3/2)*dot(a['r'].v,a['n'].v)
            Mb=g*1.25*math.exp(-1.1*a['psi'])
            expected=(2/3)*a['p']*a['h']*math.sqrt(2/3)*(Mb-eta)
            self.assertAlmostEqual(a['Kp']/expected,1.,places=11)
        x=self.inputs([2,-1,-1,0,0,0]);a=evaluate_fragment(self.fragment,**x)
        b=evaluate_fragment(self.fragment,**dict(x,e=.7))
        ratio=((2.97-.7)**2/1.7)/((2.97-.8)**2/1.8)
        self.assertAlmostEqual(b['G']/a['G'],ratio,places=12)

    def test_general_cartesian_flow_and_loading_consistency(self):
        rng=random.Random(2004)
        active=0
        for _ in range(40):
            v=[rng.uniform(-1,1) for _ in range(5)]
            x=self.inputs([v[0],v[1],-v[0]-v[1],*v[2:]])
            a=evaluate_fragment(self.fragment,**x)
            n=a['n'].v;s=math.sqrt(2)
            matrix=[[n[0],n[3]/s,n[5]/s],[n[3]/s,n[1],n[4]/s],[n[5]/s,n[4]/s,n[2]]]
            square=[[sum(matrix[i][k]*matrix[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
            det=(matrix[0][0]*(matrix[1][1]*matrix[2][2]-matrix[1][2]*matrix[2][1])
                 -matrix[0][1]*(matrix[1][0]*matrix[2][2]-matrix[1][2]*matrix[2][0])
                 +matrix[0][2]*(matrix[1][0]*matrix[2][1]-matrix[1][1]*matrix[2][0]))
            self.assertAlmostEqual(a['cos3theta'],3*math.sqrt(6)*det,places=12)
            trace=sum(square[i][i] for i in range(3))
            source=[[a['B']*matrix[i][j]-a['C']*(square[i][j]-(trace/3 if i==j else 0)) for j in range(3)] for i in range(3)]
            expected=[source[0][0],source[1][1],source[2][2],s*source[0][1],s*source[1][2],s*source[0][2]]
            for v,w in zip(a['Rdev'].v,expected):self.assertAlmostEqual(v,w,places=12)
            self.assertAlmostEqual(sum(a['Rdev'].v[:3]),0.,places=12)
            # Yield consistency: N:d_sigma = p*n:d_alpha, since dm=0.
            if a['L']>0:
                active+=1
                N=[v-(dot(n,a['r'].v)/3 if i<3 else 0) for i,v in enumerate(n)]
                lhs=dot(N,a['stress_increment'].v)
                rhs=a['p']*dot(n,a['backstress_increment'].v)
                self.assertAlmostEqual(lhs,rhs,delta=1e-8)
            self.assertAlmostEqual(sum(a['plastic_strain_increment'].v[:3]),a['plastic_multiplier']*a['D'],places=14)
        self.assertEqual(active,40)

    def test_unloading_is_elastic_and_fabric_evolves_only_during_dilation(self):
        x=self.inputs([2,-1,-1,0,0,0],e=.7,back=.9)
        a=evaluate_fragment(self.fragment,**x)
        self.assertGreater(a['L'],0.)
        self.assertLess(a['D'],0.)
        self.assertGreater(norm(a['fabric_increment'].v),0.)
        self.assertLess(dot(a['fabric_increment'].v,a['n'].v),0.)
        b=evaluate_fragment(self.fragment,**dict(x,d_epsilon=-x['d_epsilon']))
        self.assertLess(b['L'],0.)
        for name in ['plastic_strain_increment','fabric_increment','backstress_increment']:
            self.assertEqual(norm(b[name].v),0.)
        elastic=[2*b['G']*v+(b['K']*b['volumetric_increment'] if i<3 else 0.)
                 for i,v in enumerate(b['de'].v)]
        for v,w in zip(b['stress_increment'].v,elastic):self.assertAlmostEqual(v,w,places=12)

    def test_pressure_unit_covariance(self):
        x=self.inputs([.4,-.1,-.3,.7,-.2,.1]);a=evaluate_fragment(self.fragment,**x)
        for scale in [1e-3,1e3]:
            b=evaluate_fragment(self.fragment,**dict(x,sigma=x['sigma']*scale,p_at=1e5*scale))
            for name in ['G','K','Kp','loading_denominator']:
                self.assertAlmostEqual(b[name]/(a[name]*scale),1.,places=10)
            self.assertAlmostEqual(a['L'],b['L'],places=12)
            for v,w in zip(a['stress_increment'].v,b['stress_increment'].v):self.assertAlmostEqual(v,w/scale,delta=1e-8)
            for name in ['backstress_increment','fabric_increment']:
                for v,w in zip(a[name].v,b[name].v):self.assertAlmostEqual(v,w,places=12)

    def test_softening_is_not_clipped_and_unresolved_states_are_rejected(self):
        x=self.inputs([2,-1,-1,0,0,0],back=2.)
        self.assertLess(evaluate_fragment(self.fragment,**x)['Kp'],0.)
        good=self.inputs([2,-1,-1,0,0,0])
        for changes in [dict(alpha_in=good['alpha']),dict(sigma=good['sigma']*0),
                        dict(m=.02),dict(z=Sym((1.,0.,0.,0.,0.,0.)))]:
            with self.assertRaises(ValidationError):evaluate_fragment(self.fragment,**dict(good,**changes))


if __name__=='__main__':unittest.main()
