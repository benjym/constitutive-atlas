import unittest

from tools.map_private_workbooks import extract


def row(n, *cells):
    return dict(excel_row=n, cells=list(cells))


class PrivateWorkbookMappingsTest(unittest.TestCase):
    def test_missing_units_do_not_create_strain_axis(self):
        blocks = extract([row(2, 'epax=dh/h0', "p' [kPa]", 'q [kPa]'),
                          row(3, .5, 100, 20)])
        self.assertEqual(blocks[0]['candidate_axes'], [
            dict(x='effective_mean_stress', y='deviatoric_stress')])
        self.assertEqual(blocks[0]['rows'][0]['values'], {'1': 100000, '2': 20000})

    def test_duplicate_oedometer_headers_withhold_axes(self):
        blocks = extract([row(2, 'eps = dh/h0 [-]', 'eps = dh/h0 [-]'), row(3, 100, .01)])
        self.assertEqual(blocks[0]['candidate_axes'], [])
        self.assertTrue(blocks[0]['warnings'])

    def test_no_zero_fill_or_cross_block_pairing(self):
        blocks = extract([row(2, 'epax=dh/h0 [%]', 'q [kPa]'),
                          row(3, 0, None), row(4, None, 20),
                          row(5, 'epax=dh/h0 [%]', 'q [kPa]'), row(6, 1, 10)])
        self.assertEqual(blocks[0]['candidate_axes'], [])
        self.assertEqual(blocks[1]['candidate_axes'], [dict(x='axial_strain', y='deviatoric_stress')])
        self.assertEqual(blocks[1]['rows'][0]['values'], {'0': .01, '1': 10000})
        self.assertEqual(blocks[0]['rows'][0]['native'], {'0': 0})

    def test_unspecified_stress_is_not_effective_stress(self):
        blocks = extract([row(1, 'p [kPa]', 'q [kPa]'), row(2, 100, 20)])
        self.assertEqual(blocks[0]['candidate_axes'], [])
        self.assertEqual(blocks[0]['columns'][0]['quantity'], 'mean_stress_unspecified')

    def test_unknown_unit_does_not_supply_axis(self):
        blocks = extract([row(1, 'epax=dh/h0 [unknown]', 'q [kPa]'), row(2, 2, 20)])
        self.assertEqual(blocks[0]['candidate_axes'], [])
        self.assertEqual(blocks[0]['rows'][0]['native']['0'], 2)
        self.assertNotIn('0', blocks[0]['rows'][0]['values'])

    def test_duplicate_quantity_with_different_units_is_ambiguous(self):
        blocks = extract([row(1, 'epax=dh/h0 [%]', 'q [kPa]', 'q [unknown]'), row(2, 2, 20, 30)])
        self.assertEqual(blocks[0]['candidate_axes'], [])


if __name__ == '__main__':
    unittest.main()
