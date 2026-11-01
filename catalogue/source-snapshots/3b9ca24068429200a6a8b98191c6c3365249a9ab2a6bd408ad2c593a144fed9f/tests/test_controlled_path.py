"""Analytical and transaction checks for the separate controlled-path API."""
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

from atlas.compiler import generate
from atlas.dsl import ValidationError
from atlas.model import ROOT, integration_kind, load, validate
from atlas.path import Context, Settings, advance, initialize


class ControlledPathTests(unittest.TestCase):
    def setUp(self):
        self.model = load(ROOT / 'tests/fixtures/controlled-path/synthetic-model.json')
        self.state = {'vscalar': 1., 'A': [0.] * 6}
        self.controls = {'load': 2., 'unused': 3.}
        self.params = {'pref': 1000.}
        self.parent = initialize(self.model, self.state, 7., self.controls, self.params)

    def advance(self, **kwargs):
        args = dict(model=self.model, parent=self.parent, progress=.25,
                    controls_start=self.controls, controls_end={'load': 4., 'unused': 3.})
        args.update(kwargs)
        return advance(**args)

    def test_linear_control_and_derivative_scalar_tensor(self):
        before = copy.deepcopy(self.parent)
        result = self.advance()
        self.assertAlmostEqual(result.state['vscalar'], 3.75, places=12)
        for actual, expected in zip(result.state['A'], [2750.] * 3 + [0.] * 3):
            self.assertAlmostEqual(actual, expected, places=9)
        self.assertEqual(result.coordinate, 7.25)
        self.assertEqual(self.parent, before)
        restart = initialize(self.model, result.state, result.coordinate, result.controls, result.parameters)
        self.assertEqual(advance(self.model, restart, 0, result.controls, result.controls), result)

    def test_rejection_preserves_whole_parent_and_recovery(self):
        before = copy.deepcopy(self.parent)
        failures = [dict(progress=x) for x in (-1, float('nan'), float('inf'))]
        failures += [dict(progress=60, settings=Settings(max_step=.1)), dict(progress=0), dict(controls_start={'load': 1., 'unused': 3.}),
                     dict(controls_end={'load': 2.}),
                     dict(controls_end={'load': 2., 'unused': float('nan')}),
                     dict(controls_end={**self.controls, 'extra': 1.}),
                     dict(settings=Settings(relative=0)),
                     dict(parent=Context(self.state, 1e30, self.controls, self.params), progress=1)]
        expected = self.advance()
        for overrides in failures:
            with self.subTest(overrides=overrides):
                with self.assertRaises((ValueError, ValidationError, ArithmeticError)):
                    self.advance(**overrides)
                self.assertEqual(self.parent, before)
                self.assertEqual(self.advance(), expected)

    def test_initialization_requires_complete_finite_context(self):
        failures = [({'vscalar': float('inf'), 'A': [0.] * 6}, self.params),
                    ({'vscalar': 1., 'A': [0.] * 5}, self.params),
                    ({'vscalar': 1.}, self.params),
                    (self.state, {'pref': -1}),
                    (self.state, {**self.params, 'extra': 0})]
        for state, params in failures:
            with self.subTest(state=state, params=params), self.assertRaises((ValueError, ValidationError)):
                initialize(self.model, state, 0, self.controls, params)

    def test_curved_analytical_solution_and_trial_budget(self):
        model = load(ROOT / 'tests/fixtures/controlled-path/synthetic-curved.json')
        parent = initialize(model, self.state, 0, self.controls, self.params)
        result = advance(model, parent, .5, self.controls, self.controls)
        self.assertLess(abs(result.state['vscalar'] - math.exp(.5)), 2e-7)
        with self.assertRaises(ValueError):
            advance(model, parent, .5, self.controls, self.controls, Settings(max_trials=1))

    def test_input_contract_and_compiler_partition(self):
        self.assertEqual(integration_kind(self.model), 'path_ode')
        for mutate in (
            lambda m: m['parameters'].update(u=dict(unit='1', default=1, min=0, max=2)),
            lambda m: m['formulation']['inputs']['equation']['du'].update(unit='Pa'),
            lambda m: m['formulation']['inputs']['equation']['du']['binding'].update(derivative_order=0),
            lambda m: m['formulation']['inputs']['equation']['u']['binding'].update(control='std'),
        ):
            invalid = copy.deepcopy(self.model)
            mutate(invalid)
            with self.assertRaises(ValidationError):
                validate(invalid)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                generate(directory, [ROOT / 'models/linear-elastic.json', ROOT / 'tests/fixtures/controlled-path/synthetic-model.json'])

    def test_named_norsand_example_matches_qualified_endpoint(self):
        example = json.loads((ROOT / 'catalogue/path-examples/norsand-1993-loose-constant-cell.json').read_text())
        model = load(ROOT / 'models/research/norsand/norsand-jefferies-1993-active-axial.json')
        parent = initialize(model, **example['context'])
        result = advance(model, parent, example['advance']['progress'], parent.controls,
                         example['advance']['controls_end'], Settings(**example['execution']))
        for value, expected in zip(result.state.values(), example['qualification']['endpoint']['state']):
            self.assertLess(abs(value - expected), 2e-11)
        self.assertAlmostEqual(result.state['eq'] - result.coordinate,
                               parent.state['eq'] - parent.coordinate, places=12)


if __name__ == '__main__':
    unittest.main()
