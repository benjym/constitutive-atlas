"""Synthetic complete-prediction calibration; no files, solver or measurements."""
import copy
import hashlib
import json
import math
import unittest
from atlas.calibration_search import METHOD, PredictionFailure, calibrate


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.reserve = {'paper_reservation_version': 1, 'id': 'synthetic-reservations',
            'experiments': [{'id': t, 'role': 'reserved_final' if t == 'R' else 'development'}
                            for t in ['A', 'B', 'E', 'R']]}
        self.rh = hashlib.sha256(json.dumps(self.reserve).encode()).hexdigest()
        self.allocation = {'schema_version': '0.1', 'kind': 'whole-test-study-allocation',
            'id': 'synthetic-allocation', 'phase': 'development', 'grouping_unit': 'whole_test',
            'evaluation_claim': 'previously_exposed_development',
            'calibration_packages': {'fit': ['A', 'B']}, 'evaluation_ids': ['E'],
            'reservation_policy': {'id': 'synthetic-reservations', 'sha256': self.rh},
            'limitations': ['Synthetic only.']}
        self.ah = hashlib.sha256(json.dumps(self.allocation).encode()).hexdigest()
        self.objective = {'schema_version': '0.1', 'kind': 'study-objective', 'id': 'synthetic-objective',
            'allocation_sha256': self.ah, 'package': 'fit',
            'method': 'piecewise-linear-residual-axial-travel-v1',
            'test_aggregation': 'equal_whole_test', 'failure_policy': 'reject_entire_candidate',
            'channels': {'q': {'unit': 'Pa', 'scale': 1., 'weight': 1.}}}
        self.observations = {t: {'units': {'q': 'Pa'}, 'rows': [
            {'axial_strain': 0., 'q': 1.}, {'axial_strain': .01, 'q': 1.}]} for t in ['A', 'B']}
        self.spec = {'id': 'synthetic-search', 'method': METHOD,
            'parameters': {'x': 3., 'fixed': 7.},
            'fitted': [{'name': 'x', 'bounds': [0., 4.], 'transform': 'linear'}],
            'max_evaluations': 5, 'initial_step': .25, 'minimum_step': .0625}

    def predict(self, parameters):
        return {t: {'units': {'q': 'Pa'}, 'status': 'success', 'points': [
            {'observation_index': i, 'axial_strain': r['axial_strain'], 'q': parameters['x']}
            for i, r in enumerate(self.observations[t]['rows'])]} for t in ['A', 'B']}

    def run_search(self, predict=None, **kwargs):
        return calibrate(self.spec, predict or self.predict, self.objective,
            self.allocation, self.reserve, self.observations,
            allocation_sha256=self.ah, reservation_sha256=self.rh, **kwargs)

    def test_exact_serial_poll_budget_best_and_no_parameter_mutation(self):
        before = copy.deepcopy((self.spec, self.observations))
        calls = []
        def model(p):
            calls.append(copy.deepcopy(p));return self.predict(p)
        result = self.run_search(model)
        self.assertEqual([c['x'] for c in calls], [3., 2., 4., 1., 0.])
        self.assertEqual(result['evaluations'], 5)
        self.assertEqual(result['stop_reason'], 'evaluation_budget')
        self.assertEqual(result['best']['parameters'], {'x': 1., 'fixed': 7.})
        self.assertEqual(result['best']['objective'], 0.)
        self.assertEqual([c['sequence'] for c in result['candidates']], list(range(5)))
        self.assertTrue(all(c['fixed'] == 7. for c in calls))
        self.assertEqual(before, (self.spec, self.observations))
        self.assertFalse(result['scientific_admission'])

    def test_multiaxis_sweep_uses_frozen_center_and_first_strict_best(self):
        self.spec['parameters']['y']=3.
        self.spec['fitted'].append({'name':'y','bounds':[0.,4.],'transform':'linear'})
        self.objective['channels']['p']={'unit':'Pa','scale':1.,'weight':1.}
        for bundle in self.observations.values():
            bundle['units']['p']='Pa'
            for row in bundle['rows']:row['p']=1.
        calls=[]
        def model(parameters):
            calls.append(copy.deepcopy(parameters));result=self.predict(parameters)
            for bundle in result.values():
                bundle['units']['p']='Pa'
                for point in bundle['points']:point['p']=parameters['y']
            return result
        result=self.run_search(model)
        self.assertEqual([(p['x'],p['y']) for p in calls],[(3,3),(2,3),(4,3),(3,2),(3,4)])
        self.assertEqual(result['best']['parameters']['x'],2.)
        self.assertEqual(result['best']['parameters']['y'],3.)

    def test_log_coordinates_use_geometric_steps_and_preserve_exact_bounds(self):
        self.spec['parameters']['x'] = 10.
        self.spec['fitted'][0].update(bounds=[1., 100.], transform='log')
        self.spec.update(initial_step=.5, max_evaluations=3)
        result = self.run_search()
        self.assertEqual([c['parameters']['x'] for c in result['candidates']], [10., 1., 100.])
        self.assertEqual(result['best']['parameters']['x'], 1.)

    def test_failures_count_and_never_receive_finite_penalty_or_prefix_score(self):
        self.spec['max_evaluations'] = 3
        def model(p):
            if p['x'] == 2.: raise PredictionFailure('synthetic nonconvergence')
            result = self.predict(p)
            if p['x'] == 4.: result['B']['status'] = 'failed'
            return result
        result = self.run_search(model)
        self.assertEqual(result['evaluations'], 3)
        self.assertEqual([r['status'] for r in result['candidates']], ['success', 'rejected', 'rejected'])
        self.assertEqual(result['best']['parameters']['x'], 3.)
        for row in result['candidates'][1:]:
            self.assertIsNone(row['objective']);self.assertIsNone(row['score']);self.assertTrue(row['error'])

    def test_all_failures_terminate_at_minimum_step_and_none_is_best(self):
        self.spec['max_evaluations'] = 100
        def model(p): raise PredictionFailure('no solution')
        result = self.run_search(model)
        self.assertEqual(result['status'], 'no_feasible_candidate')
        self.assertEqual(result['stop_reason'], 'minimum_step')
        self.assertIsNone(result['best'])
        self.assertTrue(all(r['status']=='rejected' for r in result['candidates']))
        keys=[r['parameters']['x'] for r in result['candidates']]
        self.assertEqual(len(keys),len(set(keys)))

    def test_failed_seed_can_recover_at_feasible_neighbour(self):
        self.spec['max_evaluations']=3
        def model(p):
            if p['x']==3.:raise PredictionFailure('seed outside coupled domain')
            predicted=self.predict(p)
            p['fixed']=-999.  # Adapter mutation cannot change stored parameter identity.
            return predicted
        result=self.run_search(model)
        self.assertEqual(result['candidates'][0]['status'],'rejected')
        self.assertEqual(result['best']['parameters'],{'x':2.,'fixed':7.})
        self.assertAlmostEqual(result['best']['objective'],1.,delta=4*math.ulp(1.))
        self.assertEqual(result['evaluations'],3)

    def test_unexpected_evaluator_error_is_recorded_and_stops_immediately(self):
        calls=[]
        def model(p):
            calls.append(p);raise RuntimeError('synthetic adapter bug')
        result=self.run_search(model)
        self.assertEqual(len(calls),1)
        self.assertEqual(result['status'],'error')
        self.assertEqual(result['stop_reason'],'evaluator_error')
        self.assertIn('RuntimeError',result['candidates'][0]['error'])
        self.assertIsNone(result['best'])

    def test_receipt_sink_precedes_next_call_and_cannot_mutate_result(self):
        events=[]
        def model(p): events.append('predict');return self.predict(p)
        def sink(r):
            events.append('record');r['parameters']['x']=-999.;r['objective']=-1.
        result=self.run_search(model,on_candidate=sink)
        self.assertEqual(events,['predict','record']*5)
        self.assertEqual(result['best']['objective'],0.)
        self.assertTrue(all(r['parameters']['x']>=0 for r in result['candidates']))
        def fail(r):raise OSError('synthetic full journal')
        calls=[]
        def once(p):calls.append(p);return self.predict(p)
        with self.assertRaisesRegex(OSError,'journal'):self.run_search(once,on_candidate=fail)
        self.assertEqual(len(calls),1)

    def test_reproducible_result_and_observation_value_binding(self):
        first=self.run_search();self.assertEqual(first,self.run_search())
        self.observations['A']['rows'][1]['q']=2.
        second=self.run_search()
        self.assertNotEqual(first['observation_values_sha256'],second['observation_values_sha256'])
        json.dumps(second,allow_nan=False)

    def test_invalid_search_settings_reject_before_callback(self):
        baseline=copy.deepcopy(self.spec)
        variants=[]
        for key,value in [('max_evaluations',True),('max_evaluations',0),('max_evaluations',10001),
                          ('initial_step',0.),('minimum_step',math.nan),('minimum_step',.5),
                          ('method','random-search')]:
            v=copy.deepcopy(baseline);v[key]=value;variants.append(v)
        for item in [dict(name='missing',bounds=[0,4],transform='linear'),
                     dict(name='x',bounds=[0,4],transform='log'),
                     dict(name='x',bounds=[0,2],transform='linear'),
                     dict(name='x',bounds=[-1e308,1e308],transform='linear')]:
            v=copy.deepcopy(baseline);v['fitted']=[item];variants.append(v)
        v=copy.deepcopy(baseline);v['fitted']*=2;variants.append(v)
        calls=[]
        for spec in variants:
            self.spec=spec
            with self.subTest(spec=spec),self.assertRaises(ValueError):
                self.run_search(lambda p:calls.append(p))
        self.assertEqual(calls,[])

    def test_metadata_and_observations_fail_before_callback(self):
        calls=[]
        def model(p):calls.append(p);return self.predict(p)
        self.objective['allocation_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'identity'):self.run_search(model)
        self.objective['allocation_sha256']=self.ah
        self.observations['E']=self.observations['A']
        with self.assertRaisesRegex(ValueError,'exactly'):self.run_search(model)
        del self.observations['E']
        self.observations['A']['rows'][1]['q']=float('nan')
        with self.assertRaisesRegex(ValueError,'finite'):self.run_search(model)
        self.assertEqual(calls,[])

    def test_truncated_extra_and_nonfinite_predictions_reject_entire_candidate(self):
        self.spec['max_evaluations']=1
        for kind in ['truncated','reserved','nonfinite']:
            def model(p):
                predictions=self.predict(p)
                if kind=='truncated':predictions['B']['points'].pop()
                if kind=='reserved':predictions['R']=predictions['A']
                if kind=='nonfinite':predictions['B']['points'][1]['q']=math.inf
                return predictions
            with self.subTest(kind=kind):
                result=self.run_search(model)
                self.assertEqual(result['status'],'no_feasible_candidate')
                self.assertIsNone(result['best'])
                self.assertEqual(result['candidates'][0]['status'],'rejected')


if __name__=='__main__':unittest.main()
