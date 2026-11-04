"""Committed-parent reset semantics, independent of any SANISAND transcription."""
import copy,json,math,os,subprocess,unittest
from pathlib import Path
from atlas.dsl import ValidationError
from atlas.model import ROOT,load,validate,prepare_increment

SOLVER=Path(os.environ.get('ATLAS_TIME_SOLVER',ROOT/'build/atlas_time_solver'))
FIXTURES=ROOT/'tests/fixtures/time'
def state(coordinate=1,anchor=0):return {'sigma':[100,100,100,0,0,0],'coordinate':coordinate,'anchor':anchor}
def flat(s):return [*s['sigma'],s['coordinate'],s['anchor']]
def run(initial,increment,model='test-parent-reset',parameters=None):
    command=[str(SOLVER),'--mode','integrate','--model',model,'--initial',','.join(map(str,initial)),'--strain',','.join(map(str,increment))]
    if parameters is not None:command+=['--parameters',','.join(map(str,parameters))]
    result=subprocess.run(command,text=True,capture_output=True,timeout=30)
    if result.returncode not in (0,1):raise AssertionError(result.stderr)
    return json.loads(result.stdout)

class ParentResetLanguageTests(unittest.TestCase):
    def test_pure_parent_selection_zero_and_positive_boundary(self):
        model=load(FIXTURES/'parent-reset.json');s=state()
        self.assertEqual(prepare_increment(model,s,[-.5,0,0,0,0,0])['anchor'],1)
        for de in ([0]*6,[.5,0,0,0,0,0]):self.assertEqual(prepare_increment(model,s,de),s)
        self.assertEqual(s,state())
        # Values and guards all read the original parent, regardless of order.
        model['increment_reset']['updates']=[dict(target='coordinate',guard='-1',value='anchor'),dict(target='anchor',guard='coordinate - 2',value='coordinate')]
        validate(model)
        for updates in (model['increment_reset']['updates'],list(reversed(model['increment_reset']['updates']))):
            model['increment_reset']['updates']=updates
            prepared=prepare_increment(model,s,[0]*6)
            self.assertEqual((prepared['coordinate'],prepared['anchor']),(0,1))

    def test_nonfinite_parent_and_prepared_derived_values(self):
        for suffix in ('nonfinite-derived','prepared-derived'):
            model=load(FIXTURES/('parent-'+suffix+'.json'));initial=state()
            with self.subTest(suffix=suffix),self.assertRaises((ValueError,ZeroDivisionError)):
                prepare_increment(model,initial,[-.5,0,0,0,0,0])
            self.assertEqual(initial,state())

    def test_invalid_shapes_units_scopes_and_duplicate_targets(self):
        model=load(FIXTURES/'parent-reset.json')
        changes=[lambda m:m['increment_reset'].update(scope='substep'),
                 lambda m:m['increment_reset']['updates'][0].update(guard='de'),
                 lambda m:m['increment_reset']['updates'][0].update(guard='coordinate < 0'),
                 lambda m:m['increment_reset']['updates'][0].update(value='sigma'),
                 lambda m:m['increment_reset']['updates'][0].update(value='p_ref'),
                 lambda m:m['increment_reset']['updates'][0].update(target='missing'),
                 lambda m:m['increment_reset']['updates'].append(copy.deepcopy(m['increment_reset']['updates'][0])),
                 lambda m:m['state'][2].update(transient=True),
                 lambda m:m['increment_reset']['updates'][0].update(value='time')]
        for change in changes:
            bad=copy.deepcopy(model);change(bad)
            with self.subTest(change=change),self.assertRaises(ValidationError):validate(bad)
        physical=load(FIXTURES/'maxwell.json');physical['increment_reset']=model['increment_reset']
        with self.assertRaises(ValidationError):validate(physical)

    def test_nonfinite_guard_and_lazy_values(self):
        model=load(FIXTURES/'parent-reset.json')
        model['increment_reset']['updates'][0].update(guard='exp(coordinate * 1000)',value='sqrt(-1)')
        validate(model)
        with self.assertRaises((OverflowError,ValueError)):prepare_increment(model,state(),[0]*6)
        model['increment_reset']['updates'][0]['guard']='1'
        self.assertEqual(prepare_increment(model,state(),[0]*6),state())

