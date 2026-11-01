"""Exact multiplicity controls and lazy numeric extrema, without compiled execution."""
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

from atlas.dsl import Sym, Type, PRESSURE, ValidationError, cpp, evaluate, infer, parse
from atlas.model import load, validate
from atlas.compiler import generate
from atlas.history import _tree, validate_program
from atlas.history_compiler import _expression
from atlas.numerics.spectral_multiplicity import repeated_extremes

ROOT = Path(__file__).resolve().parents[1]


def extreme_expression(maximum=True, name='sigma'):
    side, pair = ('max', 'upper') if maximum else ('min', 'lower')
    return (f'select(principal_range_le({name},0*p_ref),trace({name}/3),'
            f'select(principal_{side}_repeated({name}),principal_{pair}_sum({name})/2,'
            f'principal_{side}({name})))')


class SpectralMultiplicity(unittest.TestCase):
    def test_exact_known_eigensystems_and_scaling(self):
        fixtures = [([0.,0.,0.,0.,0.,0.], (True,True)),
                    ([3.,3.,3.,0.,0.,0.], (True,True)),
                    ([3.,3.,1.,0.,0.,0.], (True,False)),
                    ([3.,1.,1.,0.,0.,0.], (False,True)),
                    ([3.,2.,1.,0.,0.,0.], (False,False)),
                    ([0.,0.,0.,1.,1.,1.], (False,True)),
                    ([0.,0.,0.,-1.,-1.,-1.], (True,False))]
        for x, target in fixtures:
            for exponent in (-1074,-500,0,500,1021):
                scaled = [math.ldexp(v,exponent) for v in x]
                with self.subTest(x=x, exponent=exponent):
                    self.assertEqual(repeated_extremes(scaled),target)
        for sign in (-1.,1.):
            x=[1.,1.,1.,0.,0.,0.]
            x[0]=math.nextafter(1., math.inf if sign>0 else -math.inf)
            self.assertEqual(repeated_extremes(x), (False,True) if sign>0 else (True,False))
        # A third distinct one-ULP diagonal value is not silently clustered.
        self.assertEqual(repeated_extremes([math.nextafter(1.,math.inf),1.,math.nextafter(1.,0.),0.,0.,0.]),(False,False))

    def test_shape_units_arity_and_event_dependency(self):
        for side in ('max','min'):
            name=f'principal_{side}_repeated'
            self.assertEqual(infer(parse(name+'(A)'),{'A':Type('sym',PRESSURE)}),Type('bool'))
            for expr in (name+'(1)',name+'()',name+'(A,A)',name+'(x=1)'):
                with self.subTest(expr=expr), self.assertRaises(ValidationError):
                    infer(parse(expr),{'A':Type('sym',PRESSURE)})
            with self.assertRaises(ValidationError):
                infer(parse(name+'(A)*1'),{'A':Type('sym',PRESSURE)})
        program=json.loads((ROOT/'fixtures/history/ordered-copy.json').read_text())
        program['phases'][0]['bindings']['tensor']={'snapshot':'parent','field':'stress'}
        program['phases'][0]['guard']='select(principal_max_repeated(tensor),1,-1)'
        with self.assertRaises(ValidationError): validate_program(program)
        _tree('principal_min_repeated(A)',{'A':Type('sym',PRESSURE)},Type('bool'))

    def test_lazy_composite_and_unchanged_near_gap_failure(self):
        for x, bounds in [([1.,1.,1.,0.,0.,0.],(1.,1.)),
                          ([3.,1.,1.,0.,0.,0.],(3.,1.)),
                          ([3.,3.,1.,0.,0.,0.],(3.,1.)),
                          ([3.,2.,1.,0.,0.,0.],(3.,1.)),
                          ([0.,0.,0.,1.,1.,1.],(math.sqrt(2),-1/math.sqrt(2)))]:
            for maximum,target in zip((True,False),bounds):
                got=evaluate(parse(extreme_expression(maximum)),{'sigma':Sym(x),'p_ref':1.})
                self.assertAlmostEqual(got,target,places=14)
        x=[math.nextafter(1.,math.inf),1.,math.nextafter(1.,0.),0.,0.,0.]
        with self.assertRaisesRegex(ValidationError,'selected_eigenvalue_unresolved'):
            evaluate(parse(extreme_expression()),{'sigma':Sym(x),'p_ref':1.})
        with self.assertRaises(ValidationError):
            evaluate(parse('principal_max(sigma)'),{'sigma':Sym([1.,1.,1.,0.,0.,0.])})

    def test_generated_routing_and_reset_rejection(self):
        model=copy.deepcopy(load(ROOT/'models/linear-elastic.json'))
        model['equations']['sigma']='sigma-'+extreme_expression()+'*I'
        validate(model)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'probe.json';p.write_text(json.dumps(model))
            generate(Path(tmp)/'generated',[p])
            header=(Path(tmp)/'generated/models.hpp').read_text()
            self.assertIn('#include "atlas/checked_spectral_multiplicity.hpp"',header)
        model['increment_reset']={'scope':'parent_increment','updates':[
            {'target':'sigma','guard':'select(principal_max_repeated(sigma),p_ref,-p_ref)','value':'sigma'}]}
        with self.assertRaises(ValidationError):validate(model)
        self.assertIn('principal_max_repeated_or_mark',cpp(parse('principal_max_repeated(sigma)')))
        self.assertIn('spectral_multiplicity_accuracy::checked',_expression(parse('principal_min_repeated(A)'),{'A':'input_A'}))

    def test_nonfinite_and_wrong_shape_reject(self):
        for x in ([1.,2.], [True,1.,1.,0.,0.,0.], [math.inf,1.,1.,0.,0.,0.], [math.nan,1.,1.,0.,0.,0.]):
            with self.assertRaises(ValueError):repeated_extremes(x)


if __name__=='__main__':unittest.main()
