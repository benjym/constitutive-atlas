"""Python-only source-fragment checks against separate Cartesian algebra."""
import math
import random
import unittest

from atlas.dsl import Sym, ValidationError
from tools.inspect_pm4sand_surfaces import evaluate_fragment, load_fragment


def mandel(a):
    return Sym((a[0][0], a[1][1], a[2][2], math.sqrt(2)*a[0][1],
                math.sqrt(2)*a[1][2], math.sqrt(2)*a[0][2]))


def determinant(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            - a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            + a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def rotate(a):
    # Exact rational orthogonal frame; all directions mix normal/shear components.
    q = [[1/3, 2/3, 2/3], [2/3, 1/3, -2/3], [-2/3, 2/3, -1/3]]
    return [[sum(q[i][k]*a[k][l]*q[j][l] for k in range(3) for l in range(3))
             for j in range(3)] for i in range(3)]


class PM4SandSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fragment = load_fragment()  # Checks all DSL types and pinned source identity.

    def test_axisymmetric_endpoints_and_shear(self):
        zero = Sym((0.,)*6)
        for c in [.64, .71, .95, 1.]:
            for r, cosine, expected in [
                (Sym((2., -1., -1., 0., 0., 0.)), 1., 1.),
                (Sym((-2., 1., 1., 0., 0., 0.)), -1., c),
                (Sym((0., 0., 0., 1., 0., 0.)), 0., c*(2/(1+c**4))**.25),
            ]:
                result = evaluate_fragment(self.fragment, r=r, alpha=zero, c=c, m=.01)
                self.assertAlmostEqual(result['cos3theta'], cosine, delta=2e-15)
                self.assertAlmostEqual(result['g'], expected, delta=3e-15)

    def test_oblique_tensors_against_cartesian_determinant(self):
        rng = random.Random(20261031)
        for case in range(40):
            a, b, u, v, w = [rng.uniform(-1., 1.) for _ in range(5)]
            delta = [[a,u,w], [u,b,v], [w,v,-a-b]]
            alpha = [[.13,.07,-.03], [.07,-.04,.02], [-.03,.02,-.09]]
            norm = math.sqrt(sum(x*x for row in delta for x in row))
            # For trace-free 3x3 matrices, tr(A^3)=3 det(A). No production tensor functions.
            cosine = 3*math.sqrt(6)*determinant(delta)/norm**3
            for c in [.64, .71, 1.]:
                # Algebraically rearranged fourth-root equation, distinct from the DSL AST.
                expected_g = (2*c**4/(1-cosine+c**4*(1+cosine)))**.25
                outputs = []
                for d, back in [(delta, alpha), (rotate(delta), rotate(alpha))]:
                    r = [[d[i][j]+back[i][j] for j in range(3)] for i in range(3)]
                    result = evaluate_fragment(self.fragment, r=mandel(r), alpha=mandel(back), c=c, m=.02)
                    with self.subTest(case=case, c=c):
                        self.assertAlmostEqual(result['cos3theta'], cosine, delta=4e-15)
                        self.assertAlmostEqual(result['g'], expected_g, delta=5e-15)
                        self.assertAlmostEqual(result['distance'], norm, delta=2e-15)
                        self.assertAlmostEqual(result['yield_distance'], norm-math.sqrt(2/3)*.02, delta=2e-15)
                        expected_M = math.sqrt(1.5*sum(x*x for row in r for x in row))
                        self.assertAlmostEqual(result['M_current'], expected_M, delta=2e-15)
                    outputs.append(result)
                self.assertAlmostEqual(outputs[0]['g'], outputs[1]['g'], delta=5e-15)

    def test_backstress_direction_and_scale_are_preserved(self):
        # Lode direction uses r-alpha, not r. A translation must not alter that direction.
        alpha = Sym((-.1,.05,.05,.2,0.,0.))
        delta = Sym((2.,-1.,-1.,0.,0.,0.))
        zero = Sym((0.,)*6)
        for scale in [1e-9, 1., 1e9]:
            result = evaluate_fragment(self.fragment, r=(alpha+delta)*scale,
                                       alpha=alpha*scale, c=.71, m=.01)
            plain = evaluate_fragment(self.fragment, r=delta*scale, alpha=zero, c=.71, m=.01)
            self.assertAlmostEqual(result['g'], 1., delta=3e-15)
            self.assertAlmostEqual(result['cos3theta'], plain['cos3theta'], delta=2e-15)

    def test_undefined_or_out_of_scope_inputs_fail_without_a_floor(self):
        zero = Sym((0.,)*6)
        valid = dict(r=Sym((2.,-1.,-1.,0.,0.,0.)), alpha=zero, c=.71, m=.01)
        bad = [dict(r=zero), dict(alpha=valid['r']), dict(c=.63), dict(c=1.01), dict(m=0.),
               dict(c=math.nan), dict(r=Sym((1.,1.,1.,0.,0.,0.))),
               dict(alpha=Sym((.1,.1,.1,0.,0.,0.))), dict(r=Sym((1.,2.))),
               dict(r=Sym((math.inf,-1.,-1.,0.,0.,0.))),
               dict(r=valid['r']*1e-300)]
        for change in bad:
            with self.subTest(change=change), self.assertRaises(ValidationError):
                evaluate_fragment(self.fragment, **(valid | change))


if __name__ == '__main__':
    unittest.main()
