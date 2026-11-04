"""Shared compiled history vs Python: arithmetic only, no model admission claims."""
import copy
import json
import math
import os
import subprocess
import unittest

from atlas.dsl import ValidationError
from atlas.history import _hash, make_snapshot, advance
from atlas.history_compiler import generate
from atlas.model import ROOT
from tools.history_cases import cases


class HistoryCompilerTests(unittest.TestCase):
    def test_validates_before_generation_and_preserves_source(self):
        p = json.loads((ROOT/'fixtures/history/ordered-copy.json').read_text())
        original = copy.deepcopy(p)
        header = generate([p])
        self.assertIn(_hash(p), header)
        self.assertEqual(p, original)
        p['phases'][-1]['base'] = 'parent'
        with self.assertRaises(ValidationError):
            generate([p])
        # Canonical program identity must imply one positional layout regardless
        # of JSON object insertion order.
        reordered = copy.deepcopy(original)
        for key in ['fields', 'inputs']:
            reordered[key] = dict(reversed(list(reordered[key].items())))
        self.assertEqual(_hash(original), _hash(reordered))
        # Metadata preserves original JSON spelling, but executable code/layout match.
        self.assertEqual(generate([original]).split('inline const char* description')[0],
                         generate([reordered]).split('inline const char* description')[0])
        with self.assertRaises(ValueError):
            generate([])
        with self.assertRaises(ValueError):
            generate([original, original])

    def test_boolean_arithmetic_rejected_before_native_compilation(self):
        for expression in ['-(1 > 0)', '(1 > 0)+(1 > 0)',
                           'select(1 > 0, 1 > 0, -(1 > 0))']:
            p = json.loads((ROOT/'fixtures/history/ordered-copy.json').read_text())
            p['phases'][-1]['checks'] = [expression]
            with self.subTest(expression=expression), self.assertRaises(ValidationError):
                generate([p])

    def test_binary64_integer_policy_prevents_silent_restart_rounding(self):
        p = json.loads((ROOT/'fixtures/history/validation-probe.json').read_text())
        with self.assertRaises(ValidationError):
            make_snapshot(p, {'x': 9007199254740993})
        parent = make_snapshot(p, {'x': 1})
        with self.assertRaises(ValidationError):
            advance(p, parent, {'gate': 0, 'value': 9007199254740993})
        p['phases'][0]['writes']['x'] = '9007199254740993'
        with self.assertRaises(ValidationError):
            generate([p])
        # Exactly representable large finite integers remain valid numeric values.
        self.assertEqual(make_snapshot(p | {'phases': [dict(p['phases'][0], writes={'x':'value'})]},
                                       {'x': 2**100})['values']['x'], 2**100)


class HistoryRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.solver = os.environ.get('ATLAS_HISTORY_SOLVER', str(ROOT/'build/atlas_history_solver'))
        if not os.path.isfile(cls.solver):
            if 'ATLAS_HISTORY_SOLVER' in os.environ:
                raise AssertionError('requested history runtime does not exist')
            raise unittest.SkipTest('build atlas_history_solver to exercise shared history runtime')

    def invoke(self, wire):
        args = [self.solver]
        for key, value in zip(['--program','--hash','--state','--inputs','--generation','--epoch'], wire):
            args.extend([key, value])
        return subprocess.run(args, capture_output=True, text=True, timeout=10)

    def test_compiled_descriptor_pins_exact_program_and_layout(self):
        result = subprocess.run([self.solver, '--describe'], capture_output=True, text=True, check=True, timeout=10)
        actual = json.loads(result.stdout)
        paths = sorted((ROOT/'fixtures/history').glob('*.json'))
        self.assertEqual(len(actual), len(paths))
        for item, path in zip(actual, paths):
            program = json.loads(path.read_text())
            self.assertEqual(item['program'], program)
            self.assertEqual(item['program_sha256'], _hash(program))
            self.assertEqual(item['id'], program['id'])
            self.assertEqual(item['state_order'], sorted(program['fields']))
            self.assertEqual(item['input_order'], sorted(program['inputs']))
            for key, declaration in [('state_size','fields'), ('input_size','inputs')]:
                self.assertEqual(item[key], sum(6 if f['shape']=='sym' else 1 for f in program[declaration].values()))

    def test_python_parity_and_transactional_rollback(self):
        for case in cases():
            with self.subTest(case=case['label']):
                result = self.invoke(case['wire'])
                self.assertEqual(result.returncode, 0, result.stderr)
                actual = json.loads(result.stdout)
                self.assertIsInstance(actual.pop('message'), str)
                expected = case['expected']
                actual_values, expected_values = actual.pop('values'), expected['values']
                self.assertEqual(actual, {k:v for k,v in expected.items() if k!='values'})
                for a,b in zip(actual_values, expected_values, strict=True):
                    self.assertTrue(math.isclose(a,b,rel_tol=2e-14,abs_tol=1e-300), (a,b))
                # Trial failures preserve every parent slot and both counters exactly.
                if not actual['ok']:
                    self.assertEqual(actual_values, list(map(float,case['wire'][2].split(','))))
                    self.assertEqual(actual['events'], [])
                    self.assertEqual(actual['generation'], int(case['wire'][4]))
                    self.assertEqual(actual['preparation_epoch'], int(case['wire'][5]))

    def test_repeated_candidate_is_pure(self):
        case = cases()[1]
        self.assertEqual(self.invoke(case['wire']).stdout, self.invoke(case['wire']).stdout)

    def test_rejects_malformed_wire_before_trial(self):
        wire = cases()[0]['wire']
        for slot, value in [(0,'unknown'),(1,'0'*64),(2,'nan'),(2,wire[2]+',0'),
                            (3,'inf'),(3,''),(4,'-1'),(4,'1.0'),(4,'01'),
                            (4,'9007199254740992'),(5,'true')]:
            with self.subTest(slot=slot,value=value):
                bad = wire.copy(); bad[slot] = value
                result = self.invoke(bad)
                self.assertEqual(result.returncode, 2)
                actual = json.loads(result.stdout)
                self.assertFalse(actual['valid']); self.assertFalse(actual['ok'])
                self.assertNotIn('values', actual)
        bad = wire.copy()
        # guarded-probe parent mode is first scalar; invalid parents cannot be trial results.
        bad = cases()[8]['wire'].copy(); parts=bad[2].split(',');parts[0]='2';bad[2]=','.join(parts)
        self.assertFalse(json.loads(self.invoke(bad).stdout)['valid'])


if __name__ == '__main__':
    unittest.main()
