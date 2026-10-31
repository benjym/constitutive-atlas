"""Independent Cartesian oracle for a source flow fragment; no material integration."""
import copy
import math
import random
import unittest
from atlas.dsl import Sym, ValidationError
from tools.inspect_pm4sand_flow import evaluate_flow, load_flow_fragment, validate_flow_fragment

ZERO = Sym((0.,)*6)


def mandel(a):
    return Sym((a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]))


def determinant(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
           -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
           +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def rotate(a):
    q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
    return [[sum(q[i][k]*a[k][l]*q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]


def cartesian_flow(delta,c,D):
    # No production tensor_square/cube_trace/norm/g implementation is called.
    norm=math.sqrt(sum(v*v for row in delta for v in row))
    n=[[v/norm for v in row] for row in delta]
    cosine=3*math.sqrt(6)*determinant(delta)/norm**3
    denominator=1-cosine+c**4*(1+cosine)
    # Substitute g^4=2*c^4/denominator before evaluating B and C.
    B=1+.75*(c**4-1)*cosine/denominator
    C=(3*math.sqrt(6)/4)*(c**4-1)/denominator
    square=[[sum(n[i][k]*n[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    deviator=[[B*n[i][j]-C*(square[i][j]-(1/3 if i==j else 0)) for j in range(3)] for i in range(3)]
    full=[[deviator[i][j]+(D/3 if i==j else 0) for j in range(3)] for i in range(3)]
    return B,C,deviator,full


class PM4SandFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fragment=load_flow_fragment()

    def assertSymClose(self,a,b,tolerance=2e-13):
        for x,y in zip(a.v,b.v):self.assertAlmostEqual(x,y,delta=tolerance)

    def flow(self,**changes):
        values=dict(r=Sym((2.,-1.,-1.,0.,0.,0.)),alpha=ZERO,c=.71,m=.01,D=.3)
        return evaluate_flow(self.fragment,**(values|changes))

    def test_source_identity_dependency_and_typed_dimension_checks(self):
        self.assertEqual(len(self.fragment['terms']),11)
        self.assertFalse(self.fragment['complete_constitutive_model'])
        self.assertEqual(self.fragment['independent_review'],'pending')
        for mutate in [lambda f:f['source'].update(sha256='0'*64),
                       lambda f:f['dependencies'][0].update(sha256='0'*64),
                       lambda f:f['inputs'].pop('D'),
                       lambda f:f['audit_domain'].update(c_min=.1),
                       lambda f:f['terms'][0].update(expression='r+alpha'),
                       lambda f:f['terms'][-1].update(expression='Rdev+D'),
                       lambda f:f['terms'][-1].update(unit='Pa')]:
            fragment=copy.deepcopy(self.fragment);mutate(fragment)
            with self.assertRaises(ValidationError):validate_flow_fragment(fragment)

    def test_compression_extension_and_circular_surface_reductions(self):
        for c in [.64,.71,.95,1.]:
            for sign in [-1.,1.]:
                for D in [-.8,0.,.6]:
                    result=self.flow(r=Sym((2*sign,-sign,-sign,0.,0.,0.)),c=c,D=D)
                    self.assertSymClose(result['Rdev'],result['n'])
                    self.assertAlmostEqual(sum(result['Rdev'].v[:3]),0.,delta=2e-14)
                    self.assertAlmostEqual(sum(result['R'].v[:3]),D,delta=2e-14)
                    if c<1:self.assertLess(result['C'],0.)
        general=Sym((.4,-.3,-.1,.6,-.2,.7))
        result=self.flow(r=general,c=1.)
        self.assertEqual(result['B'],1.);self.assertEqual(result['C'],0.)
        self.assertSymClose(result['Rdev'],result['n'])

    def test_cartesian_matrix_square_oracle_trace_and_oblique_covariance(self):
        rng=random.Random(20261101)
        for case in range(40):
            a,b,u,v,w=[rng.uniform(-1,1) for _ in range(5)]
            delta=[[a,u,w],[u,b,v],[w,v,-a-b]]
            alpha=[[.13,.07,-.03],[.07,-.04,.02],[-.03,.02,-.09]]
            r=[[delta[i][j]+alpha[i][j] for j in range(3)] for i in range(3)]
            for c in [.64,.71,1.]:
                for D in [-.4,0.,.7]:
                    B,C,dev,full=cartesian_flow(delta,c,D)
                    plain=self.flow(r=mandel(r),alpha=mandel(alpha),c=c,D=D)
                    rotated=self.flow(r=mandel(rotate(r)),alpha=mandel(rotate(alpha)),c=c,D=D)
                    with self.subTest(case=case,c=c,D=D):
                        self.assertAlmostEqual(plain['B'],B,delta=2e-13)
                        self.assertAlmostEqual(plain['C'],C,delta=2e-13)
                        self.assertSymClose(plain['Rdev'],mandel(dev))
                        self.assertSymClose(plain['R'],mandel(full))
                        self.assertSymClose(rotated['Rdev'],mandel(rotate(dev)))
                        self.assertSymClose(rotated['R'],mandel(rotate(full)))
                        self.assertAlmostEqual(sum(plain['Rdev'].v[:3]),0.,delta=2e-14)
                        self.assertAlmostEqual(sum(plain['R'].v[:3]),D,delta=2e-14)

    def test_direction_translation_scaling_and_supplied_D(self):
        delta=Sym((.4,-.3,-.1,.6,-.2,.7));alpha=Sym((-.1,.05,.05,.2,0.,0.))
        original=self.flow(r=delta,D=-.4)
        for scale in [1e-9,1.,1e9]:
            shifted=self.flow(r=(delta+alpha)*scale,alpha=alpha*scale,D=-.4)
            self.assertSymClose(shifted['Rdev'],original['Rdev'])
            self.assertSymClose(shifted['R'],original['R'])
        changed=self.flow(r=delta,D=.8)
        expected=Sym((.4,.4,.4,0.,0.,0.))
        self.assertSymClose(changed['R']-original['R'],expected)
        self.assertSymClose(changed['Rdev'],original['Rdev'])
        # General nonaxisymmetric Rdev is not normalized: do not erase its norm
        # to reconcile a separate dilatancy interpretation statement in Eq. 38.
        general=self.flow(r=Sym((1.,0.,-1.,0.,0.,0.)),c=.71)
        self.assertGreater(sum(x*x for x in general['Rdev'].v),1.01)

    def test_invalid_or_undefined_domain_remains_rejected(self):
        invalid=[dict(r=ZERO),dict(alpha=Sym((2.,-1.,-1.,0.,0.,0.))),
                 dict(c=.63),dict(c=1.01),dict(c=math.nan),dict(m=0.),
                 dict(r=Sym((1.,1.,1.,0.,0.,0.))),dict(alpha=Sym((.1,.1,.1,0.,0.,0.))),
                 dict(r=Sym((1.,2.))),dict(r=Sym((math.inf,-1.,-1.,0.,0.,0.))),
                 dict(r=Sym((2e-300,-1e-300,-1e-300,0.,0.,0.))),
                 dict(D=math.nan),dict(D=math.inf),dict(D=True),dict(D=Sym((0.,)*6))]
        for change in invalid:
            with self.subTest(change=change),self.assertRaises(ValidationError):self.flow(**change)

if __name__=='__main__':unittest.main()
