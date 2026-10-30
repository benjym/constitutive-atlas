"""Independent coordinates, complete acquisitions and missing thresholds."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from atlas.public_data import load_curated
from atlas.measurement_units import sanitize_units, comparison_metadata
from tools.ingest_torsion import read_torsion

ROOT = Path(__file__).resolve().parents[1]


class Leap2018Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {r['id']: r for r in load_curated(ROOT)
                       if r['provenance']['source_id'].startswith('leap-2018-')}

    def test_campaign_coverage_and_independent_coordinates(self):
        torsion = [r for r in self.records.values() if r['provenance']['source_id'] == 'leap-2018-torsion']
        dss = [r for r in self.records.values() if r['provenance']['source_id'] == 'leap-2018-dss']
        self.assertEqual(len(torsion), 74)
        self.assertEqual(len(dss), 17)
        history = self.records['LEAP-2018-TOR-DR50-0P19-LOADING']
        cycle = self.records['LEAP-2018-TOR-DR50-0P19-CYCLE']
        half = self.records['LEAP-2018-TOR-DR50-0P19-HALF-CYCLE']
        self.assertEqual([len(r['rows']) for r in (history, cycle, half)], [676, 7, 16])
        self.assertEqual(history['rows'][0]['c1'], 0)
        self.assertEqual(cycle['rows'][0]['c25'], 1)
        self.assertEqual(half['rows'][0]['c33'], .25)
        self.assertNotIn('c34', half['rows'][0])
        self.assertEqual(half['source_table']['values'][0][-1], '-')
        self.assertAlmostEqual(history['rows'][-1]['c13'], -2.4783279674292484)
        self.assertAlmostEqual(cycle['rows'][0]['c31'], .2001710683107376)
        for r in torsion + dss:
            self.assertFalse(r['initial'])
            self.assertEqual(comparison_metadata(r)['plots'], [])

    def test_full_raw_acquisition_and_deduplicated_aliases(self):
        raw = self.records['LEAP-2018-TOR-RAW-F036-LOADING']
        self.assertEqual(len(raw['rows']), 882)
        self.assertEqual(raw['rows'][0], dict(c1=1, c2=.016, c3=-.02, c4=6.6, c5=200.0273))
        self.assertEqual(raw['rows'][-1]['c1'], 882)
        common = self.records['LEAP-2018-TOR-RAW-F051-LOADING']
        self.assertEqual(len(common['provenance']['identical_source_paths']), 8)
        volume = self.records['LEAP-2018-TOR-RAW-F044-CONSOL']
        self.assertEqual(volume['columns'][1]['unit'], 'not specified')
        self.assertEqual(sanitize_units(volume)['columns'][1]['unit_status'], 'unresolved')

    def test_missing_liquefaction_threshold_and_source_specimen_names(self):
        r = self.records['LEAP-2018-TOR-DR60-STRENGTH']
        self.assertEqual(len(r['rows']), 5)
        self.assertNotIn('c15', r['rows'][0])  # 7.5% DA criterion not reached/reported
        self.assertEqual(r['rows'][0]['c13'], 622.9)
        self.assertEqual(r['source_table']['original_rows'][4][6], 'Dr60-0.12')
        self.assertEqual(r['rows'][1]['c15'], 68.4)
        dss = self.records['LEAP-2018-DSS-EO_0_59_SV_100_CSR_0_075']
        self.assertEqual(len(dss['rows']), 62500)
        self.assertEqual([c['unit'] for c in dss['columns']], ['cycles','%','kPa','%','kPa','kPa'])
        self.assertIn('c6', dss['rows'][-1])

    def test_raw_reader_rejects_acquisition_count_changes(self):
        # Apparatus sample numbers are coordinates, not elapsed seconds; absent
        # volume units must survive parsing instead of borrowing workbook units.
        cells = [['metadata'] for _ in range(17)]
        cells[7] = ['VERT_UNITS', '', 'mm']
        cells[15] = ['NUM_SAMPS', '2']
        cells[16] = ['', 'CH_1', 'CH_2']
        cells += [['1', '2.5', '-.1'], ['2', '2.7', '-.2']]
        text = io.StringIO(); csv.writer(text).writerows(cells)
        raw = text.getvalue().encode()
        file = dict(filename='raw.csv', sha256=hashlib.sha256(raw).hexdigest(), raw_acquisition=True,
                    original_headers=cells[16], original_units=cells[7], material='Fixture',
                    tables=[dict(id='RAW', sheet='acquisition', columns=[1,2,3], header_rows=[17],
                                 data_start=18, units={'1':'1','2':'not specified','3':'mm'},
                                 x=1,y=3,protocol='consolidation-apparatus-source')])
        source = dict(id='fixture', source_url='https://example.org',license='ODC-BY-1.0',
                      license_url='https://opendatacommons.org/licenses/by/1-0/',attribution='Fixture',files=[file])
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'raw.csv').write_bytes(raw)
            r = read_torsion(source, Path(tmp))[0]
            self.assertEqual(r['rows'][1], dict(c1=2,c2=2.7,c3=-.2))
            self.assertEqual(r['provenance']['original_headers'][0], '')
            cells[15][1] = '3'
            text = io.StringIO(); csv.writer(text).writerows(cells)
            changed = text.getvalue().encode()
            (Path(tmp)/'raw.csv').write_bytes(changed)
            file['sha256'] = hashlib.sha256(changed).hexdigest()
            with self.assertRaisesRegex(ValueError, 'count mismatch'):
                read_torsion(source, Path(tmp))
