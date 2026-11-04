import gzip
import json
from pathlib import Path
import tempfile
import unittest

from tools.map_private_text_tables import columns_for, family, iter_mapped_rows, residual_checks, role


class PrivateTextMappingTests(unittest.TestCase):
    def test_missing_stress_units_remain_missing(self):
        columns = columns_for(['N\tuacc/p0\tp\tq\teps_1 [%]'])
        self.assertTrue(all(c['conversion'] is None for c in columns[:4]))
        self.assertEqual(columns[4]['conversion']['scale'], .01)

    def test_numeric_identity_does_not_relabel_source_p(self):
        columns = columns_for(["eps1 u sigma3 sigma3' sigma1 sigma1' p q",
                               '[%] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa]'])
        checks = residual_checks(columns)
        row = [1, 100, 150, 50, 180, 80, 60, 30]
        self.assertEqual(checks['q_equals_axial_minus_radial'](row), 0)
        self.assertEqual(checks['p_equals_total_mean_minus_pore_pressure'](row), 0)
        self.assertEqual(checks['p_equals_total_mean'](row), -100)
        self.assertEqual(checks['p_equals_effective_mean'](row), 0)
        self.assertEqual(checks['q_equals_effective_axial_minus_radial'](row), 0)
        self.assertEqual(columns[6]['quantity'], 'mean_stress_unspecified')

    def test_cycle_summary_and_stages_stay_distinct(self):
        self.assertEqual(role('strain-cycles/C43-test-data-vs-N.dat'), 'cycle_summary')
        self.assertEqual(role('strain-cycles/C43-test-data-vs-time.dat'), 'cyclic_history')
        self.assertEqual(role('UCT15_Preloading.dat'), 'preloading_stage')
        self.assertEqual(role('UCT15_Shearing.dat'), 'shearing_stage')
        self.assertEqual(family('soilmodels-karlsruhe-kaolin','a/C01-test-data-vs-N.dat'),
                         family('soilmodels-karlsruhe-kaolin','b/C01-test-data-vs-time.dat'))
        self.assertNotEqual(family('soilmodels-zbraslav','Paper1/UCT1.dat'),
                            family('soilmodels-zbraslav','Paper2/UCT1.dat'))

    def test_stream_retains_native_and_coordinates(self):
        columns = columns_for(['N\tuacc/p0\tp\tq\teps_1 [%]'])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input.gz'
            with gzip.open(path,'wt') as f:
                for r in [dict(metadata={}),dict(source_line=1,source_text='header'),
                          dict(source_line=2,native=[0,.2,100,20,1])]:
                    f.write(json.dumps(r)+'\n')
            rows=list(iter_mapped_rows(path,columns))
        self.assertEqual(rows,[dict(source_line=2,native=[0,.2,100,20,1],values={'c4':.01})])

    def test_unknown_header_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unreviewed'):
            columns_for(['new measurements [kPa]'])

    def test_changed_unit_line_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unreviewed'):
            columns_for(["eps1 u sigma3 sigma3' sigma1 sigma1' p q",
                         '[-] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa]'])


if __name__ == '__main__':
    unittest.main()
