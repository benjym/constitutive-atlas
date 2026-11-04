"""Measured source blocks stay separate from fits, aliases and sensor guesses."""
import gzip
import json
from pathlib import Path
import unittest

from atlas.measurement_units import sanitize_units, comparison_metadata

ROOT = Path(__file__).resolve().parents[1]


class PrintedGrainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {e['id']: json.loads(gzip.decompress((ROOT/'data/curated'/e['path']).read_bytes()))
                       for e in json.loads((ROOT/'data/curated/index.json').read_text())['records']
                       if e['source_id'] == 'printed-grains'}

    def test_complete_acquisition_and_independent_comparator(self):
        self.assertEqual(len(self.records), 2)
        raw = self.records['PRINTED-GRAINS-OED-ACQUISITION']
        sand = self.records['PRINTED-GRAINS-REAL-SAND-COMPARATOR']
        self.assertEqual(len(raw['rows']), 8032)
        self.assertEqual(len(sand['rows']), 2138)
        self.assertEqual(raw['provenance']['source_rows'][0], 16)
        self.assertEqual(raw['provenance']['source_rows'][-1], 8047)
        self.assertEqual(raw['rows'][0]['c13'], .351549)
        self.assertEqual(raw['rows'][-1]['c14'], 2.043591)
        self.assertEqual(sand['rows'][0], dict(c41=4.15268,c42=0,c43=0,c44=.817))
        self.assertNotIn(1745, sand['provenance']['source_rows'])
        self.assertEqual(raw['source_plot'], dict(x='c14', y='c13'))
        self.assertEqual(sand['source_plot'], dict(x='c42', y='c41'))
        for r in (raw,sand):
            self.assertFalse(r['initial'])
            self.assertEqual(comparison_metadata(r)['plots'], [])
            self.assertNotIn('c17', r['rows'][0])  # Fitted stress is not an observation.

    def test_scan_markers_and_unresolved_sensor_units_survive(self):
        raw = self.records['PRINTED-GRAINS-OED-ACQUISITION']
        self.assertEqual(sum('c2' in r for r in raw['rows']), 18)
        self.assertEqual(raw['rows'][22]['c2'], 2)
        self.assertEqual(raw['rows'][0]['c9'], .280032)
        self.assertEqual(raw['source_table']['values'][0][6], ' 0,280032 ')
        converted = sanitize_units(raw)
        units = {c['key']:c for c in converted['columns']}
        for key in ('c5','c7','c8','c9'):
            self.assertEqual(units[key]['unit_status'], 'unresolved')
            self.assertEqual(converted['rows'][0][key], raw['rows'][0][key])
        self.assertEqual(converted['rows'][0]['c13'], 351.549)
        self.assertAlmostEqual(converted['rows'][0]['c14'], -.001225/100)
        self.assertAlmostEqual(converted['rows'][0]['c10'], 64304.487852e-6)
        self.assertAlmostEqual(converted['rows'][22]['c12'], .25e-6)
        self.assertTrue(any('compliance' in w for w in raw['warnings']))
        self.assertTrue(any('source-calculated' in w for w in raw['warnings']))
