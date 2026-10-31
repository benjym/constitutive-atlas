"""Unit arithmetic must not invent physical meanings or destroy source evidence."""
import unittest
from atlas.measurement_units import sanitize_units, comparison_metadata


class MeasurementUnitTests(unittest.TestCase):
    def test_conversions_preserve_sources_and_missing_values(self):
        record = dict(kind='measurement-series', columns=[
            dict(key='c1', name='Stress', unit='MPa'),
            dict(key='c2', name='Strain', unit='%'),
            dict(key='c3', name='Temperature', unit='\\circC'),
            dict(key='c4', name='Unknown', unit='not specified'),
            dict(key='c5', name='Log stress', unit='ln(source kPa)'),
        ], rows=[dict(c1=.2, c2=-2, c3=0, c4=17, c5=4), dict(c1=.3)])
        result = sanitize_units(record)
        self.assertEqual(result['rows'][0], dict(c1=200000, c2=-.02, c3=273.15, c4=17, c5=4))
        self.assertEqual(result['rows'][1], dict(c1=300000))
        self.assertEqual(record['rows'][0]['c1'], .2)
        self.assertEqual(result['columns'][0]['source_unit'], 'MPa')
        self.assertEqual(result['columns'][0]['unit'], 'Pa')
        self.assertEqual(result['columns'][3]['unit_status'], 'unresolved')
        self.assertEqual(result['columns'][4]['unit_status'], 'unresolved')
        self.assertEqual(comparison_metadata(result)['plots'], [])

    def test_scale_factors_across_dimensions(self):
        cases = [('kPa', 2, 2000), ('lbf', 1, 4.4482216152605),
                 ('mm', 10, .01), ('mm^2', 100, .0001),
                 ('(mm3)', 1000, 1e-6), ('cm^3', 1, 1e-6),
                 ('min', 2, 120), ('ms', 2, .002), ('h', 1, 3600),
                 ('%/h', 3600, .01), ('mm/mm', -.02, -.02),
                 ('kN/m2', -2, -2000), ('ml', 2, 2e-6),
                 ('deg', 180, 3.141592653589793), ('N・m', -2, -2)]
        for unit, value, expected in cases:
            with self.subTest(unit=unit):
                record = dict(kind='measurement-series', columns=[dict(key='c1', name='Signal', unit=unit)], rows=[dict(c1=value)])
                self.assertAlmostEqual(sanitize_units(record)['rows'][0]['c1'], expected)

    def test_unit_conversion_does_not_establish_effective_stress(self):
        r = dict(kind='measurement-series', columns=[dict(key='c1', name='Pressure', unit='kPa')], rows=[dict(c1=10)])
        self.assertEqual(comparison_metadata(sanitize_units(r)), dict(plots=[], loading='unreviewed'))

    def test_only_paired_axes_and_observed_loading_direction(self):
        record = dict(kind='experiment', rows=[dict(axial_strain=0, q=0), dict(axial_strain=.01, q=100, p=1000)])
        self.assertEqual(comparison_metadata(record), dict(plots=['stress', 'path'], loading='monotonic'))
        record['rows'].append(dict(axial_strain=0, q=-20))
        self.assertEqual(comparison_metadata(record)['loading'], 'reversing')
