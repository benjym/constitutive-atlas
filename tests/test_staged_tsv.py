"""Stage boundaries and source history must survive public-data extraction."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.ingest_staged_tsv import read_staged_tsv


class StagedTSVTests(unittest.TestCase):
    def read(self, data, **changes):
        encoded = data.encode('utf-16')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('history.txt', encoded)
            config = dict(member='history.txt', sha256=hashlib.sha256(encoded).hexdigest(),
                          encoding='utf-16', headers=['time [h]', 'strain [%]', 'procedure'],
                          units=['h', '%'], expected_observations=4, specimen='A', phase='shear',
                          id_prefix='TEST-A', protocol='creep-source', boundary_conditions={})
            config.update(changes)
            file = dict(filename=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        material='Clay', readme_url='https://example.com/readme',
                        readme_sha256='0'*64, tables=[config])
            source = dict(id='test', source_url='https://example.com', license='CC0-1.0',
                          license_url='https://creativecommons.org/publicdomain/zero/1.0/',
                          attribution='Test fixture', files=[file])
            return read_staged_tsv(source, Path(directory))

    def test_stage_split_preserves_time_origin_order_and_unlabeled_data(self):
        records = self.read('time [h]\tstrain [%]\tprocedure\n5\t0\tramp\n6\t1\tramp\n\t\t\n7\t2\t\n8\t3\thold\n')
        self.assertEqual([r['provenance']['source_stage_label'] for r in records], ['ramp', '', 'hold'])
        self.assertEqual([r['provenance']['source_rows'] for r in records], [[2, 3], [5], [6]])
        self.assertEqual([r['provenance']['blank_source_lines'] for r in records], [[4]]*3)
        self.assertEqual([row for r in records for row in r['rows']],
                         [{'c1':5., 'c2':0.}, {'c1':6., 'c2':1.}, {'c1':7., 'c2':2.}, {'c1':8., 'c2':3.}])
        self.assertEqual(records[1]['source_table']['values'], [[5, 7., 2., '']])

    def test_numeric_final_column_is_retained_when_no_stage_column_exists(self):
        records = self.read('time [h]\tstrain [%]\tprocedure\n5\t1\t30\n6\t2\t31\n',
                            stage_column=0, units=['h', '%', '°C'], expected_observations=2)
        self.assertIsNone(records[0]['provenance']['source_stage_label'])
        self.assertEqual(records[0]['rows'], [{'c1':5., 'c2':1., 'c3':30.}, {'c1':6., 'c2':2., 'c3':31.}])
        self.assertEqual(records[0]['source_table']['units'], ['1', 'h', '%', '°C'])

    def test_decreasing_time_and_nonfinite_measurements_fail(self):
        for data in ['time [h]\tstrain [%]\tprocedure\n1\t0\ta\n0\t1\tb\n',
                     'time [h]\tstrain [%]\tprocedure\n1\tNaN\ta\n']:
            with self.assertRaises(ValueError):
                self.read(data)

    def test_unreviewed_layout_fails(self):
        with self.assertRaisesRegex(ValueError, 'header'):
            self.read('wrong\tstrain [%]\tprocedure\n1\t2\ta\n')


if __name__ == '__main__':
    unittest.main()
