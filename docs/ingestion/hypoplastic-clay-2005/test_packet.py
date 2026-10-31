import math
import unittest
from check_packet import coefficients, run_checks, ncl_void, equivalent_pressure, isotropic_rate


class BoundedChecks(unittest.TestCase):
    def test_all_analytical_identities(self):
        r = run_checks()
        self.assertTrue(r['passed'], [x for x in r['checks'] if not x['passed']])
        self.assertGreaterEqual(r['count'], 35)

    def test_parameter_rejections(self):
        for p in ((True, .11, .016, .4), (float('nan'), .11, .016, .4), (0, .11, .016, .4), (.4, .016, .11, .4), (.4, .11, .016, 0)):
            with self.subTest(p=p), self.assertRaises(ValueError):
                coefficients(*p)

    def test_ncl_inverse_across_scales(self):
        for p in (1, 1000, 1e6):
            e = ncl_void(p, 1.375, .11)
            self.assertAlmostEqual(equivalent_pressure(e, 1.375, .11) / p, 1, places=13)

    def test_zero_and_signed_initial_tangents(self):
        p, lam, kap = 500000, .11, .016
        e = ncl_void(p, 1.375, lam)
        for v in (-.003, 0, .003):
            pr, er = isotropic_rate(p, e, v, 1.375, lam, kap, .4, math.radians(22.6))
            slope = lam if v > 0 else kap
            self.assertAlmostEqual(pr / p, v / slope, places=13)
            self.assertEqual(er, -(1 + e) * v)

    def test_negative_c2_is_not_itself_invalid(self):
        c = coefficients(math.radians(22.6), .11, .016, .1)
        self.assertLess(c['c2'], 0)
        # At H=I/3 the complete L remains positive definite.
        self.assertGreater(c['c1'], 0)
        self.assertGreater(c['c1'] + c['c2'] * c['a'] ** 2 / 3, 0)
        # Near rank-one compression this parameter set loses positivity.
        self.assertLess(c['c1'] + c['c2'] * c['a'] ** 2, 0)

    def test_density_zero_is_not_invariant_boundary(self):
        _, er = isotropic_rate(1000, 0, .001, 1.375, .11, .016, .4, math.radians(22.6))
        self.assertLess(er, 0)  # Must reject a crossing; never invent e clipping.


if __name__ == '__main__':
    unittest.main()
