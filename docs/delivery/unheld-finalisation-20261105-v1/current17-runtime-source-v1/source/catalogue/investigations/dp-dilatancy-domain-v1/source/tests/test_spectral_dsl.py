"""Spectral expression typing and checked routing; compiled contexts are separate."""
import copy
import gzip
import json
import math
from pathlib import Path
from decimal import Decimal, localcontext
import tempfile
import unittest

from atlas.dsl import (I, PRESSURE, ZERO, Sym, Type, ValidationError, cpp,
                       evaluate, infer, parse)
from atlas.compiler import generate
from atlas.history import _tree, validate_program
from atlas.history_compiler import _expression, generate as history_header
from atlas.initialization import validate_recipe
from atlas.model import ROOT, load, validate
from atlas.symmetric_spectral import SPECTRAL_FUNCTIONS, spectral


class SpectralDsl(unittest.TestCase):
    def setUp(self):
        self.symbols = {'A': Type('sym', PRESSURE), 'B': Type('sym'),
                        'p': Type(dim=PRESSURE), 'v': Type(value_only=True), 'x': Type()}

    def inferred(self, expr):
        return infer(parse(expr), self.symbols)

    def test_shape_units_and_arity(self):
        for name, (_, shape, value_only) in SPECTRAL_FUNCTIONS.items():
            with self.subTest(operation=name):
                self.assertEqual(self.inferred(name+'(A)'),
                                 Type(shape, ZERO if shape == 'sym' else PRESSURE, value_only))
                for expr in (name+'(p)', name+'()', name+'(A,A)', name+'(x=1)'):
                    with self.assertRaises(ValidationError): self.inferred(expr)

    def test_qualifier_cannot_be_laundered_through_numeric_operations(self):
        expressions = ['v+x', 'x-v', 'v*x', 'x/v', 'v**x', 'x**v', 'sqrt(v)',
                       'exp(v)', 'log(v)', 'log1p(v)', 'sin(v)', 'cos(v)', 'abs(v)',
                       'min(x,v)', 'max(v,x)', 'trace(v*B)', 'norm(v*B)',
                       'dot(B,v*B)', 'cube_trace(v*B)', 'determinant(v*B)',
                       'normalized_determinant(v*B)', 'trace(expm(v*B))',
                       'trace(tensor_square(v*B))', 'trace(dev(v*B))',
                       'trace(sym(v,x,x,x,x,x))', 'principal_max(v*B)',
                       'trace(projector_max(v*B))', 'select(x>0,v,x)', 'select(v>0,x,v)']
        for expr in expressions:
            with self.subTest(expr=expr): self.assertTrue(self.inferred(expr).value_only)
        for expr in ('v>x', 'select(v>x,x,0)', 'select(principal_max_value(A)>p,A,p*B)'):
            with self.subTest(expr=expr): self.assertFalse(self.inferred(expr).value_only)
        for expr in ('(v>0)*1', '1+(v>0)', '-(v>0)', '(v>0)**2', '2**(v>0)', 'min(x,v>0)'):
            with self.subTest(expr=expr), self.assertRaises(ValidationError): self.inferred(expr)

    def test_model_numeric_sink_and_consumed_reset_guard(self):
        base = load(ROOT/'models/linear-elastic.json')
        for expr in ('principal_max_value(sigma)*I',
                     'select(1>0,sigma,principal_max_value(sigma)*I)'):
            model = copy.deepcopy(base); model['equations']['sigma'] = expr
            with self.subTest(expr=expr), self.assertRaises(ValidationError): validate(model)
        model = copy.deepcopy(base)
        model['derived'] += [{'name':'query','expr':'principal_max_value(sigma)'},
                             {'name':'decision','expr':'select(query>0*p_ref,p_ref,-p_ref)'}]
        model['increment_reset'] = {'scope':'parent_increment', 'updates':[
            {'target':'sigma', 'guard':'decision', 'value':'sigma'}]}
        with self.assertRaises(ValidationError): validate(model)
        model['increment_reset']['updates'][0]['guard'] = 'principal_max(sigma)'
        validate(model)
        model['equations']['sigma'] = 'select(query>0*p_ref,sigma,sigma)'
        validate(model)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'model.json'; path.write_text(json.dumps(model))
            generate(Path(tmp)/'generated', [path])
            header = (Path(tmp)/'generated/models.hpp').read_text()
            self.assertIn('#include "atlas/checked_spectral.hpp"', header)
            self.assertIn('atlas::spectral_scalar_or_mark(', header)

    def test_history_event_policy_differs_from_boolean_checks(self):
        symbols = {'A':Type('sym', PRESSURE), 'p':Type(dim=PRESSURE)}
        _tree('principal_max_value(A)>p', symbols, Type('bool'))
        with self.assertRaises(ValidationError): _tree('principal_max_value(A)', symbols, Type(dim=PRESSURE))
        program = json.loads((ROOT/'fixtures/history/ordered-copy.json').read_text())
        phase = program['phases'][0]
        phase['bindings']['tensor'] = {'snapshot':'parent', 'field':'stress'}
        phase['guard'] = 'select(principal_max_value(tensor)>0*trace(tensor),1,-1)'
        with self.assertRaises(ValidationError): validate_program(program)
        phase['guard'] = 'select(principal_max(tensor)>0*trace(tensor),1,-1)'
        validate_program(program)
        header = history_header([program])
        self.assertIn('#include "atlas/checked_spectral.hpp"', header)
        self.assertIn('atlas::spectral_candidate::scalar_checked(', header)

    def test_initialization_numeric_sinks_and_predicate(self):
        model = load(ROOT/'models/research/terracotta-2024-fig1.json')
        recipe = json.loads((ROOT/'initialization/terracotta-2024-fig1-total-stress.json').read_text())
        validate_recipe(recipe, model)
        for kind in ('term', 'state', 'rate'):
            item = copy.deepcopy(recipe)
            if kind == 'term': item['terms'][0]['expr'] = 'principal_max_value(pInput*I)'
            elif kind == 'state': item['state']['ev_e'] = 'principal_max_value(phiInput*I)'
            else: item['initial_strain_rate'] = 'principal_max_value(DvInput*I)*I'
            with self.subTest(kind=kind), self.assertRaises(ValidationError): validate_recipe(item, model)
        recipe['terms'][0]['requires'] = ['principal_max_value(pInput*I)>0*pInput']
        validate_recipe(recipe, model)

    def test_lazy_selected_failure_eager_mask_and_recovery(self):
        env = {'B':Sym((1.,1.,1.,0.,0.,0.))}
        for expr in ('principal_max(B)', 'trace(projector_max(B))',
                     '0*principal_max(B)', 'select(principal_max(B)>0,1,2)'):
            with self.subTest(expr=expr), self.assertRaises(ValidationError): evaluate(parse(expr), env)
        self.assertEqual(evaluate(parse('select(principal_max_value(B)>0,3,principal_max(B))'), env), 3)
        self.assertEqual(evaluate(parse('principal_mid_value(B)'), env), 1)
        expr = parse('select(principal_max_value(B)>0,projector_max(B),I)')
        self.assertIn('atlas::spectral_projector_or_mark(', cpp(expr))
        self.assertIn('atlas::spectral_candidate::projector_checked(', _expression(expr, {'B':'input_B'}))

    def test_frozen_independent_primal_references(self):
        here = ROOT/'catalogue/investigations/symmetric-spectral-primitive-v1'
        references = json.loads(gzip.decompress((here/'reference/reference-p360.json.gz').read_bytes()))
        requests = json.loads(gzip.decompress((here/'requests.json.gz').read_bytes()))
        cases = {case['input']['id']:case['reference'] for case in references['cases']}
        with localcontext() as ctx:
            ctx.prec = 500
            eps = Decimal(2)**-52
            tiny = 2*Decimal.from_float(math.ulp(0.))
            for request in requests:
                if request['kind'] != 'double': continue
                with self.subTest(case=request['id']):
                    values = [float.fromhex(x) for x in request['values']]
                    op = request['operation']
                    if request['expected_status'] != 'ok':
                        with self.assertRaisesRegex(ValueError, '^'+request['expected_status']+'$'): spectral(values, op)
                        continue
                    observed = spectral(values, op); ref = cases[request['case']]
                    eigen = list(map(Decimal, ref['eigenvalues']))
                    norm = sum(Decimal.from_float(x)**2 for x in values).sqrt()
                    if op.startswith('projector_'):
                        i = 0 if op == 'projector_max' else 2
                        name = 'max' if i == 0 else 'min'
                        p = [[Decimal(x) for x in row] for row in ref['selected'][name]['projector']]
                        rt2 = Decimal(2).sqrt()
                        target = [p[0][0],p[1][1],p[2][2],rt2*p[0][1],rt2*p[1][2],rt2*p[0][2]]
                        error = sum((Decimal.from_float(x)-y)**2 for x,y in zip(observed,target)).sqrt()
                        gap = min(abs(eigen[i]-eigen[j]) for j in range(3) if j != i)
                        bound = 2048*eps*norm/gap+tiny
                    else:
                        if op in ('upper_sum', 'lower_sum'):
                            target = Decimal(ref['pair_sums']['upper' if op == 'upper_sum' else 'lower']['value'])
                        else: target = eigen[0 if op in ('max','max_value') else 1 if op in ('mid','mid_value') else 2]
                        error = abs(Decimal.from_float(observed)-target); bound = 512*eps*norm+tiny
                        if (ref['method'].startswith('diagonal') or ref['method'] == 'zero') and op not in ('upper_sum','lower_sum'):
                            self.assertEqual(observed, float(target))
                    self.assertLessEqual(error, bound)
