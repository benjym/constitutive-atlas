import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.compression_protocol import first_loading_diagnostics


def specimen():
    # Reference height 100 mm, solid-equivalent height 50 mm. Three loading
    # observations, a hold at peak, unloading, and reloading above the old peak.
    heights = [100, 99, 96, 96, 98, 95]
    stresses = [0, 2000, 100000, 100000, 1000, 120000]
    return dict(id='KFS-OE1', protocol='oedometer', rows=[
        dict(axial_stress=stress, axial_strain=(100-height)/100,
             void_ratio=height/50-1, source_line=i+4)
        for i, (height, stress) in enumerate(zip(heights, stresses))])


class CompressionProtocolTests(unittest.TestCase):
    def test_reference_height_geometry_and_native_continuity_are_distinct(self):
        record = specimen()
        result = first_loading_diagnostics(record, [1000])
        scenario = result['scenarios'][0]
        self.assertEqual(scenario['start_axial_stress_Pa'], 2000)
        self.assertAlmostEqual(scenario['engineering_strain_increment'], .03)
        self.assertAlmostEqual(scenario['logarithmic_height_strain_increment'], math.log(99/96))
        self.assertAlmostEqual(scenario['geometry_end_void_ratio'], .92)
        self.assertAlmostEqual(scenario['geometry_end_void_ratio_residual'], 0)
        self.assertAlmostEqual(scenario['engineering_driven_continuity_end_void_ratio'], 1.98*math.exp(-.03)-1)
        self.assertGreater(scenario['engineering_driven_end_void_ratio_residual'], .001)

    def test_peak_hold_retained_and_later_higher_reloading_peak_excluded(self):
        record = specimen()
        original = copy.deepcopy(record)
        result = first_loading_diagnostics(record, [1000])
        self.assertEqual(result['first_loading_end_index'], 3)
        self.assertEqual(result['scenarios'][0]['observations'], 3)
        self.assertEqual(result['later_observations_excluded_from_this_diagnostic'], 2)
        self.assertEqual(record, original)

    def test_no_interval_does_not_interpolate_or_take_later_peak(self):
        result = first_loading_diagnostics(specimen(), [110000])
        self.assertEqual(result['scenarios'][0]['status'], 'no_nonzero_first_loading_interval')

    def test_reserved_id_rejected_before_response_access(self):
        with self.assertRaisesRegex(ValueError, 'reserved final'):
            first_loading_diagnostics(dict(id='KFS-OE2'), [1000])

    def test_invalid_volume_coordinate_and_threshold_rejected(self):
        for invalid in (1, -0.1, float('nan')):
            record = specimen()
            record['rows'][1]['axial_strain'] = invalid
            with self.assertRaises(ValueError):
                first_loading_diagnostics(record, [1000])
        for threshold in (0, -1, float('inf')):
            with self.assertRaises(ValueError):
                first_loading_diagnostics(specimen(), [threshold])

    def test_strain_reversal_on_first_stress_loading_needs_review(self):
        record = specimen()
        record['rows'][2]['axial_strain'] = .005
        with self.assertRaisesRegex(ValueError, 'decreasing strain'):
            first_loading_diagnostics(record, [1000])


if __name__ == '__main__':
    unittest.main()
