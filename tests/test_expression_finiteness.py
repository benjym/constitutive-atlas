"""Current interpreter versus independently specified executed-node witnesses."""
import json
import math
import struct
import unittest
from pathlib import Path
from atlas.dsl import Sym, ValidationError, evaluate, parse
from atlas.evidence import checked_receipt
ROOT = Path(__file__).resolve().parents[1]

class ExpressionFiniteness(unittest.TestCase):
    def test_independent_contract_corpus(self):
        rows = json.loads((ROOT / 'docs/reviews/expression-finiteness-audit-v1/checks.json').read_text())['rows']
        self.assertEqual(len(rows), 31)
        env = {'h': 1e308, 't': 1e-308, 'z': 0.,
               'a': Sym((1e308, -1e308, 0., 0., 0., 0.)),
               'bad': Sym((1., 2., 3., 0., math.inf, 0.)),
               'nan': math.nan, 'inf': math.inf,
               'sub': float.fromhex('0x0.0000000000001p-1022')}
        for row in rows:
            with self.subTest(case=row['id']):
                if row['expected_accepted']:
                    evaluate(parse(row['expression']), env)
                else:
                    with self.assertRaises((ValidationError, ArithmeticError, ValueError)):
                        evaluate(parse(row['expression']), env)
                    # Rejection must not leave interpreter state poisoned.
                    self.assertEqual(evaluate(parse('select(1>0,7,h*h)'), env), 7.)
        self.assertEqual(struct.pack('>d', evaluate(parse('-z'), env)).hex(), '8000000000000000')
        self.assertEqual(evaluate(parse('sub'), env), env['sub'])
        self.assertEqual(evaluate(parse('t*t'), env), 0.)
        self.assertIs(evaluate(parse('1<2'), env), True)
        self.assertEqual(evaluate(parse('sym(1,2,3,4,5,6)'), env).v, (1.,2.,3.,4.,5.,6.))

    def test_every_tensor_component_and_malformed_name(self):
        for component in range(6):
            for value in (math.nan, math.inf, -math.inf, True, None, 1j):
                v = [1.] * 6
                v[component] = value
                for expr in ('A', 'select(trace(A)>0,1,2)', '0*A'):
                    with self.subTest(component=component, value=repr(value), expr=expr):
                        with self.assertRaises(ValidationError):
                            evaluate(parse(expr), {'A': Sym(tuple(v))})
        values = [Sym((1.,2.,3.)), Sym(tuple(range(7))), 10**10000, 1j, '1', None]
        for value in values:
            with self.assertRaises(ValidationError):
                evaluate(parse('x'), {'x': value})

    def test_v2_original_source_bindings(self):
        data = json.loads((ROOT / 'catalogue/source-replays/dsl-identity-v2/inventory.json').read_text())
        self.assertEqual(len(data['references']), 12)
        for row in data['references'] + data['secondary_source_map_references']:
            with self.subTest(document=row['document'], source=row['original_path']):
                self.assertEqual(checked_receipt(ROOT, row['document'], row['original_path'], row['sha256']),
                                 (ROOT / row['archived_path']).resolve())
