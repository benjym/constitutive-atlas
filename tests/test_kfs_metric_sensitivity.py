"""Synthetic saved-study diagnostic witnesses, without experimental observations."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-metric-sensitivity-v1/assess.py'
SPEC = importlib.util.spec_from_file_location('kfs_metric_diagnostic', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    policy = {'id':'synthetic', 'phase':'synthetic', 'new_method':MODULE.METHOD,
              'model_sha256':{'model':'synthetic-digest'},
              'packages':{'pressure3':['calibration-a'], 'density3':['calibration-b']},
              'evaluation_ids':['evaluation-a','evaluation-b'],
              'maximum_axial_strain':0.02, 'channels':['q','volumetric_strain'],
              'q_scale':'initial_mean_effective_stress', 'volumetric_strain_scale':0.01,
              'legacy_method':'trapezoidal endpoint error over absolute axial-strain travel',
              'relative_score_tolerance':1e-12, 'absolute_score_tolerance':1e-15}
    report = {'input_integrity':'verified_unchanged', 'model_sha256':policy['model_sha256'],
              'config':{'packages':policy['packages'], 'evaluation_ids':policy['evaluation_ids'],
                        'maximum_axial_strain':0.02, 'objective':{
                            'channels':policy['channels'], 'q_scale':policy['q_scale'],
                            'volumetric_strain_scale':0.01}}, 'predictions':[], 'calibrations':[]}
    experiments = {}
    for eid in policy['evaluation_ids']:
        experiments[eid] = {'id':eid, 'protocol':'drained-triaxial',
                            'initial':{'effective_stress':[3,3,3,0,0,0], 'void_ratio':0.8},
                            'rows':[{'axial_strain':x,'q':0,'volumetric_strain':0}
                                    for x in (0,0.01,0.03,0.005)]}
    for package in policy['packages']:
        report['calibrations'].append({'model':'model','package':package,'selected_seed':1,
                                       'fits':[{'seed':1,'best':{'completed':True,'parameters':{'p':1}}}]})
        for eid in policy['evaluation_ids']:
            report['predictions'].append({'model':'model','package':package, 'experiment_id':eid,
                'selected':True, 'seed':1, 'parameters':{'p':1}, 'status':'success',
                'points':[{'observation_index':i, 'axial_strain':x,'q':3*i,'volumetric_strain':0.01*i}
                          for i,x in enumerate((0,0.01))],
                'metrics':{c:{'weighting':policy['legacy_method'], 'scale':s,
                              'observations':2, 'total_absolute_axial_strain_travel':0.01,
                              'scaled_mse':0.5} for c,s in (('q',3),('volumetric_strain',0.01))}})
    return report, experiments, policy


class SavedMetricSensitivityTests(unittest.TestCase):
    def test_complete_locked_study_matches_analytic_gap(self):
        report, experiments, policy = fixture()
        before = copy.deepcopy((report,experiments,policy))
        result = MODULE.assess(report,experiments,policy)
        self.assertEqual(result['selected_predictions'],4)
        self.assertEqual(result['channel_comparisons'],8)
        self.assertAlmostEqual(result['aggregates'][0]['legacy_root_scaled_mse'],(1/2)**0.5)
        self.assertAlmostEqual(result['aggregates'][0]['new_root_scaled_mse'],(1/3)**0.5)
        self.assertAlmostEqual(result['records'][0]['channels']['q']['analytic_scaled_mse_gap'],1/6)
        self.assertEqual((report,experiments,policy),before)

    def test_window_stops_at_first_crossing_not_later_return(self):
        report, experiments, policy = fixture()
        rows, scales = MODULE.window(experiments['evaluation-a'],policy)
        self.assertEqual([r['axial_strain'] for r in rows],[0,0.01])
        self.assertEqual(scales['q'],3)

    def test_duplicate_missing_and_extra_selected_predictions_reject(self):
        for change in ('duplicate','missing','extra'):
            report, experiments, policy = fixture()
            if change == 'duplicate':report['predictions'].append(copy.deepcopy(report['predictions'][0]))
            if change == 'missing':report['predictions'].pop()
            if change == 'extra':report['predictions'][0]['experiment_id']='reserved-test'
            with self.subTest(change=change), self.assertRaisesRegex(ValueError,'selected prediction'):
                MODULE.assess(report,experiments,policy)

    def test_changed_locked_parameters_or_seed_reject(self):
        for field,value in (('parameters',{'p':2}),('seed',2)):
            report, experiments, policy = fixture()
            report['predictions'][0][field]=value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,'locked selected fit'):
                MODULE.assess(report,experiments,policy)

    def test_failed_partial_or_corrupt_saved_score_reject(self):
        for change in ('failed','partial','score','scale','coordinate'):
            report, experiments, policy = fixture()
            p=report['predictions'][0]
            if change == 'failed':p['status']='failed'
            if change == 'partial':p['points'].pop()
            if change == 'score':p['metrics']['q']['scaled_mse']=0.6
            if change == 'scale':p['metrics']['q']['scale']=4
            if change == 'coordinate':p['points'][1]['axial_strain']=0.009
            with self.subTest(change=change), self.assertRaises(ValueError):
                MODULE.assess(report,experiments,policy)

    def test_task_identity_and_initialization_corruption_reject(self):
        for change in ('model','window','id','void','stress'):
            report, experiments, policy = fixture()
            if change == 'model':report['model_sha256']={'other':'digest'}
            if change == 'window':report['config']['maximum_axial_strain']=0.01
            if change == 'id':experiments['evaluation-a']['id']='other'
            if change == 'void':experiments['evaluation-a']['initial']['void_ratio']=False
            if change == 'stress':experiments['evaluation-a']['initial']['effective_stress'][0]=float('nan')
            with self.subTest(change=change), self.assertRaises(ValueError):
                MODULE.assess(report,experiments,policy)

    def test_failed_metadata_gate_precedes_missing_report_access(self):
        with tempfile.TemporaryDirectory() as directory:
            here=Path(directory); content=b'{}'
            (here/'policy.json').write_bytes(content)
            (here/'assess.py').write_bytes(content)
            digest=hashlib.sha256(content).hexdigest()
            (here/'freeze.json').write_text(json.dumps({'policy_sha256':digest,'assessor_sha256':digest}))
            with patch.object(MODULE,'check_parameters',side_effect=ValueError('metadata rejected')) as gate:
                with self.assertRaisesRegex(ValueError,'metadata rejected'):
                    MODULE.run(here/'nonexistent-root',here)
                gate.assert_called_once()


if __name__ == '__main__':unittest.main()
