"""Arithmetic transaction oracles; no constitutive or integration claims."""
import copy
import json
import math
import unittest

from atlas.dsl import ValidationError
from atlas.history import advance, make_snapshot, validate_program
from atlas.model import ROOT


def fixture():
    program = json.loads((ROOT/'fixtures/history/ordered-copy.json').read_bytes())
    values = {'x': 2., 'y': 5., 'lag': 11., 'seed': 7., 'mode': 0.,
              'clock': 3., 'stress': [10., 20., 30., 0., 0., 0.]}
    inputs = {'delta': 4., 'dt': .5, 'prepare': 0., 'load': [1., 2., 3., 0., 0., 0.]}
    return program, values, inputs


class HistoryTests(unittest.TestCase):
    def test_simultaneous_writes_and_ordered_snapshots(self):
        program, values, inputs = fixture()
        parent = make_snapshot(program, values)
        original = copy.deepcopy(parent)
        result = advance(program, parent, inputs)
        self.assertTrue(result['ok'])
        # advance reads x/y simultaneously; ordered reads that output's x plus OLD lag.
        self.assertEqual(result['snapshot']['values'], dict(values, x=9., y=2., lag=20., clock=3.5,
                                                           stress=[11., 22., 33., 0., 0., 0.]))
        self.assertEqual(parent, original)
        self.assertEqual(result['snapshot']['generation'], 1)
        self.assertEqual(result['snapshot']['preparation_epoch'], 0)

    def test_prepare_changes_old_history_base_and_commits_once(self):
        program, values, inputs = fixture(); inputs['prepare'] = 1.
        parent = make_snapshot(program, values, generation=6, preparation_epoch=3)
        result = advance(program, parent, inputs)
        self.assertTrue(result['ok'])
        self.assertEqual(result['snapshot']['values'], dict(values, x=6., y=5., seed=2., mode=1.,
                                                           lag=17., clock=3.5, stress=[11.,22.,33.,0.,0.,0.]))
        self.assertEqual(result['snapshot']['generation'], 7)
        self.assertEqual(result['snapshot']['preparation_epoch'], 4)
        self.assertEqual(result['events'][0], {'phase': 'prepared', 'kind': 'prepare'})

    def test_failure_after_preparation_rolls_back_every_field(self):
        program, values, inputs = fixture(); inputs['prepare'] = 1.
        program['phases'][-1]['checks'] = ['x < 0']
        parent = make_snapshot(program, values, generation=6, preparation_epoch=3)
        original = copy.deepcopy(parent)
        result = advance(program, parent, inputs)
        self.assertFalse(result['ok']); self.assertEqual(result['snapshot'], original)
        self.assertIs(result['snapshot'], parent)
        self.assertEqual(parent, original); self.assertEqual(result['events'], [])
        self.assertEqual(result['diagnostics']['failed_phase'], 'ordered')

    def test_guard_strict_negative_and_lazy_rhs(self):
        program, values, inputs = fixture()
        phase = program['phases'][-1]
        phase.update(guard='gate', bindings={'gate': {'input': 'prepare'}}, writes={'x': 'sqrt(-1)'})
        for gate in (0., 2.):
            with self.subTest(gate=gate):
                inputs['prepare'] = gate
                result = advance(program, make_snapshot(program, values), inputs)
                self.assertTrue(result['ok'])
                self.assertNotIn({'phase': 'ordered', 'kind': 'advance'}, result['events'])
        inputs['prepare'] = -1.
        result = advance(program, make_snapshot(program, values), inputs)
        self.assertFalse(result['ok']); self.assertEqual(result['events'], [])

    def test_inactive_phase_checks_still_validate_output(self):
        program, values, inputs = fixture()
        program['phases'][-1].update(guard='0', checks=['x < 0'])
        parent = make_snapshot(program, values)
        self.assertFalse(advance(program, parent, inputs)['ok'])

    def test_nonfinite_intermediate_guards_checks_and_writes_fail(self):
        for mode in ('guard', 'write', 'check'):
            program, values, inputs = fixture(); phase = program['phases'][-1]
            if mode == 'guard': phase['guard'] = '1e308*1e308'
            if mode == 'write': phase['writes']['x'] = '1/(1/(1e308*1e308)+1)'
            if mode == 'check': phase['checks'] = ['1e308*1e308 > 0']
            with self.subTest(mode=mode):
                parent = make_snapshot(program, values)
                result = advance(program, parent, inputs)
                self.assertFalse(result['ok']); self.assertEqual(result['snapshot'], parent)

    def test_lazy_select_does_not_evaluate_inactive_branch(self):
        program, values, inputs = fixture()
        program['phases'][-1]['writes']['x'] = 'select(1 > 0, 8, sqrt(-1))'
        result = advance(program, make_snapshot(program, values), inputs)
        self.assertTrue(result['ok']); self.assertEqual(result['snapshot']['values']['x'], 8.)

    def test_repeated_candidates_and_serialized_restart(self):
        program, values, inputs = fixture(); parent = make_snapshot(program, values)
        first = advance(program, parent, inputs)
        other = advance(program, parent, dict(inputs, delta=1.))
        self.assertEqual(first, advance(program, parent, inputs))
        self.assertEqual(other['snapshot']['generation'], 1)
        restored = json.loads(json.dumps(first['snapshot'], allow_nan=False))
        self.assertEqual(advance(program, restored, inputs), advance(program, first['snapshot'], inputs))
        self.assertEqual(parent['values'], values)
        original_inputs = copy.deepcopy(inputs)
        first['snapshot']['values']['stress'][0] = -999.
        self.assertEqual(parent['values'], values)
        self.assertEqual(inputs, original_inputs)

    def test_invalid_phase_graph_binding_or_units_rejected(self):
        changes = {
            'future': lambda p: p['phases'][1]['bindings']['oldx'].update(snapshot='ordered'),
            'cycle': lambda p: p['phases'][1].update(base='copy'),
            'pre_reset_read': lambda p: p['phases'][1]['bindings']['oldx'].update(snapshot='parent'),
            'pre_reset_base': lambda p: p['phases'][1].update(base='parent'),
            'unit': lambda p: p['phases'][1]['writes'].update(x='dt'),
            'shape': lambda p: p['phases'][1]['writes'].update(x='load'),
            'unknown': lambda p: p['phases'][1]['writes'].update(x='unknown'),
            'prep_write': lambda p: p['phases'][1]['writes'].update(seed='oldx'),
            'extra': lambda p: p.update(unsupported_capability=True),
            'source': lambda p: p.update(sources=[]),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                program, _, _ = fixture(); change(program)
                with self.assertRaises(ValidationError): validate_program(program)

    def test_invalid_parent_input_and_lineage_rejected(self):
        program, values, inputs = fixture(); parent = make_snapshot(program, values)
        for bad in (dict(inputs, extra=1), dict(inputs, delta=True), dict(inputs, delta=math.nan),
                    dict(inputs, load=[1,2]), {k:v for k,v in inputs.items() if k!='dt'}):
            with self.assertRaises(ValidationError): advance(program, parent, bad)
        for change in (lambda p: p.update(program_sha256='0'*64),
                       lambda p: p.update(generation=True),
                       lambda p: p.update(preparation_epoch=-1),
                       lambda p: p['values'].update(mode=.5),
                       lambda p: p['values'].pop('lag'),
                       lambda p: p['values'].update(stress=[math.inf]*6)):
            bad = copy.deepcopy(parent); change(bad)
            with self.assertRaises(ValidationError): advance(program, bad, inputs)

    def test_failed_trial_cannot_consume_reset_command(self):
        program, values, inputs = fixture(); parent = make_snapshot(program, values)
        bad = dict(inputs, prepare=1., delta=-100.)
        failure = advance(program, parent, bad)
        self.assertFalse(failure['ok'])
        success = advance(program, parent, dict(inputs, prepare=1.))
        self.assertTrue(success['ok'])
        self.assertEqual(success['snapshot']['preparation_epoch'], 1)
        self.assertEqual(parent['preparation_epoch'], 0)

    def test_invalid_mode_and_counter_exhaustion_roll_back(self):
        program, values, inputs = fixture()
        program['phases'][-1]['writes']['mode'] = '0.5'
        parent = make_snapshot(program, values)
        result = advance(program, parent, inputs)
        self.assertFalse(result['ok']); self.assertEqual(result['snapshot'], parent)
        self.assertEqual(result['events'], [])
        program, values, inputs = fixture()
        for counters, commands in (({'generation': 9007199254740991}, inputs),
                                   ({'preparation_epoch': 9007199254740991}, dict(inputs, prepare=1.))):
            parent = make_snapshot(program, values, **counters)
            result = advance(program, parent, commands)
            self.assertFalse(result['ok']); self.assertEqual(result['snapshot'], parent)
            self.assertEqual(result['events'], [])

    def test_huge_integer_validation_is_bounded(self):
        huge = 10**1000
        for kind in ('unit', 'enum'):
            program, _, _ = fixture()
            if kind == 'unit': program['fields']['x']['unit'] = {'si':[huge,0,0,0]}
            else: program['fields']['mode']['enum'] = [0,huge]
            with self.subTest(kind=kind):
                with self.assertRaises(ValidationError): validate_program(program)
        program, values, inputs = fixture(); parent = make_snapshot(program, values)
        with self.assertRaises(ValidationError): advance(program, parent, dict(inputs, delta=huge))
        with self.assertRaises(ValidationError): make_snapshot(program, dict(values, x=huge))
        parent['generation'] = huge
        with self.assertRaises(ValidationError): advance(program, parent, inputs)

    def test_layout_and_phase_budgets_rejected(self):
        program, _, _ = fixture()
        for n in range(40): program['fields']['extra'+str(n)] = {'shape':'scalar','unit':'1','storage':'state'}
        with self.assertRaises(ValidationError): validate_program(program)
        program, _, _ = fixture(); program['phases'] *= 30
        with self.assertRaises(ValidationError): validate_program(program)


if __name__ == '__main__': unittest.main()
