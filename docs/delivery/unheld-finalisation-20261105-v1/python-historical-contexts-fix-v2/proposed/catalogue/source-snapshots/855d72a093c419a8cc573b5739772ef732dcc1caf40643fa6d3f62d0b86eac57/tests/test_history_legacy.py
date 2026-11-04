"""Full-state transport oracles, including an unchanged legacy preparation call."""
import copy
import json
import unittest

from atlas.dsl import ValidationError
from atlas.history import MAX_COUNTER
from atlas.history_legacy import advance_legacy, make_legacy_snapshot
from atlas.model import ROOT, defaults, load, prepare_increment

FIXTURES = ROOT/'tests/fixtures/time'


def fixture(suffix='reset', generation=0):
    model = load(FIXTURES/('parent-'+suffix+'.json'))
    state = {f['name']: copy.deepcopy(f['initial']) for f in model['state']}
    parent = make_legacy_snapshot(model, state, defaults(model), [0.]*6, generation=generation)
    return model, state, parent


def named(snapshot):
    return {f['name']: snapshot['history']['values'][f['slot']] for f in snapshot['binding']['layout']}


def identity(model, state, increment, parameters):
    return {'ok': True, 'state': state, 'diagnostics': {'calls': 1}}


class LegacyHistoryTests(unittest.TestCase):
    def test_complete_identity_transport_and_copy_isolation(self):
        model, state, parent = fixture(); original = copy.deepcopy(parent); before_model = copy.deepcopy(model)
        increment = [-.5,0,0,0,0,0]
        def mutate(m, s, de, p):
            self.assertEqual(s, state); self.assertEqual(de, increment)
            self.assertEqual(p, defaults(model)); self.assertEqual(m, model)
            m['description'] = 'callback local edit'; de[0] = 77; p['p_ref'] = 77
            s['anchor'] = 9
            return {'ok':True,'state':s,'diagnostics':{'note':['finite',None,True]}}
        result = advance_legacy(model, parent, increment, mutate)
        self.assertTrue(result['ok']); self.assertEqual(named(result['snapshot'])['anchor'], 9)
        self.assertEqual(result['snapshot']['strain'], increment)
        self.assertEqual(result['snapshot']['history']['generation'],1)
        self.assertEqual(result['snapshot']['history']['preparation_epoch'],0)
        self.assertEqual(result['events'],[])
        self.assertEqual(parent,original); self.assertEqual(model,before_model)
        self.assertEqual(increment,[-.5,0,0,0,0,0])
        result['snapshot']['history']['values']['f0'][0] = -999
        self.assertEqual(parent,original)

    def test_original_parent_and_existing_reset_selection_once(self):
        for suffix in ('reset','residual','tensor','simultaneous','derived'):
            with self.subTest(suffix=suffix):
                model, state, parent = fixture(suffix); calls=[]; de=[-.5,0,0,0,0,0]
                def full(m,s,d,p):
                    calls.append(copy.deepcopy(s)); self.assertEqual(s,state)
                    return {'ok':True,'state':prepare_increment(m,s,d,p),'diagnostics':{}}
                result=advance_legacy(model,parent,de,full)
                self.assertTrue(result['ok']); self.assertEqual(calls,[state])
                self.assertEqual(named(result['snapshot']),prepare_increment(model,state,de,defaults(model)))

    def test_failure_exception_and_malformed_response_exact_rollback(self):
        model, state, parent=fixture(); before=copy.deepcopy(parent)
        failures=[lambda *args: (_ for _ in ()).throw(RuntimeError('backend failure')),
                  lambda *args: {'ok':False,'state':dict(state,anchor=99),'diagnostics':{'substeps':2}},
                  lambda *args: {'ok':1,'state':state,'diagnostics':{}},
                  lambda *args: {'ok':True,'state':dict(state,anchor=float('nan')),'diagnostics':{}},
                  lambda *args: {'ok':True,'state':state,'diagnostics':{'bad':float('inf')}},
                  lambda *args: {'ok':True,'state':{},'diagnostics':{}},
                  lambda *args: {'ok':True,'state':state,'diagnostics':{} ,'message':12},
                  lambda *args: {'ok':True,'state':state,'diagnostics':{'bad':object()}},
                  lambda *args: None]
        for callback in failures:
            with self.subTest(callback=callback):
                result=advance_legacy(model,parent,[-.5,0,0,0,0,0],callback)
                self.assertFalse(result['ok']);self.assertIs(result['snapshot'],parent)
                self.assertEqual(parent,before);self.assertEqual(result['events'],[])

    def test_eager_derived_and_inactive_reset_preserve_legacy_semantics(self):
        for suffix in ('nonfinite-derived','prepared-derived'):
            model,state,parent=fixture(suffix)
            def full(m,s,d,p):return {'ok':True,'state':prepare_increment(m,s,d,p),'diagnostics':{}}
            result=advance_legacy(model,parent,[-.5,0,0,0,0,0],full)
            self.assertFalse(result['ok']);self.assertIs(result['snapshot'],parent)
        model,state,parent=fixture()
        model['increment_reset']['updates'][0].update(guard='1',value='sqrt(-1)')
        parent=make_legacy_snapshot(model,state,defaults(model),[0.]*6)
        def full(m,s,d,p):return {'ok':True,'state':prepare_increment(m,s,d,p),'diagnostics':{}}
        self.assertTrue(advance_legacy(model,parent,[0.]*6,full)['ok'])

    def test_outer_trials_and_restart_are_pure(self):
        model,state,parent=fixture(); inc=[-.5,0,0,0,0,0]
        first=advance_legacy(model,parent,inc,identity)
        advance_legacy(model,parent,[.7,0,0,0,0,0],identity)
        self.assertEqual(advance_legacy(model,parent,inc,identity),first)
        restored=json.loads(json.dumps(first['snapshot'],allow_nan=False))
        self.assertEqual(advance_legacy(model,restored,inc,identity),advance_legacy(model,first['snapshot'],inc,identity))

    def test_binding_and_snapshot_tampering_rejected_before_callback(self):
        model,state,parent=fixture(); calls=[]
        def call(*args):calls.append(1);return identity(*args)
        mutations=[lambda p:p['binding'].update(model_sha256='0'*64),
                   lambda p:p['binding']['parameters'].update(p_ref=1001),
                   lambda p:p['binding']['layout'][0].update(offset=1),
                   lambda p:p['binding']['layout'][0].update(transient=0),
                   lambda p:p['history'].update(program_sha256='0'*64),
                   lambda p:p['history'].update(generation=True),
                   lambda p:p['history'].update(preparation_epoch=1),
                   lambda p:p['strain'].__setitem__(0,1),
                   lambda p:p['history']['values'].pop('f0')]
        for change in mutations:
            bad=copy.deepcopy(parent);change(bad)
            with self.assertRaises(ValidationError):advance_legacy(model,bad,[0.]*6,call)
        self.assertEqual(calls,[])

    def test_parameter_order_is_part_of_wire_identity(self):
        model,state,parent=fixture(); reordered=copy.deepcopy(model)
        reordered['parameters']=dict(reversed(list(reordered['parameters'].items())))
        self.assertNotEqual(list(reordered['parameters']),list(model['parameters']))
        with self.assertRaises(ValidationError):advance_legacy(reordered,parent,[0.]*6,identity)

    def test_counter_overflow_and_strain_overflow_rollback(self):
        model,state,parent=fixture(generation=MAX_COUNTER);calls=[]
        def call(*args):calls.append(1);return identity(*args)
        result=advance_legacy(model,parent,[0.]*6,call)
        self.assertFalse(result['ok']);self.assertIs(result['snapshot'],parent);self.assertEqual(calls,[])
        model,state,_=fixture();parent=make_legacy_snapshot(model,state,defaults(model),[1e308]*6)
        result=advance_legacy(model,parent,[1e308]*6,identity)
        self.assertFalse(result['ok']);self.assertIs(result['snapshot'],parent)

    def test_invalid_inputs_reject_without_material_evaluation(self):
        model,state,parent=fixture()
        for de in ([0]*5,[False]*6,[float('nan')]*6,[10**1000]*6):
            with self.assertRaises(ValidationError):advance_legacy(model,parent,de,identity)
        with self.assertRaises(ValidationError):make_legacy_snapshot(model,state,{},[0.]*6)
        with self.assertRaises(ValidationError):make_legacy_snapshot(model,state,defaults(model),[0.]*5)
        timed=load(FIXTURES/'maxwell.json')
        with self.assertRaises(ValidationError):make_legacy_snapshot(timed,{}, {},[0.]*6)

    def test_all_five_public_layouts_roundtrip_without_reinterpretation(self):
        baseline=['drucker-prager','hypoplastic-sand-igs97','hypoplastic-sand-vw96','linear-elastic','modified-cam-clay']
        paths=[ROOT/'models'/(name+'.json') for name in baseline]
        self.assertTrue(all(path.is_file() for path in paths))
        for path in paths:
            model=load(path)
            with self.subTest(model=model['id']):
                state={f['name']:copy.deepcopy(f['initial']) for f in model['state']}
                parent=make_legacy_snapshot(model,state,defaults(model),[0.]*6)
                restored=json.loads(json.dumps(parent,allow_nan=False,sort_keys=True))
                result=advance_legacy(model,restored,[0.]*6,identity)
                self.assertTrue(result['ok']);self.assertEqual(named(result['snapshot']),state)
                self.assertEqual(result['snapshot']['binding']['parameter_order'],list(model['parameters']))

    def test_explicit_v03_draft_is_rejected_by_legacy_transport(self):
        model=load(ROOT/'models/barodesy-clay-2017.json')
        self.assertEqual(model['schema_version'],'0.3')
        state={f['name']:copy.deepcopy(f['initial']) for f in model['state']}
        with self.assertRaisesRegex(ValidationError,'model schema 0.1'):
            make_legacy_snapshot(model,state,defaults(model),[0.]*6)

    def test_transient_transport_is_not_reclassified_as_physical_history(self):
        model=load(ROOT/'models/drucker-prager.json')
        state={f['name']:copy.deepcopy(f['initial']) for f in model['state']}
        parent=make_legacy_snapshot(model,state,defaults(model),[0.]*6)
        self.assertEqual(len(parent['binding']['layout']),len(model['state']))
        transient=[f for f in parent['binding']['layout'] if f['transient']]
        self.assertTrue(transient)
        self.assertTrue(advance_legacy(model,parent,[0.]*6,identity)['ok'])


if __name__=='__main__':unittest.main()
