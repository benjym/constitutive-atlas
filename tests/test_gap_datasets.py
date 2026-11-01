"""Release boundaries and quantity semantics for the November gap datasets."""
import gzip
import json
from pathlib import Path
import unittest

from atlas.measurement_units import comparison_metadata, sanitize_units

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {'estefania', 'newcastle-london-clay', 'bionics-clay-fill', 'polito-uniroma1'}


class GapDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        index = json.loads((ROOT / 'data/curated/index.json').read_text())
        cls.records = [json.loads(gzip.decompress((ROOT / 'data/curated' / e['path']).read_bytes()))
                       for e in index['records'] if e['source_id'] in SOURCES]

    def test_curve_families_and_no_unqualified_model_overlays(self):
        expected = {'estefania': 11, 'newcastle-london-clay': 3,
                    'bionics-clay-fill': 6, 'polito-uniroma1': 252}
        for source, count in expected.items():
            selected = [r for r in self.records if r['provenance']['source_id'] == source]
            self.assertEqual(len(selected), count)
            for r in selected:
                self.assertNotEqual(r['kind'], 'experiment')
                self.assertEqual(comparison_metadata(r)['plots'], [])
                self.assertEqual(r['provenance']['license'], 'CC-BY-4.0')
        polito = [r for r in self.records if r['provenance']['source_id'] == 'polito-uniroma1']
        self.assertEqual(sum(r['protocol'].startswith('resonant-column') for r in polito), 110)
        self.assertEqual(sum(r['protocol'].startswith('cyclic-double') for r in polito), 142)

    def test_si_arithmetic_preserves_order_missingness_and_sources(self):
        dimensions = {'%': ('1', .01), 'MPa': ('Pa', 1e6),
                      'kPa': ('Pa', 1000), 'mm': ('m', .001),
                      'Hz': ('Hz', 1), '1': ('1', 1)}
        for record in self.records:
            converted = sanitize_units(record)
            self.assertEqual(len(record['rows']), len(converted['rows']))
            for before, after in zip(record['columns'], converted['columns']):
                unit, factor = dimensions[before['unit']]
                self.assertEqual(after['unit'], unit)
                self.assertEqual(after['unit_status'], 'standardized')
                self.assertEqual(after['source_unit'], before['unit'])
                for source_row, target_row in zip(record['rows'], converted['rows']):
                    key = before['key']
                    self.assertEqual(key in source_row, key in target_row)
                    if key in source_row:
                        self.assertEqual(target_row[key], source_row[key] * factor)

    def test_predictions_and_distinct_physical_quantities_stay_separate(self):
        for record in self.records:
            source = record['provenance']['source_id']
            cols = {c['source_column'] for c in record['columns']}
            if source == 'newcastle-london-clay':
                self.assertTrue(cols <= {1, 2, 3, 4, 5, 6})
            elif source == 'bionics-clay-fill':
                self.assertTrue(cols <= set(range(13, 24)))
                self.assertIn('Change in Pore Pressure', record['columns'][1]['name'])
            elif source == 'polito-uniroma1':
                # Specimen context includes OCR, ei/ec and damping method,
                # not just the three opening header rows.
                context = record['provenance']['workbook_info']
                self.assertEqual(context[2][11], 'OCR')
                self.assertEqual(context[5][1], 'Soil material')
                self.assertTrue(record['material'].endswith(record['provenance']['sheet']))
            elif record['id'].startswith('ESTEFANIA-BE-'):
                self.assertEqual(record['columns'][0]['name'], "p'/p'ref")
                self.assertEqual(record['columns'][0]['unit'], '1')
            elif record['id'].startswith('ESTEFANIA-STIFFNESS-'):
                self.assertEqual(cols, {6, 7})


if __name__ == '__main__':
    unittest.main()
