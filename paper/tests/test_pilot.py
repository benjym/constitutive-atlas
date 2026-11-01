"""Checks of scientific invariants used by the paper development pilot."""
import copy
import json
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.atlas_adapter import NativeAdapter
from analysis.common import ROOT, read_json
from analysis.metrics import compare, compare_acquisition, monotonic_pairs
from analysis.pilot import calibrate, prepare_experiment, score_prediction, validate_config
from analysis.evaluation import prepare_evaluation, predict_evaluation, resolutions
from analysis.reservations import assert_development_ids, select_members
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_data import audit
from report_pilot import evaluation_score


class ScientificControls(unittest.TestCase):
    def setUp(self):
        self.config = read_json(ROOT/'paper/study/pilot.json')

    def test_whole_test_leakage_is_rejected(self):
        self.config['packages']['C1'].append(self.config['evaluation_ids'][0])
        with self.assertRaisesRegex(ValueError, 'leakage'):
            validate_config(self.config)

    def test_reserved_response_cannot_enter_config(self):
        self.config['experiment_paths']['KFS-TMD18'] = 'never-open-this.json'
        with self.assertRaisesRegex(ValueError, 'reserved final'):
            validate_config(self.config)

    def test_renamed_reserved_record_is_rejected_before_rows(self):
        with self.assertRaisesRegex(ValueError, 'reserved final'):
            prepare_experiment({'id': 'KFS-TMD18'}, self.config)

    def test_unassigned_kfs_requires_a_role(self):
        with self.assertRaisesRegex(ValueError, 'assign a study role'):
            assert_development_ids(['KFS-NEW1'])

    def test_archive_allowlist_excludes_reserved_members(self):
        self.assertEqual(select_members(['TMD6.dat', 'TMD7.dat', 'TMD10.dat'], ['KFS-TMD7']),
                         {'KFS-TMD7': 'TMD7.dat'})
        with self.assertRaisesRegex(ValueError, 'reserved final'):
            select_members(['TMD6.dat'], ['KFS-TMD6'])
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            select_members(['a/TMD7.dat', 'b/TMD7.dat'], ['KFS-TMD7'])

    def test_audit_never_opens_reserved_named_response(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            # Invalid JSON proves it cannot have been parsed.
            (directory/'KFS-TMD18.json').write_text('reserved bytes must remain unread')
            manifest = directory/'sources.txt'
            manifest.write_text('{"sources": []}')
            with patch('audit_data.read_json', wraps=read_json) as reader:
                with self.assertRaisesRegex(ValueError, 'no normalized experiments'):
                    audit(directory, manifest)
                self.assertEqual([call.args[0] for call in reader.call_args_list], [manifest])

    def test_fixed_parameter_cannot_be_hidden_as_fitted(self):
        self.config['models'][0]['fixed_parameters']['E'] = 1e6
        with self.assertRaisesRegex(ValueError, 'partition'):
            validate_config(self.config)

    def test_missing_initial_state_is_rejected(self):
        experiment = {'protocol': 'drained-triaxial', 'initial': {}}
        with self.assertRaisesRegex(ValueError, 'void ratio'):
            prepare_experiment(experiment, self.config)

    def test_extension_path_cannot_be_sorted_into_compression(self):
        with self.assertRaisesRegex(ValueError, 'decreasing'):
            monotonic_pairs([{'x': 0., 'y': 0.}, {'x': .01, 'y': 1.}, {'x': .005, 'y': 2.}], 'x', 'y', .02)

    def test_short_prediction_cannot_improve_error_by_truncation(self):
        with self.assertRaisesRegex(ValueError, 'cover'):
            compare([(0., 0.), (1., 1.)], [(0., 0.), (.5, .5)], 1.)

    def test_scale_is_external_and_error_is_in_physical_units(self):
        metric = compare([(0., 0.), (1., 2.)], [(0., 3.), (1., 5.)], 2.)
        self.assertAlmostEqual(metric['rmse'], 3.)
        self.assertAlmostEqual(metric['scaled_mse'], 2.25)

    def test_nonfinite_prediction_is_retained_as_a_failure(self):
        prepared = {'curves': {'q': [(0., 0.), (1., 1.)]}, 'scales': {'q': 1.}}
        prediction = {'status': 'success', 'points': [
            {'axial_strain': 0., 'q': 0.}, {'axial_strain': 1., 'q': float('nan')}]}
        self.assertIsNone(score_prediction(prepared, prediction, 101))
        self.assertEqual(prediction['status'], 'invalid_prediction')
        self.assertEqual(len(prediction['points']), 2)

    def test_acquisition_metric_weights_reversal_travel(self):
        rows = [{'axial_strain': x, 'q': 0.} for x in (0., 2., 1.)]
        prediction = {'status': 'success', 'points': [
            {'observation_index': i, 'axial_strain': x, 'q': error}
            for i, (x, error) in enumerate(zip((0., 2., 1.), (0., 2., 4.)))]}
        metric = compare_acquisition(rows, prediction, 'q', 2.)
        self.assertAlmostEqual(metric['rmse']**2, 14/3)
        self.assertAlmostEqual(metric['scaled_mse'], 14/12)
        prediction['points'].reverse()
        with self.assertRaisesRegex(ValueError, 'preserve acquisition'):
            compare_acquisition(rows, prediction, 'q', 2.)

    def test_missing_evaluation_test_cannot_improve_aggregate(self):
        predictions = [{'experiment_id': 'a', 'status': 'success',
                        'metrics': {'q': {'scaled_mse': 0.}}}]
        self.assertIsNone(evaluation_score(predictions, ['a', 'b']))
        self.assertIsNone(evaluation_score(predictions*2, ['a', 'b']))

    def test_replay_requires_an_explicit_refining_protocol(self):
        config = read_json(ROOT/'paper/study/pilot_density.json')
        config['evaluation_protocol']['refinement_maximum_increments'] = [.0003]
        with self.assertRaisesRegex(ValueError, 'strictly refine'):
            validate_config(config)

    def test_replay_evaluation_preserves_rows_while_calibration_rejects_reversal(self):
        config = read_json(ROOT/'paper/study/pilot_density.json')
        rows = [{'axial_strain': x, 'q': x*1e7, 'volumetric_strain': x*.6}
                for x in [0., .002, .001, .001, .003]]
        experiment = {'id': 'synthetic', 'protocol': 'drained-triaxial', 'initial': {
            'void_ratio': .8, 'effective_stress': [1e5, 1e5, 1e5, 0., 0., 0.]}, 'rows': rows}
        with self.assertRaisesRegex(ValueError, 'decreasing'):
            prepare_experiment(experiment, config)
        prepared = prepare_evaluation(experiment, config)
        self.assertEqual(prepared['rows'], rows)
        self.assertEqual(resolutions(config)[0], {'maximum_increment': .0002})

        class IncompleteReplay:
            def replay(self, *args):
                return {'status': 'success', 'points': []}

        prediction, metrics = predict_evaluation(prepared, 'synthetic', {}, IncompleteReplay(), config)
        self.assertIsNone(metrics)
        self.assertEqual(prediction['status'], 'invalid_prediction')

    def test_empty_success_is_not_treated_as_perfect_prediction(self):
        prepared = {'curves': {'q': [(0., 0.), (1., 1.)]}, 'scales': {'q': 1.}}
        prediction = {'status': 'success', 'points': []}
        self.assertIsNone(score_prediction(prepared, prediction, 101))
        self.assertEqual(prediction['status'], 'invalid_prediction')

    def test_pattern_search_recovers_synthetic_elastic_constants(self):
        # Analytical drained uniaxial loading with fixed radial stress, used as
        # an independent inverse problem with a known exact answer.
        config = copy.deepcopy(self.config)
        config['optimizer']['max_evaluations'] = 200
        model = config['models'][0]
        E, nu = 1e7, .2
        rows = [{'axial_strain': x, 'q': E*x, 'volumetric_strain': (1-2*nu)*x}
                for x in [0., .005, .01, .015, .02]]
        experiment = {'id': 'synthetic', 'protocol': 'drained-triaxial', 'initial': {
            'void_ratio': .8, 'effective_stress': [1e5, 1e5, 1e5, 0., 0., 0.]}, 'rows': rows}

        class AnalyticalAdapter:
            def simulate(self, mid, parameters, experiment, target, steps, timeout):
                return {'status': 'success', 'points': [
                    {'axial_strain': row['axial_strain'], 'q': parameters['E']*row['axial_strain'],
                     'volumetric_strain': (1-2*parameters['nu'])*row['axial_strain']} for row in rows]}

        result = calibrate(model, [prepare_experiment(experiment, config)], config,
                           AnalyticalAdapter(), 0, lambda row: None)
        self.assertEqual(result['status'], 'success')
        self.assertLess(abs(result['best']['parameters']['E']/E-1), .01)
        self.assertLess(abs(result['best']['parameters']['nu']-nu), .002)


@unittest.skipUnless((ROOT/'build/atlas_solver').exists(), 'build native solver for adapter verification')
class NativeContract(unittest.TestCase):
    def test_density_runner_accounts_for_acquisition_evaluation_and_archives_inputs(self):
        config = read_json(ROOT/'paper/study/pilot_density.json')
        config['models'] = config['models'][:1]
        config['optimizer']['seeds'] = [0]
        config['optimizer']['max_evaluations'] = 1
        config['packages'] = {'synthetic_fit': ['synthetic-calibration']}
        config['evaluation_ids'] = ['synthetic-evaluation']
        config['evaluation_protocol']['refinement_maximum_increments'] = [.0001]
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            config['experiment_paths'] = {}
            for identifier, coordinates in [('synthetic-calibration', [0., .001, .002]),
                                             ('synthetic-evaluation', [0., .002, .001, .003])]:
                experiment = {'id': identifier, 'schema_version': '0.1', 'protocol': 'drained-triaxial',
                    'initial': {'void_ratio': .8, 'effective_stress': [1e5, 1e5, 1e5, 0., 0., 0.]},
                    'rows': [{'axial_strain': x, 'q': x*3e7, 'volumetric_strain': x*.5} for x in coordinates]}
                path = directory/f'{identifier}.json'
                path.write_text(json.dumps(experiment))
                config['experiment_paths'][identifier] = str(path)
            config_path = directory/'config.json'
            config_path.write_text(json.dumps(config))
            process = subprocess.run([sys.executable, str(ROOT/'paper/scripts/run_pilot.py'),
                '--config', str(config_path), '--output', str(directory/'run')], capture_output=True, text=True, timeout=30)
            self.assertEqual(process.returncode, 0, process.stderr)
            report = read_json(directory/'run/report.json')
            self.assertEqual(report['input_integrity'], 'verified_unchanged')
            self.assertEqual(len(report['predictions']), 1)
            prediction = report['predictions'][0]
            self.assertEqual(prediction['status'], 'success', prediction['message'])
            self.assertEqual([p['axial_strain'] for p in prediction['points']], [0., .002, .001, .003])
            self.assertLess(prediction['metrics']['q']['rmse'], 1e-5)
            self.assertEqual(len(prediction['refinement']), 1)
            self.assertEqual(len(report['baselines']), 1)
            for identifier in config['experiment_paths']:
                self.assertTrue((directory/'run/experiments'/f'{identifier}.json').exists())

    def test_failed_replay_segment_does_not_commit_trial_state(self):
        adapter = NativeAdapter(ROOT/'build/atlas_solver', ['linear-elastic'])
        initial = [1e5, 1e5, 1e5, 0., 0., 0.]
        experiment = {'schema_version': '0.1', 'protocol': 'drained-triaxial', 'initial': {
            'void_ratio': .8, 'effective_stress': initial}}
        parameters = {'p_ref': 1e5, 'E': 1e7, 'nu': .2}
        failed = {'catalogue_hash': adapter.catalogue_hash, 'ok': False,
                  'message': 'deliberate failure after partial segment',
                  'points': [{'state': [999.]*7, 'strain': [.001]*6}]}
        with patch('analysis.atlas_adapter.subprocess.run', return_value=subprocess.CompletedProcess(
                [], 0, json.dumps(failed), '')) as runner:
            result = adapter.replay('linear-elastic', parameters, experiment, [0., .002, .003])
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(result['status'], 'integration_failure')
        self.assertEqual(result['last_committed_state'], initial+[.8])
        self.assertEqual(result['completed_observations'], 1)

    def test_replay_matches_native_monotonic_hypoplastic_path(self):
        config = read_json(ROOT/'paper/study/pilot.json')
        model = config['models'][2]
        adapter = NativeAdapter(ROOT/'build/atlas_solver', [model['id']])
        experiment = {'schema_version': '0.1', 'protocol': 'drained-triaxial', 'initial': {
            'void_ratio': .8, 'effective_stress': [1e5, 1e5, 1e5, 0., 0., 0.]}}
        replay = adapter.replay(model['id'], model['baseline_parameters'], experiment, [0., .005, .01], .0005)
        monotonic = adapter.simulate(model['id'], model['baseline_parameters'], experiment, .01, 20)
        self.assertEqual(replay['status'], 'success', replay['message'])
        self.assertEqual(monotonic['status'], 'success', monotonic['message'])
        self.assertAlmostEqual(replay['points'][-1]['q'], monotonic['points'][-1]['q'], delta=.05)
        self.assertAlmostEqual(replay['points'][-1]['volumetric_strain'], monotonic['points'][-1]['volumetric_strain'], delta=1e-8)

    def test_recorded_order_replay_preserves_reversal_and_duplicate(self):
        adapter = NativeAdapter(ROOT/'build/atlas_solver', ['linear-elastic'])
        experiment = {'schema_version': '0.1', 'protocol': 'drained-triaxial', 'initial': {
            'void_ratio': .8, 'effective_stress': [1e5, 1e5, 1e5, 0., 0., 0.]}}
        coordinates = [0., .002, .001, .001, .003]
        parameters = {'p_ref': 1e5, 'E': 1e7, 'nu': .2}
        replay = adapter.replay('linear-elastic', parameters, experiment, coordinates)
        self.assertEqual(replay['status'], 'success', replay['message'])
        self.assertEqual([p['axial_strain'] for p in replay['points']], coordinates)
        for p in replay['points']:
            self.assertAlmostEqual(p['q'], 1e7*p['axial_strain'], places=6)
            self.assertAlmostEqual(p['volumetric_strain'], .6*p['axial_strain'], places=12)
        self.assertEqual(replay['points'][2]['state'], replay['points'][3]['state'])
        rows = [{'axial_strain': x, 'q': 1e7*x} for x in coordinates]
        self.assertLess(compare_acquisition(rows, replay, 'q', 1e5)['rmse'], 1e-6)
        replay['status'] = 'integration_failure'
        with self.assertRaisesRegex(ValueError, 'complete successful'):
            compare_acquisition(rows, replay, 'q', 1e5)

    def test_frozen_run_survives_origin_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            origin = directory/'origin'
            origin.mkdir()
            model_path = origin/'linear-elastic.json'
            shutil.copy2(ROOT/'models/linear-elastic.json', model_path)
            solver_path = origin/'atlas_solver'
            shutil.copy2(ROOT/'build/atlas_solver', solver_path)
            adapter = NativeAdapter(solver_path, ['linear-elastic'], origin)
            run = directory/'run'
            run.mkdir()
            adapter.freeze(run)
            model_path.write_text('{}')
            solver_path.write_text('origin replaced during concurrent development')
            adapter.verify_unchanged()
            self.assertEqual(adapter.origin_drift(), {'models': {'linear-elastic': True}, 'solver': True})
            experiment = {'schema_version': '0.1', 'protocol': 'drained-triaxial', 'initial': {
                'void_ratio': .8, 'effective_stress': [1e5, 1e5, 1e5, 0., 0., 0.]}}
            prediction = adapter.simulate('linear-elastic', {'p_ref': 1e5, 'E': 1e7, 'nu': .2}, experiment, .01, 10)
            self.assertEqual(prediction['status'], 'success')

    def test_adapter_agrees_with_analytical_elastic_traction_path(self):
        adapter = NativeAdapter(ROOT/'build/atlas_solver', ['linear-elastic'])
        experiment = {'schema_version': '0.1', 'protocol': 'drained-triaxial', 'initial': {
            'void_ratio': .8, 'effective_stress': [1e5, 1e5, 1e5, 0., 0., 0.]}}
        parameters = {'p_ref': 1e5, 'E': 1e7, 'nu': .2}
        prediction = adapter.simulate('linear-elastic', parameters, experiment, .01, 20)
        self.assertEqual(prediction['status'], 'success')
        final = prediction['points'][-1]
        self.assertAlmostEqual(final['q'], parameters['E']*.01, places=5)
        self.assertAlmostEqual(final['volumetric_strain'], (1-2*parameters['nu'])*.01, places=10)
        adapter.verify_unchanged()


if __name__ == '__main__':
    unittest.main()
