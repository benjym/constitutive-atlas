"""State lifecycle and explicit initialization, independent of preparation recipes."""
import copy
import json
import os
import subprocess
import unittest

from atlas.dsl import ValidationError
from atlas.initialization import canonical_hash, initialize, initialize_state
from atlas.model import ROOT, defaults, load, migrate_formulation, state_role, validate


def migrated(name='linear-elastic'):
    return migrate_formulation(load(ROOT/'models'/f'{name}.json'))


def persistent_examples(model):
    return {f['name']:copy.deepcopy(f['initial']) for f in model['state'] if state_role(f)=='persistent'}


class StateContractTests(unittest.TestCase):
    def test_migration_records_roles_without_guessing_history_meaning(self):
        model=migrated('modified-cam-clay')
        fields={f['name']:f for f in model['state']}
        self.assertEqual(fields['gamma']['semantics']['role'],'plastic_multiplier')
        self.assertEqual(fields['pc']['semantics']['quantity'],'unspecified')
        self.assertEqual(fields['sigma']['semantics']['transformation'],'symmetric_spatial_tensor')
        self.assertEqual(model['initialization']['required_state'],['sigma','e','pc'])
        self.assertTrue(all('transient' not in f and 'multiplier' not in f for f in fields.values()))
        from atlas.refinement import state_layout
        layout=state_layout(model,list(defaults(model).values()))
        self.assertTrue(layout[-1]['transient'])
        self.assertFalse(layout[0]['transient'])
        h=next(f for f in migrated('hypoplastic-sand-igs97')['state'] if f['name']=='h')
        self.assertEqual(h['semantics']['transformation'],'fixed_components')

    def test_state_semantics_must_match_shape_and_lifecycle(self):
        for mutate in [
            lambda m:m['state'][0].pop('semantics'),
            lambda m:m['state'][0]['semantics'].update(transformation='scalar_invariant'),
            lambda m:m['state'][1]['semantics'].update(transformation='symmetric_spatial_tensor'),
            lambda m:m['state'][1]['semantics'].update(quantity='  '),
            lambda m:m['state'][0]['semantics'].update(quantity='unspecified'),
            lambda m:m['state'][-1].update(initial=1),
            lambda m:m['state'][-1].update(transient=True),
            lambda m:m['equations'].update(gamma='gamma_n'),
        ]:
            bad=migrated('modified-cam-clay');mutate(bad)
            with self.subTest(model=bad),self.assertRaises(ValidationError):validate(bad)
        rate=migrated('hypoplastic-sand-vw96')
        rate['state'][1]['semantics']['role']='increment_unknown'
        rate['state'][1]['initial']=0
        rate['initialization']['required_state']=['sigma']
        with self.assertRaises(ValidationError):validate(rate)
        tensor=migrated('hypoplastic-sand-igs97')
        tensor['state'][-1]['semantics'].update(quantity='intergranular_strain',transformation='symmetric_spatial_tensor')
        validate(tensor)

    def test_initialization_contract_is_complete_and_closed(self):
        for mutate in [
            lambda m:m.pop('initialization'),
            lambda m:m['initialization'].update(required_state=['sigma']),
            lambda m:m['initialization'].update(required_state=['sigma','e','gamma']),
            lambda m:m['initialization'].update(required_state=['e','sigma']),
            lambda m:m['initialization'].update(default_policy='use_literals'),
            lambda m:m['initialization'].update(method='project_to_yield_surface'),
            lambda m:m['initialization'].update(validation='none'),
        ]:
            bad=migrated('drucker-prager');mutate(bad)
            with self.subTest(model=bad),self.assertRaises(ValidationError):validate(bad)

    def test_explicit_state_fills_only_temporary_slots_and_does_not_mutate(self):
        model=migrated('modified-cam-clay');state=persistent_examples(model);parameters=defaults(model)
        before=copy.deepcopy((model,state,parameters))
        result=initialize_state(model,state,parameters)
        self.assertEqual((model,state,parameters),before)
        self.assertEqual(result['named_state']['gamma'],0)
        self.assertEqual(len(result['initial']),9)
        self.assertEqual(result['provenance']['model_sha256'],canonical_hash(model))
        result['named_state']['sigma'][0]=0
        self.assertEqual(state['sigma'][0],100000)

    def test_initialization_rejects_missing_state_and_invalid_values(self):
        model=migrated('drucker-prager');state=persistent_examples(model);parameters=defaults(model)
        for mutate in [lambda s,p:s.pop('e'), lambda s,p:s.update(gamma=0),
                       lambda s,p:s.update(e=-1), lambda s,p:s.update(e=float('nan')),
                       lambda s,p:s.update(sigma=[0]*5), lambda s,p:s.update(e=True),
                       lambda s,p:p.pop('nu'),lambda s,p:p.update(E=-1),
                       lambda s,p:p.update(E=float('inf'))]:
            s,p=copy.deepcopy((state,parameters));mutate(s,p)
            with self.subTest(state=s,parameters=p),self.assertRaises(ValidationError):initialize_state(model,s,p)
        with self.assertRaises(ValidationError):initialize_state(model,state,parameters,time=0)
        with self.assertRaises(ValidationError):initialize_state(model,state,parameters,loading=[0]*6)

    def test_declared_consistency_and_custom_parameter_scales_are_checked(self):
        model=migrated('modified-cam-clay');state=persistent_examples(model)
        state['pc']=1000
        with self.assertRaises(ValidationError):initialize_state(model,state,defaults(model))
        model=migrated();model['initial_checks']=['e > 0.8']
        with self.assertRaises(ValidationError):initialize_state(model,persistent_examples(model),defaults(model))
        model=migrated();model['parameters']['factor']={'default':1,'min':-1,'max':1,'unit':'1'}
        model['state'][0]['scale']='p_ref * factor'
        parameters=defaults(model);parameters['factor']=-1
        with self.assertRaises(ValidationError):initialize_state(model,persistent_examples(model),parameters)

    def test_physical_initialization_requires_actual_time_and_rate(self):
        model=migrate_formulation(load(ROOT/'tests/fixtures/time/clock.json'))
        state=persistent_examples(model);parameters=defaults(model)
        for kwargs in [{},{'time':3},{'loading':[0]*6},{'time':float('nan'),'loading':[0]*6},
                       {'time':3,'loading':[0]*5}]:
            with self.subTest(kwargs=kwargs),self.assertRaises(ValidationError):initialize_state(model,state,parameters,**kwargs)
        model['initial_checks']=['time > 0 * tau']
        result=initialize_state(model,state,parameters,time=3,loading=[0]*6)
        self.assertEqual(result['initial_time'],3)
        with self.assertRaises(ValidationError):initialize_state(model,state,parameters,time=-3,loading=[0]*6)
        model=migrate_formulation(load(ROOT/'tests/fixtures/time/maxwell-axisymmetric.json'),stress_scope='effective')
        with self.assertRaises(ValidationError):initialize_state(model,persistent_examples(model),defaults(model),time=0,loading=[1,0,1,0,0,0])

    def test_existing_recipe_can_target_reconciled_v03_model(self):
        import json
        old=load(ROOT/'models/research/terracotta-2024-fig1.json')
        recipe=json.loads((ROOT/'initialization/terracotta-2024-fig1-total-stress.json').read_text())
        configuration=json.loads((ROOT/'initialization/terracotta-2024-kaolin-initialization.json').read_text())
        expected=initialize(recipe,configuration,old)
        model=migrate_formulation(old,stress_scope='total')
        recipe['model_sha256']=canonical_hash(model)  # Explicit reconciliation of this unchanged test recipe.
        result=initialize(recipe,configuration,model)
        self.assertEqual(result['named_state'],expected['named_state'])
        self.assertEqual(result['observables_at_time_zero'],expected['observables_at_time_zero'])
        self.assertEqual(result['run_fields'],expected['run_fields'])


