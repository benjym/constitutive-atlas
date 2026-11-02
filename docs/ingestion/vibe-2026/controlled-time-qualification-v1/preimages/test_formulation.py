"""Explicit formulation boundaries and equivalence to preserved definitions."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from atlas.compiler import generate
from atlas.dsl import ValidationError
from atlas.model import ROOT, equation_input_types, integration_kind, interpret, load, migrate_formulation, physical_time, validate
from atlas.structure import check
from tests.test_stress_scope import without_stress_scope_metadata


class FormulationTests(unittest.TestCase):
    def test_explicit_inputs_and_namespaces(self):
        incremental = migrate_formulation(load(ROOT/'models/linear-elastic.json'))
        timed = migrate_formulation(load(ROOT/'tests/fixtures/time/clock.json'))
        self.assertEqual(set(equation_input_types(incremental)), {'de'})
        self.assertEqual(incremental['formulation']['inputs']['advance'], {})
        self.assertEqual(set(equation_input_types(timed)), {'time', 'strain_rate'})
        self.assertEqual(set(timed['formulation']['inputs']['advance']), {'start_time', 'duration'})
        for name in ['start_time', 'duration']:
            bad = copy.deepcopy(timed)
            bad['equations']['x'] = name+' / tau'
            with self.subTest(symbol=name), self.assertRaises(ValidationError):validate(bad)
            bad = copy.deepcopy(timed)
            bad['parameters'][name] = {'default':1, 'min':0, 'max':2, 'unit':'s'}
            with self.subTest(parameter=name), self.assertRaises(ValidationError):validate(bad)
        # A profile requires its declared loading even when this scalar ODE ignores it.
        for loading in [[0]*5, [0]*7, [float('inf')]*6, [True]*6]:
            with self.subTest(loading=loading), self.assertRaises(ValueError):
                interpret(timed, {'x':0}, None, loading, time=3)

    def test_inconsistent_input_contracts_rejected_structurally(self):
        schema = json.loads((ROOT/'schemas/model-v0.3.schema.json').read_text())
        for source in [ROOT/'models/linear-elastic.json', ROOT/'tests/fixtures/time/clock.json']:
            model = migrate_formulation(load(source))
            inputs = model['formulation']['inputs']
            mutations = []
            for group, fields in inputs.items():
                for name, field in fields.items():
                    mutations.append((group,name,None))
                    for key in field:
                        changed = copy.deepcopy(field)
                        changed[key] = 'unsupported'
                        mutations.append((group,name,changed))
            for group, name, field in mutations:
                bad = copy.deepcopy(model)
                if field is None:del bad['formulation']['inputs'][group][name]
                else:bad['formulation']['inputs'][group][name] = field
                with self.subTest(source=source,group=group,name=name,field=field):
                    with self.assertRaises(ValidationError):check(bad,schema)
                    with self.assertRaises(ValidationError):validate(bad)
            for group in ['equation','advance']:
                bad = copy.deepcopy(model)
                bad['formulation']['inputs'][group]['temperature'] = {
                    'quantity':'temperature', 'shape':'scalar', 'unit':'K',
                    'sampling':'stage', 'constraint':'finite'}
                with self.subTest(group=group), self.assertRaises(ValidationError):validate(bad)

    def test_migration_preserves_all_current_definitions(self):
        for path in sorted((ROOT/'models').rglob('*.json')):
            with self.subTest(path=path):
                original_bytes = path.read_bytes()
                old = load(path)
                before = copy.deepcopy(old)
                scope = 'total' if path.name == 'terracotta-2024-fig1.json' else None
                new = migrate_formulation(old, stress_scope=scope)
                self.assertEqual(old, before)
                self.assertEqual(path.read_bytes(), original_bytes)
                self.assertEqual(new['schema_version'], '0.3')
                self.assertNotIn('integration', new)
                self.assertEqual(physical_time(old), physical_time(new))
                self.assertEqual(integration_kind(old), integration_kind(new))
                self.assertEqual(migrate_formulation(new), new)
                # Material-update code is identical; identity, initialization policy and
                # explicit scope metadata can differ from unscoped legacy timed output.
                with tempfile.TemporaryDirectory() as directory:
                    base = Path(directory)
                    for label, model in [('old', old), ('new', new)]:
                        definition = base/(label+'.json')
                        definition.write_text(json.dumps(model))
                        generate(base/label, [definition])
                    def executable(label):
                        header = 'path_models.hpp' if integration_kind(old)=='path_ode' else 'models.hpp'
                        return [line for line in without_stress_scope_metadata((base/label/header).read_text()).splitlines()
                                if 'inline const char* catalogue_hash()' not in line
                                and 'inline bool explicit_initialization_required(' not in line
                                and 'inline const char* describe_models()' not in line
                                # v0.3 validates declared loading even when unused;
                                # this boundary guard is separate from material math.
                                and line != 'for (const auto& component : loading.v) if (!std::isfinite(atlas::value(component))) return false;']
                    self.assertEqual(executable('old'), executable('new'))

    def test_required_contract_and_unsupported_claims(self):
        model = migrate_formulation(load(ROOT/'models/linear-elastic.json'))
        for key in model['formulation']:
            bad = copy.deepcopy(model)
            del bad['formulation'][key]
            with self.subTest(missing=key), self.assertRaises(ValidationError):
                validate(bad)
        for key, value in [('time_dependence','physical_time'), ('equation_form','ode'),
                           ('kinematics','finite_strain_3d'), ('frame','corotational'),
                           ('objective_rate','jaumann'), ('tensor_representation','voigt'),
                           ('stress_sign','tension_positive'), ('strain_sign','tension_positive')]:
            bad = copy.deepcopy(model)
            bad['formulation'][key] = value
            with self.subTest(key=key), self.assertRaises(ValidationError):
                validate(bad)
        bad = copy.deepcopy(model)
        bad['integration'] = 'residual'
        with self.assertRaises(ValidationError):validate(bad)
        for formulation in [None, [], 'ode', {}]:
            bad = copy.deepcopy(model)
            bad['formulation'] = formulation
            with self.subTest(formulation=formulation), self.assertRaises(ValidationError):validate(bad)

    def test_migration_command_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'model.json'
            command = [sys.executable, '-m', 'atlas.cli', 'migrate-model',
                       str(ROOT/'models/linear-elastic.json'), '--output', str(output)]
            first = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(load(output)['schema_version'], '0.3')
            original = output.read_bytes()
            second = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), original)

    def test_stress_binding_and_scope(self):
        model = migrate_formulation(load(ROOT/'models/linear-elastic.json'))
        for key, value in [('name','e'), ('source','observable'), ('scope','unknown'), ('measure','kirchhoff')]:
            bad = copy.deepcopy(model)
            bad['formulation']['stress'][key] = value
            with self.subTest(key=key), self.assertRaises(ValidationError):validate(bad)
        bad = copy.deepcopy(model)
        bad['state'][0]['transient'] = True
        with self.assertRaises(ValidationError):validate(bad)
        time_model = load(ROOT/'tests/fixtures/expm/time-observable.json')
        with self.assertRaises(ValidationError):migrate_formulation(time_model)
        new = migrate_formulation(time_model, stress_scope='effective')
        for stress in [{'source':'none'}, dict(new['formulation']['stress'],name='missing')]:
            bad = copy.deepcopy(new)
            bad['formulation']['stress'] = stress
            with self.subTest(stress=stress), self.assertRaises(ValidationError):validate(bad)
        clock = migrate_formulation(load(ROOT/'tests/fixtures/time/clock.json'))
        self.assertEqual(clock['formulation']['stress'], {'source':'none'})
        with self.assertRaises(ValidationError):migrate_formulation(clock,stress_scope='total')
        self.assertEqual(interpret(clock,{'x':0},None,[0]*6,time=3)['x'], .75)

    def test_physical_equation_and_reset_boundaries(self):
        model = migrate_formulation(load(ROOT/'tests/fixtures/time/maxwell.json'), stress_scope='effective')
        for expression in ['sigma', 'sigma_n', 'de']:
            bad = copy.deepcopy(model)
            bad['equations']['sigma'] = expression
            with self.subTest(expression=expression), self.assertRaises(ValidationError):validate(bad)
        bad = copy.deepcopy(model)
        bad['increment_reset'] = {'scope':'parent_increment','updates':[]}
        with self.assertRaises(ValidationError):validate(bad)
        # The public structural schema itself rejects contradictory profiles.
        schema = json.loads((ROOT/'schemas/model-v0.3.schema.json').read_text())
        bad = copy.deepcopy(model)
        bad['formulation']['equation_form'] = 'incremental_residual'
        with self.assertRaises(ValidationError):check(bad,schema)