class ParentResetNumericalTests(unittest.TestCase):
    def test_analytical_matrix_and_python_preparation(self):
        cases=json.loads((ROOT/'tests/fixtures/parent-reset-cases.json').read_text())['cases']
        for case in cases:
            with self.subTest(case=case['name']):
                result=run(case['initial'],case['increment'],case['model'],case['parameters'])
                self.assertEqual(result['ok'],case['ok'],result)
                self.assertEqual(len(result['state']),len(case['expected']))
                for a,b in zip(result['state'],case['expected']):self.assertAlmostEqual(a,b,delta=case.get('tolerance',1e-10))
                for key in ('substeps','rejected'):self.assertGreaterEqual(result['diagnostics'][key],case.get('minimum_'+key,0))
                if not case['ok']:self.assertEqual(result['state'],case['initial'])
        # Preparation agrees with the full native step for frozen memory;
        # continuous coordinates and stress deliberately evolve afterwards.
        for suffix in ('reset','residual','tensor','simultaneous','derived'):
            model=load(FIXTURES/('parent-'+suffix+'.json'))
            initial={f['name']:copy.deepcopy(f['initial']) for f in model['state']}
            prepared=prepare_increment(model,initial,[-.5,0,0,0,0,0])
            vector=[v for f in model['state'] for v in (initial[f['name']] if f['shape']=='sym' else [initial[f['name']]])]
            actual=run(vector,[-.5,0,0,0,0,0],model['id']);self.assertTrue(actual['ok'])
            offset=0
            for f in model['state']:
                size=6 if f['shape']=='sym' else 1
                if f['name'] in ('anchor','memory'):
                    expected=prepared[f['name']] if size==6 else [prepared[f['name']]]
                    self.assertEqual(actual['state'][offset:offset+size],expected)
                offset+=size

    def test_reversal_boundary_multiple_reversals_and_zero(self):
        original=flat(state());current=original
        # Derived directly from a'=d(volume strain), with a frozen parent anchor.
        for increment,coordinate,anchor in [(-.5,.5,1),(-1,-.5,1),(.25,-.25,-.5),(.5,.25,-.5),(-.1,.15,.25),(0,.15,.25)]:
            result=run(current,[increment,0,0,0,0,0]);self.assertTrue(result['ok'],result)
            self.assertAlmostEqual(result['state'][6],coordinate,places=12)
            self.assertAlmostEqual(result['state'][7],anchor,places=12)
            current=result['state']
        self.assertEqual(original,flat(state()))

    def test_reset_frozen_across_cutbacks_and_parent_partition(self):
        initial=flat(state())
        result=run(initial,[-1,0,0,0,0,0],model='test-parent-reset-cutback')
        self.assertTrue(result['ok'],result);self.assertGreater(result['diagnostics']['rejected'],0)
        self.assertGreater(result['diagnostics']['substeps'],2)
        self.assertEqual(result['state'][7],1)
        self.assertAlmostEqual(result['state'][6],math.exp(-1),delta=2e-5)
        # Same straight loading path under two caller partitions: reset once at
        # the first parent, then preserve the anchor during continued unloading.
        first=run(initial,[-.5,0,0,0,0,0],model='test-parent-reset-cutback')
        second=run(first['state'],[-.5,0,0,0,0,0],model='test-parent-reset-cutback')
        self.assertTrue(first['ok'] and second['ok'])
        self.assertEqual(second['state'][7],1)
        self.assertAlmostEqual(second['state'][6],result['state'][6],delta=2e-5)

    def test_internal_crossing_and_explicit_caller_partition(self):
        initial=flat(state());de=[-.5,0,0,0,0,0]
        whole=run(initial,[-1,0,0,0,0,0],model='test-parent-boundary-cutback')
        first=run(initial,de,model='test-parent-boundary-cutback')
        second=run(first['state'],de,model='test-parent-boundary-cutback')
        self.assertTrue(whole['ok'] and first['ok'] and second['ok'])
        self.assertEqual(whole['state'][7],0);self.assertEqual(first['state'][7],0)
        self.assertEqual(second['state'][7],first['state'][6])
        self.assertAlmostEqual(whole['state'][6],second['state'][6],delta=2e-5)

    def test_failed_late_substep_restores_pre_reset_state(self):
        initial=flat(state());result=run(initial,[-3,0,0,0,0,0],parameters=[1000,1.1])
        self.assertFalse(result['ok']);self.assertGreater(result['diagnostics']['substeps'],0)
        self.assertEqual(result['state'],initial)

    def test_repeated_outer_trials_do_not_accumulate_resets(self):
        initial=flat(state())
        first=run(initial,[-.5,0,0,0,0,0]);run(initial,[.7,0,0,0,0,0])
        repeated=run(initial,[-.5,0,0,0,0,0]);self.assertEqual(first,repeated)
        # Actual outer stress-control Newton/perturbation calls use the same
        # immutable parent. For isotropic toy stiffness, the radial solve has
        # exactly zero lateral increment and the selected anchor is one.
        result=subprocess.run([str(SOLVER),'--mode','run','--model','test-parent-reset','--target','-.01','--steps','1','--protocol','1'],text=True,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        output=json.loads(result.stdout);self.assertTrue(output['ok'])
        self.assertAlmostEqual(output['points'][-1]['state'][6],.99,places=10)
        self.assertEqual(output['points'][-1]['state'][7],1)
