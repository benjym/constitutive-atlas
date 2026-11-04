"""Caller-path refinement semantics; no native builds in tests."""
import copy
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from atlas.compiler import generate
from atlas.dsl import ValidationError
from atlas.model import ROOT
from atlas.refinement import VERSION,refine_recorded,difference,validate_study,execute_study


def spec():return json.loads((ROOT/'protocols/recorded-linear-elastic-run.json').read_text())
def study():return dict(version=VERSION,id='fixture',description='Numerical test only',factors=[1,2,4],cases=[dict(id='elastic',specification=spec())])


class RefinementContractTests(unittest.TestCase):
    def test_exact_originals_reversals_duplicates_and_no_mutation(self):
        s=spec();before=copy.deepcopy(s);r,indices=refine_recorded(s,4)
        self.assertEqual(s,before);self.assertEqual(indices,[0,4,8,12,16])
        self.assertEqual([r['path']['knots'][i] for i in indices],s['path']['knots'])
        self.assertEqual([k['targets'][0] for k in r['path']['knots'][8:13]],[-6e-5]*5)
        self.assertGreater(r['path']['knots'][4]['targets'][0],r['path']['knots'][5]['targets'][0])
        self.assertEqual(r['path']['knots'][1]['targets'][0],.000025)
        self.assertEqual(r['path']['knots'][1]['targets'][1],100000)
        self.assertEqual(r['path']['initial_strain'],s['path']['initial_strain'])
        r['path']['knots'][0]['targets'][0]=.1;self.assertEqual(s,before)

    def test_factors_bounds_and_precision(self):
        for factor in [0,-1,True,1.5,1251]:
            with self.subTest(factor=factor),self.assertRaises(ValidationError):refine_recorded(spec(),factor)
        r,indices=refine_recorded(spec(),1250);self.assertEqual(len(r['path']['knots']),5001);self.assertEqual(indices[-1],5000)
        s=spec();s['path']['knots']=s['path']['knots'][:2]
        s['path']['knots'][0]['coordinate']=1.;s['path']['knots'][1]['coordinate']=math.nextafter(1.,math.inf)
        with self.assertRaises(ValidationError):refine_recorded(s,2)

    def test_closed_study_nested_factors_and_unique_ids(self):
        for change in [lambda s:s.update(extra=1),lambda s:s.update(factors=[2,4]),lambda s:s.update(factors=[1,4,6]),lambda s:s.update(factors=[1,2,2]),lambda s:s['cases'].append(copy.deepcopy(s['cases'][0]))]:
            s=study();change(s)
            with self.assertRaises(ValidationError):validate_study(s)

    def test_comparison_persistent_transient_and_coordinates(self):
        fields=[dict(name='stress',offset=0,size=1,scale=100,transient=False),dict(name='multiplier',offset=1,size=1,scale=1,transient=True)]
        a=[dict(coordinate=1,state=[100.,10.],strain=[0]*6)]
        b=[dict(coordinate=1,state=[102.,100.],strain=[.001]+[0]*5)]
        d=difference(a,b,fields);self.assertEqual(d['max_persistent_state_scaled'],.02);self.assertEqual(d['max_transient_state_scaled'],90)
        self.assertEqual(d['max_strain_component_abs'],.001);self.assertEqual(d['field_max_abs'],dict(stress=2,multiplier=90))
        for change in [lambda p:p.update(coordinate=2),lambda p:p.update(state=[float('nan'),1]),lambda p:p.update(strain=[0])]:
            v=copy.deepcopy(b);change(v[0])
            with self.assertRaises(ValueError):difference(a,v,fields)