@unittest.skipUnless(os.environ.get('ATLAS_STATE_CONTRACT_SOLVER'), 'dedicated native contract solver not supplied')
class NativeStateContractTests(unittest.TestCase):
    def invoke(self, *args):
        process=subprocess.run([os.environ['ATLAS_STATE_CONTRACT_SOLVER'],*args],
                               capture_output=True,text=True,timeout=20)
        result=json.loads(process.stdout)
        self.assertEqual(result['ok'],process.returncode==0,process.stderr)
        return result

    def test_examples_are_not_silent_initial_state(self):
        legacy=self.invoke('--model','linear-elastic','--mode','integrate','--strain','0,0,0,0,0,0')
        self.assertTrue(legacy['ok'])
        current=self.invoke('--model','linear-elastic-v03','--mode','integrate','--strain','0,0,0,0,0,0')
        self.assertFalse(current['ok'])
        self.assertIn('explicit state',current['message'])

    def test_material_updates_match_with_explicit_initialization(self):
        for name in ['linear-elastic','drucker-prager']:
            model=migrated(name)
            initial=initialize_state(model,persistent_examples(model),defaults(model))['initial']
            arguments=['--mode','integrate','--initial',','.join(map(str,initial)),
                       '--strain','0.00001,-0.000005,-0.000005,0,0,0']
            old=self.invoke('--model',name,*arguments)
            new=self.invoke('--model',name+'-v03',*arguments)
            self.assertTrue(new['ok'],new.get('message'))
            self.assertEqual(new['state'],old['state'])

    def test_timed_explicit_state_and_rollback(self):
        args=['--mode','integrate-time','--strain-rate','0,0,0,0,0,0',
              '--start-time','3','--duration','2']
        missing=self.invoke('--model','test-clock-v03',*args)
        self.assertFalse(missing['ok'])
        current=self.invoke('--model','test-clock-v03','--initial','0',*args)
        legacy=self.invoke('--model','test-clock',*args)
        self.assertTrue(current['ok'],current.get('message'))
        self.assertEqual(current['state'],legacy['state'])
        self.assertEqual(current['time'],5)
        failure=self.invoke('--model','test-clock-v03','--initial','0',
                            '--mode','integrate-time','--strain-rate','0,0,0,0,0,0',
                            '--start-time','3','--duration','-1')
        self.assertFalse(failure['ok'])
        self.assertEqual(failure['state'],[0])
        self.assertEqual(failure['time'],3)
