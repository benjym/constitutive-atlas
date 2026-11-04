"""Keep source inconsistencies visible instead of inventing validation curves."""
import gzip
import json
from pathlib import Path
import unittest

from atlas.measurement_units import sanitize_units, comparison_metadata

ROOT = Path(__file__).resolve().parents[1]


class ShaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        entries = json.loads((ROOT/'data/curated/index.json').read_text())['records']
        cls.records = {e['id']: json.loads(gzip.decompress((ROOT/'data/curated'/e['path']).read_bytes()))
                       for e in entries if e['source_id'] == 'shale'}

    def test_coverage_and_pressure_duplicate(self):
        self.assertEqual(len(self.records), 13)
        self.assertEqual(sum(len(r['rows']) for r in self.records.values()), 2584)
        self.assertNotIn('SHALE-WATER-3MPA-STRAIN', self.records)
        r = self.records['SHALE-WATER-2MPA-STRAIN']
        self.assertTrue(any('cell-for-cell identical' in w for w in r['warnings']))
        for r in self.records.values():
            self.assertEqual(comparison_metadata(r)['plots'], [])
            self.assertFalse(r['initial'])
            self.assertEqual(r['provenance']['license'], 'CC0-1.0')

    def test_independent_time_coordinates(self):
        stress = self.records['SHALE-WATER-1MPA-STRESS-TIME']
        flow = self.records['SHALE-WATER-1MPA-FLOW-TIME']
        self.assertEqual(stress['rows'][0], dict(c1=0, c2=0))
        self.assertEqual(flow['rows'][0], dict(c3=341.6, c4=0))
        self.assertEqual(stress['rows'][-1]['c1'], 48)
        self.assertEqual(flow['rows'][-1]['c3'], 819)
        self.assertEqual([len(self.records['SHALE-WATER-3MPA-'+name]['rows'])
                          for name in ('STRESS-TIME','FLOW-TIME')], [478,32])
        self.assertEqual(flow['source_plot'], dict(x='c3', y='c4'))

    def test_unaligned_channels_and_missing_markers(self):
        r = self.records['SHALE-WATER-2MPA-VOLUME']
        self.assertEqual(len(r['rows']), 396)
        self.assertEqual(sum('c2' in row for row in r['rows']), 268)
        self.assertEqual(r['source_plot'], dict(x='c2', y='c3'))
        self.assertTrue(all('c4' not in row for row in r['rows']))
        original = dict((row[0], row[1:]) for row in r['source_table']['original_rows'])
        self.assertEqual(original[31][-1], '--')
        self.assertEqual(original[3][-1], .0492)
        self.assertNotIn('c2', r['rows'][-1])

    def test_reviewed_units_and_swapped_failure_labels(self):
        seepage = self.records['SHALE-SEEPAGE']
        converted = sanitize_units(seepage)
        self.assertEqual(seepage['rows'][0]['c4'], 1.42202)
        self.assertAlmostEqual(converted['rows'][0]['c4']/1e-16, 1.42202)
        self.assertAlmostEqual(converted['rows'][1]['c1'], .00132/100)
        flow = sanitize_units(self.records['SHALE-WATER-1MPA-FLOW-TIME'])
        self.assertAlmostEqual(flow['rows'][1]['c4'], .1687/1000)
        dp = self.records['SHALE-FAILURE-I-J']
        mc = self.records['SHALE-FAILURE-TAU-SIGMA']
        self.assertEqual(dp['rows'][0], dict(c1=108.85759,c2=55.26617))
        self.assertEqual(mc['rows'][0], dict(c1=45.12464,c2=50.42879))
        self.assertEqual(mc['source_plot'], dict(x='c2', y='c1'))
        for r in (dp,mc):
            self.assertEqual(r['kind'], 'test-summary')
            self.assertEqual(len(r['rows']), 4)
            self.assertTrue(any('swapped' in w for w in r['warnings']))
