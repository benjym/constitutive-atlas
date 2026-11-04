"""Dimensional and version boundaries for physical-time ODE definitions."""
import copy
import json
import math
import os
from pathlib import Path
import subprocess
import unittest
from atlas.dsl import Type, ValidationError, dimensions, infer, parse
from atlas.model import ROOT, load, validate, interpret

FIXTURES=ROOT/'tests/fixtures/time'
SOLVER=Path(os.environ.get('ATLAS_TIME_SOLVER',ROOT/'build/atlas_time_solver'))

class TemporalLanguageTests(unittest.TestCase):
    def test_rate_units_and_legacy_ambiguity_rejected(self):
        m=load(FIXTURES/'maxwell.json')
        for expression in ['sigma', 'sigma_n / tau', 'Kmod * de / tau', 'sigma / dt', 'sigma / time_n']:
            bad=copy.deepcopy(m);bad['equations']['sigma']=expression
            with self.subTest(expression=expression),self.assertRaises(ValidationError):validate(bad)
        legacy=load(ROOT/'models/linear-elastic.json')
        legacy['parameters']['tau']={'unit':'s','default':1,'min':.1,'max':10}
        with self.assertRaises(ValidationError):validate(legacy)
    def test_dimensional_serialization(self):
        # Four SI exponents: mass, length, time, temperature.
        self.assertEqual(dimensions({'si':[1,-1,-1,0]}),tuple(a+b for a,b in zip(dimensions('Pa'),dimensions('s'))))
        from fractions import Fraction
        self.assertEqual(dimensions({'si':['1/3',0,0,0]})[0],Fraction(1,3))
        self.assertEqual(infer(parse('mass ** (1/3)'),{'mass':Type(dim=(1,0,0,0))}).dim,dimensions({'si':['1/3',0,0,0]}))
        for unit in [{'si':[0,0,0,.3333333333333]}, {'si':[0,0,17,0]}, {'si':[True,0,0,0]}, {'si':[0,0,1]},'kPa']:
            with self.subTest(unit=unit),self.assertRaises(ValidationError):dimensions(unit)
        m=load(FIXTURES/'maxwell.json')
        m['parameters']['viscosity']={'unit':{'si':[1,-1,-1,0]},'default':1,'min':.1,'max':10}
        validate(m)
    def test_form_and_state_contract(self):
        m=load(FIXTURES/'clock.json')
        for change in [lambda x:x['formulation'].update(equation_form='dae'),lambda x:x.update(schema_version='0.2-draft'),lambda x:x['state'][0].update(transient=True),lambda x:x.update(integration='rate')]:
            bad=copy.deepcopy(m);change(bad)
            with self.assertRaises(ValidationError):validate(bad)
        for name in ['time','strain_rate','dt','loading','evaluation_time']:
            bad=copy.deepcopy(m);bad['parameters'][name]=bad['parameters'].pop('tau')
            with self.subTest(name=name),self.assertRaises(ValidationError):validate(bad)
    def test_interpret_requires_clock_and_ignores_previous_state(self):
        m=load(FIXTURES/'clock.json')
        with self.assertRaises(ValueError):interpret(m,{'x':0},None,[0]*6)
        result=interpret(m,{'x':0},None,[0]*6,time=3)
        self.assertEqual(result['x'],.75)

@unittest.skipUnless(SOLVER.exists(),'time-fixture solver has not been built')
class TemporalInterfaceTests(unittest.TestCase):
    def invoke(self,*args):
        r=subprocess.run([str(SOLVER),*args],capture_output=True,text=True,timeout=30)
        data=json.loads(r.stdout);self.assertEqual(data['ok'],r.returncode==0);return data
    def test_native_interpreter_rate_agreement(self):
        m=load(FIXTURES/'maxwell.json');z={'sigma':[140000,80000,80000,0,0,0]};rate=[.001,-.0005,-.0005,0,0,0]
        expected=interpret(m,z,None,rate,time=3)['sigma'].v
        data=self.invoke('--mode','evaluate-time','--model','test-maxwell','--strain-rate',','.join(map(str,rate)),'--start-time','3')
        self.assertTrue(data['ok'])
        for a,b in zip(expected,data['values']):self.assertAlmostEqual(a,b)
    def test_temporal_api_and_missing_duration(self):
        prefix=['--mode','integrate-time','--model','test-clock','--strain-rate','0,0,0,0,0,0','--start-time','3']
        self.assertFalse(self.invoke(*prefix)['ok'])
        self.assertFalse(self.invoke('--model','test-maxwell','--duration','1')['ok'])
        self.assertFalse(self.invoke(*prefix,'--duration','2','--target','.1')['ok'])
        data=self.invoke(*prefix,'--duration','2')
        self.assertTrue(data['ok']);self.assertEqual(data['schema_version'],'0.2')
        self.assertEqual(data['time'],5);self.assertAlmostEqual(data['state'][0],2)
        self.assertFalse(self.invoke('--model','test-maxwell','--mode','integrate','--strain','0,0,0,0,0,0')['ok'])