class RefinementExecutionTests(unittest.TestCase):
    def run_fixture(self,failed=(),transport=()):
        s=study();calls=[]
        def fake(request,solver):
            n=(len(request['path']['knots'])-1)//4;calls.append(n)
            if n in transport:raise subprocess.TimeoutExpired('fixture',.01)
            initial=[1e5,1e5,1e5,0,0,0,.7]
            points=[]
            for knot in request['path']['knots']:
                x=knot['targets'][0]
                points.append(dict(coordinate=knot['coordinate'],strain=[x,-.25*x,-.25*x,0,0,0],state=[1e5+3e7*x,1e5,1e5,0,0,0,1.7*math.exp(-.5*x)-1]))
            ok=n not in failed
            return dict(ok=ok,parameters=[1e5,3e7,.25],initial=initial,points=points if ok else points[:1],specification=request)
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);generate(folder/'generated');descriptor=json.loads((folder/'generated/models.json').read_text());solver=folder/'solver';solver.write_text('mock binary, never executed');out=folder/'out.json'
            with patch('atlas.refinement.subprocess.check_output',return_value=json.dumps(descriptor)),patch('atlas.refinement.execute_recorded',side_effect=fake):
                result=execute_study(s,solver,out)
            self.assertEqual(json.loads(out.read_text()),result)
        self.assertEqual(calls,[1,2,4]);self.assertTrue(result['execution_complete']);return result['cases'][0]

    def test_all_levels_and_zero_analytical_path_difference(self):
        case=self.run_fixture();self.assertTrue(case['finest_complete'])
        for v in case['levels']:self.assertEqual(v['comparison_to_finest']['max_persistent_state_scaled'],0)

    def test_failed_finest_never_replaced_by_successful_coarser(self):
        case=self.run_fixture(failed=(4,));self.assertFalse(case['finest_complete'])
        for v in case['levels']:self.assertIsNone(v['comparison_to_finest'])
        self.assertFalse(case['levels'][-1]['response']['ok'])

    def test_failed_middle_breaks_adjacency(self):
        for field in ['failed','transport']:
            with self.subTest(field=field):
                case=self.run_fixture(**{field:(2,)})
                self.assertTrue(case['finest_complete']);self.assertIsNone(case['levels'][1]['comparison_to_finest']);self.assertIsNone(case['levels'][2]['comparison_to_previous'])
                if field=='transport':self.assertIn('TimeoutExpired',case['levels'][1]['transport_error'])



class RetainedRefinementTests(unittest.TestCase):
    def report(self,name='report'):
        import gzip
        path=ROOT/'catalogue/investigations/recorded-refinement-v1'/(name+'.json.gz')
        return json.loads(gzip.decompress(path.read_bytes()))

    def test_full_matrices_and_failures_preserved(self):
        from tools.analyze_recorded_refinement import summarize
        a=summarize(self.report());b=summarize(self.report('plastic-report'))
        self.assertEqual((a['successful'],a['failed']),(45,3))
        self.assertEqual((b['successful'],b['failed']),(9,3))
        self.assertEqual(len(a['cases']),8);self.assertEqual(len(b['cases']),2)

    def test_elastic_independent_closed_form_at_every_point(self):
        case=self.report()['cases'][0];self.assertEqual(case['model'],'linear-elastic')
        for level in case['levels']:
            r=level['response'];self.assertTrue(r['ok'])
            self.assertEqual(r['parameters'],[100000,30000000,.25])
            for pt,knot in zip(r['points'],r['specification']['path']['knots']):
                x=knot['targets'][0]
                for a,b in zip(pt['strain'],[x,-.25*x,-.25*x,0,0,0]):self.assertAlmostEqual(a,b,delta=2e-11)
                for a,b in zip(pt['state'][:6],[1e5+3e7*x,1e5,1e5,0,0,0]):self.assertAlmostEqual(a,b,delta=.002)
                self.assertAlmostEqual(pt['state'][6],1.7*math.exp(-.5*x)-1,delta=1e-10)

    def test_plastic_flow_hardening_and_increment_local_multiplier(self):
        a,b=self.report('plastic-report')['cases']
        for case in (a,b):
            gamma=next(f['offset'] for f in case['fields'] if f['name']=='gamma')
            self.assertTrue(any(pt['state'][gamma]>1e-5 for level in case['levels'] for pt in level['response']['points']))
        pc=next(f['offset'] for f in b['fields'] if f['name']=='pc')
        r=b['levels'][-1]['response'];self.assertGreater(max(p['state'][pc] for p in r['points']),r['initial'][pc])
        d=a['levels'][-1]['comparison_to_previous']
        self.assertLess(d['max_persistent_state_scaled'],1e-12)
        self.assertGreater(d['max_transient_state_scaled'],1e-4)

    def test_corrupt_grid_metrics_or_settings_rejected(self):
        from tools.analyze_recorded_refinement import summarize
        for change in [lambda r:r['cases'][0]['levels'][1]['original_indices'].__setitem__(1,1),
                       lambda r:r['cases'][0]['levels'][1]['comparison_to_finest'].__setitem__('max_persistent_state_scaled',1),
                       lambda r:r['cases'][0]['levels'][1]['response']['integration_settings'].__setitem__('rate_tolerance',.1),
                       lambda r:r.__setitem__('execution_complete',False)]:
            r=self.report();change(r)
            with self.assertRaises(ValueError):summarize(r)


if __name__=='__main__':unittest.main()
