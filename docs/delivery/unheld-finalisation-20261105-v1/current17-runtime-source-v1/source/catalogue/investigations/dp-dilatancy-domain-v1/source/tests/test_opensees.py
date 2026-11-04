import math
import random
import unittest

from atlas import opensees as o


class OpenSeesConventionsTests(unittest.TestCase):
    def assertVectorClose(self, a, b):
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, y, delta=1e-11*max(1, abs(x), abs(y)))

    def test_cartesian_work_and_sign_in_all_shears(self):
        # Independent Cartesian contraction includes each off-diagonal twice.
        stress = [[120., 13., -9.], [13., 80., 7.], [-9., 7., 100.]]
        strain = [[.01, -.003, .004], [-.003, -.002, .005], [.004, .005, .006]]
        sigma = [120000., 80000., 100000., math.sqrt(2)*13000.,
                 math.sqrt(2)*7000., -math.sqrt(2)*9000.]
        eps = [.01, -.002, .006, -math.sqrt(2)*.003,
               math.sqrt(2)*.005, math.sqrt(2)*.004]
        external_sigma = o.stress_to_opensees(sigma, pressure_unit_pa=1000)
        external_eps = o.strain_to_opensees(eps)
        self.assertVectorClose(external_sigma, [-120, -80, -100, -13, -7, 9])
        self.assertVectorClose(external_eps, [-.01, .002, -.006, .006, -.01, -.008])
        cartesian_work = 1000*sum(stress[i][j]*strain[i][j] for i in range(3) for j in range(3))
        self.assertAlmostEqual(sum(x*y for x, y in zip(sigma, eps)), cartesian_work)
        self.assertAlmostEqual(1000*sum(x*y for x, y in zip(external_sigma, external_eps)), cartesian_work)

    def test_full_nonsymmetric_tangent_chain_rule(self):
        rng = random.Random(204)
        for unit in (1, 1000, 1e6):
            for _ in range(20):
                C = [[rng.uniform(-30, 30) for _ in range(6)] for _ in range(6)]
                de = [rng.uniform(-.1, .1) for _ in range(6)]
                C_m = o.tangent_from_opensees(C, pressure_unit_pa=unit)
                de_ext = o.strain_to_opensees(de)
                ds_ext = [sum(a*b for a, b in zip(row, de_ext)) for row in C]
                expected = o.stress_from_opensees(ds_ext, pressure_unit_pa=unit)
                self.assertVectorClose([sum(a*b for a, b in zip(row, de)) for row in C_m], expected)
                for a, b in zip(o.tangent_to_opensees(C_m, pressure_unit_pa=unit), C):
                    self.assertVectorClose(a, b)

    def test_isotropic_engineering_shear_becomes_two_G(self):
        K, G = 120., 45.
        C = [[(K-2*G/3)+(2*G if i == j else 0) if i < 3 and j < 3
              else G if i == j else 0 for j in range(6)] for i in range(6)]
        result = o.tangent_from_opensees(C, pressure_unit_pa=1000)
        for i in range(3, 6):
            self.assertAlmostEqual(result[i][i], 90000.)

    def test_roundtrips_and_internal_dimensionless_history(self):
        v = [1, -2, 3, -4, 5, -6]
        self.assertVectorClose(o.internal_tensor_to_mandel(o.mandel_to_internal_tensor(v)), v)
        self.assertVectorClose(o.strain_from_opensees(o.strain_to_opensees(v)), v)
        for unit in (1, 1000):
            self.assertVectorClose(o.stress_from_opensees(o.stress_to_opensees(v, pressure_unit_pa=unit), pressure_unit_pa=unit), v)

    def test_invalid_boundary_values(self):
        for v in ([0]*5, [0]*7, [0]*5+[math.nan], [math.inf]*6):
            with self.assertRaises(ValueError):
                o.strain_from_opensees(v)
        for unit in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                o.stress_to_opensees([0]*6, pressure_unit_pa=unit)
        with self.assertRaises(ValueError):
            o.tangent_from_opensees([[0]*6]*5, pressure_unit_pa=1)


if __name__ == '__main__':
    unittest.main()
