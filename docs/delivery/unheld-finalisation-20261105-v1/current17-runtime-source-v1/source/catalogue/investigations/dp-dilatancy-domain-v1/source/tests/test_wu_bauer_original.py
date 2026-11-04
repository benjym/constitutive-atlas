"""Independent Cartesian and axisymmetric checks of unresolved source algebra."""
import math
import random
import unittest
from atlas.dsl import Sym, ValidationError
from tools.inspect_wu_bauer_original import evaluate_fragment, load_fragment, printed_calibration_ratios


def mandel(a):
    return Sym((a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]))


def rotate(a):
    q=((1/3,2/3,2/3),(2/3,1/3,-2/3),(-2/3,2/3,-1/3))
    return [[sum(q[i][k]*a[k][l]*q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]


def cartesian(s,d,c):
    t=sum(s[i][i] for i in range(3))
    sd=sum(s[i][j]*d[j][i] for i in range(3) for j in range(3))
    n=math.sqrt(sum(x*x for row in d for x in row))
    dev=[[s[i][j]-(t/3 if i==j else 0) for j in range(3)] for i in range(3)]
    return [[c[0]*t*d[i][j]+c[1]*sd*s[i][j]/t+n/t*sum(c[2]*s[i][k]*s[k][j]+c[3]*dev[i][k]*dev[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


class WuBauerOriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fragment=load_fragment()

    def rate(self,s,d,c):
        return evaluate_fragment(self.fragment,stress=s,stretching=d,coefficients=c)['objective_rate']

    def close(self,a,b):
        for x,y in zip(a.v,b.v):
            self.assertAlmostEqual(x,y,delta=2e-12*max(1.,abs(x),abs(y)))

    def test_cartesian_square_contraction_and_rotation(self):
        rng=random.Random(1994)
        for _ in range(30):
            x,y,z=[rng.uniform(1e4,3e5) for _ in range(3)]
            u,v,w=[rng.uniform(-1e3,1e3) for _ in range(3)]
            s=[[x,u,w],[u,y,v],[w,v,z]]
            a,b,c,h,j,k=[rng.uniform(-.02,.02) for _ in range(6)]
            d=[[a,h,k],[h,b,j],[k,j,c]]
            for parameters in self.fragment['published_parameter_sets']:
                coeff=parameters['coefficients']
                expected=cartesian(s,d,coeff)
                self.close(self.rate(mandel(s),mandel(d),coeff),mandel(expected))
                self.close(self.rate(mandel(rotate(s)),mandel(rotate(d)),coeff),mandel(rotate(expected)))

    def test_axisymmetric_equations_23_24(self):
        for record in self.fragment['published_parameter_sets']:
            c1,c2,c3,c4=record['coefficients']
            for s1,s3 in [(1e5,1e5),(3e5,1e5),(5e4,1e5)]:
                for d1,d3 in [(-1.,.2),(1.,-.1),(0.,1.),(0.,0.)]:
                    t=s1+2*s3; n=math.sqrt(d1*d1+2*d3*d3); sd=s1*d1+2*s3*d3
                    h1=c1*t*d1+c2*sd*s1/t+(c3*s1*s1+4*c4*(s1-s3)**2/9)*n/t
                    h3=c1*t*d3+c2*sd*s3/t+(c3*s3*s3+c4*(s1-s3)**2/9)*n/t
                    self.close(self.rate(Sym((s1,s3,s3,0.,0.,0.)),Sym((d1,d3,d3,0.,0.,0.)),(c1,c2,c3,c4)),Sym((h1,h3,h3,0.,0.,0.)))

    def test_homogeneity_and_zero_direction_nonsmoothness(self):
        s=Sym((2e5,1e5,1e5,100.,200.,300.)); d=Sym((-.1,.03,.02,.04,.05,.01))
        c=self.fragment['published_parameter_sets'][0]['coefficients']
        baseline=self.rate(s,d,c)
        for scale in [1e-6,1.,1e6]:
            self.close(self.rate(s*scale,d,c),baseline*scale)
            self.close(self.rate(s,d*scale,c),baseline*scale)
        zero=Sym((0.,)*6)
        self.close(self.rate(s,zero,c),zero)
        # A differentiable homogeneous law at zero would have opposite directional rates.
        even=self.rate(s,d,c)+self.rate(s,-d,c)
        self.assertGreater(max(abs(x) for x in even.v),1.)

    def test_printed_calibration_conflicts_remain_visible(self):
        # Eq.(25) row 2, at vi=0: -c2+c3=0. Eq.(31) agrees.
        c2,c3=printed_calibration_ratios(0.,.5,3.)
        self.assertAlmostEqual(c3,-c2)
        self.assertGreater(abs(-c2+c3),1.)
        # Printed Eq.(33), Rf=3, is outside the real arcsine domain.
        argument=(3.+1)/(3.-1)
        self.assertGreater(argument,1.)
        with self.assertRaises(ValueError):
            math.asin(argument)
        self.assertEqual(len(self.fragment['findings']),3)

    def test_undefined_inputs_are_rejected_without_floor(self):
        good=dict(stress=Sym((1e5,)*3+(0.,)*3),stretching=Sym((0.,)*6),coefficients=(-69.4,-673.1,-655.9,699.6))
        for patch in [dict(stress=Sym((0.,)*6)),dict(stress=Sym((1.,-1.,0.,0.,0.,0.))),dict(stress=Sym((1.,2.))),dict(stretching=Sym((math.inf,)*6)),dict(coefficients=(1.,2.,math.nan,4.)),dict(coefficients=(1.,2.,3.))]:
            with self.subTest(patch=patch),self.assertRaises(ValidationError):
                evaluate_fragment(self.fragment,**(good|patch))


if __name__=='__main__':
    unittest.main()
