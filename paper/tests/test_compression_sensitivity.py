import copy
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from analysis.atlas_adapter import NativeAdapter
from analysis.common import ROOT, read_json
from run_compression_sensitivity import summarize, validate_config


class CompressionScheduleTests(unittest.TestCase):
    def setUp(self):
        self.config = read_json(ROOT/'paper/study/compression_sensitivity.json')

    def records(self):
        records = []
        for model, ratio, coordinate, spacing in itertools.product(self.config['model_ids'],
                self.config['initial_radial_to_axial_stress_ratios'], self.config['coordinates'],
                self.config['maximum_increments']):
            stress = ratio*10+5*(coordinate == 'log_height_increment')+60*spacing
            points = [dict(observation_index=i, axial_stress=stress, imposed_axial_coordinate=x,
                           void_ratio=1.8*math.exp(-x)-1) for i, x in enumerate([0., .01])]
            records.append(dict(experiment_id='synthetic', model_id=model, minimum_stress_Pa=1000,
                initial_stress_ratio=ratio, coordinate=coordinate, maximum_increment=spacing,
                source_lines=[4, 5], initial_void_ratio=.8,
                prediction=dict(status='success', points=points)))
        return records

    def test_missing_and_duplicate_cases_cannot_improve_complete_aggregate(self):
        records = self.records()
        for invalid in (records[:-1], records+[records[0]]):
            with self.assertRaisesRegex(ValueError, 'schedule'):
                summarize(invalid, self.config)

    def test_failure_retained_and_prevents_sensitivity_aggregate(self):
        records = self.records()
        records[0]['prediction'] = dict(status='integration_failure', points=[])
        summary = summarize(records, self.config)
        failed = next(r for r in summary if r['model_id'] == records[0]['model_id'])
        self.assertEqual(failed['successful_replays'], failed['requested_replays']-1)
        self.assertNotIn('maximum_coordinate_scenario_difference_Pa', failed)

    def test_pairing_holds_other_factors_fixed(self):
        summary = summarize(self.records(), self.config)
        for item in summary:
            self.assertAlmostEqual(item['maximum_initial_stress_scenario_difference_Pa'], 6.5)
            self.assertAlmostEqual(item['maximum_coordinate_scenario_difference_Pa'], 5.)
            self.assertAlmostEqual(item['maximum_step_refinement_difference_Pa'], .015)
            self.assertAlmostEqual(item['maximum_numerical_void_ratio_continuity_difference'], 0.)
        records = self.records()
        records[0]['source_lines'].reverse()
        with self.assertRaisesRegex(ValueError, 'observations'):
            summarize(records, self.config)

    def test_no_fit_selection_and_refinement_required(self):
        for key, invalid in [('parameter_selection', 'best_fit'), ('maximum_increments', [.001, .002]),
                             ('initial_radial_to_axial_stress_ratios', [.5, .5])]:
            config = copy.deepcopy(self.config)
            config[key] = invalid
            with self.assertRaises(ValueError):
                validate_config(config)


@unittest.skipUnless((ROOT/'build/atlas_solver').exists(), 'build native solver for adapter verification')
class OedometerAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = NativeAdapter(ROOT/'build/atlas_solver', ['linear-elastic'])
        self.parameters = dict(p_ref=1e5, E=1e7, nu=.2)
        self.stress = [2000., 1000., 1000., 0., 0., 0.]

    def test_matches_independent_constrained_elastic_solution_with_hold(self):
        coordinates = [0., .001, .001, .003]
        result = self.adapter.replay_oedometer('linear-elastic', self.parameters, self.stress, .8, coordinates)
        self.assertEqual(result['status'], 'success', result['message'])
        E, nu = self.parameters['E'], self.parameters['nu']
        modulus = E*(1-nu)/((1+nu)*(1-2*nu))
        lame = E*nu/((1+nu)*(1-2*nu))
        for p, x in zip(result['points'], coordinates):
            self.assertAlmostEqual(p['axial_stress'], 2000+modulus*x, delta=1e-5)
            self.assertAlmostEqual(p['radial_stress'], 1000+lame*x, delta=1e-5)
            self.assertAlmostEqual(p['void_ratio'], 1.8*math.exp(-x)-1, delta=1e-9)
            self.assertEqual(p['strain'][1:], [0.]*5)
        self.assertEqual(result['points'][1]['state'], result['points'][2]['state'])
        self.assertEqual(result['native_calls'], 2)

    def test_segment_failure_rolls_back_to_preceding_observation(self):
        failed = dict(catalogue_hash=self.adapter.catalogue_hash, ok=False,
                      message='deliberate partial failure', points=[dict(state=[999.]*7, strain=[.001]*6)])
        with patch('analysis.atlas_adapter.subprocess.run', return_value=subprocess.CompletedProcess(
                [], 0, json.dumps(failed), '')):
            result = self.adapter.replay_oedometer('linear-elastic', self.parameters, self.stress, .8, [0., .002, .003])
        self.assertEqual(result['status'], 'integration_failure')
        self.assertEqual(result['last_committed_state'], self.stress+[.8])
        self.assertEqual(result['completed_observations'], 1)

    def test_missing_full_stress_or_reversal_rejected(self):
        with self.assertRaisesRegex(ValueError, 'tensor'):
            self.adapter.replay_oedometer('linear-elastic', self.parameters, [2000.], .8, [0., .001])
        with self.assertRaisesRegex(ValueError, 'without sorting'):
            self.adapter.replay_oedometer('linear-elastic', self.parameters, self.stress, .8, [0., .001, .0005])


if __name__ == '__main__':
    unittest.main()
