"""Flattened GIS research definition and coupled numerical rate checks."""
import copy,json,math,os
from pathlib import Path
import unittest
from atlas.dsl import Sym,ValidationError
from atlas.model import ROOT,load,interpret
from tools.gis2024_rate_study import MODEL_PATH,REFERENCE_PATH,make_request,assess
from tools.clay2013_integration_study import native_call
from tools.reference_gis2024_coupled import coupled_rates as oracle,ReferenceDomainError
from tools.inspect_gis2024_coupled import coupled_rates as typed

SOLVER=Path(os.environ.get('ATLAS_GIS2024_SOLVER',ROOT/'build/atlas_gis2024_solver'))
class GISDefinition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.model=load(MODEL_PATH);cls.cases=json.loads(REFERENCE_PATH.read_text())['cases']
    def test_flattened14_rates_against_independent_cartesian(self):
        for c in self.cases:
            state=c['state']|dict(sigma=Sym(tuple(c['state']['sigma'])),h=Sym(tuple(c['state']['h'])))
            r=interpret(self.model,c['state'],c['state'],c['de'],c['parameters']|dict(p_scale=1e5))
            flat=list(r['sigma'].v)+[r['e']]+list(r['h'].v)+[r['Omega']]
            target=oracle(c['state'],c['de'],c['parameters'])['derivative']
            for i,(x,y) in enumerate(zip(flat,target,strict=True)):
                self.assertAlmostEqual(x,y,delta=max(1e-8,abs(y)*2e-10) if i<6 else 1e-14)
    def test_positive_suppression_underflow_rejected_without_clamping(self):
        c=self.cases[0];p=c['parameters']|dict(gamma_chi=100.)
        s=c['state']|dict(sigma=Sym(tuple(c['state']['sigma'])),h=Sym(tuple(c['state']['h'])))
        with self.assertRaises(ReferenceDomainError):oracle(c['state'],c['de'],p)
        with self.assertRaises(ValidationError):typed(s,Sym(tuple(c['de'])),p)
        with self.assertRaises((ValidationError,ValueError)):interpret(self.model,c['state'],c['state'],c['de'],p|dict(p_scale=1e5))
        result=interpret(self.model,c['state'],c['state'],[0.]*6,p|dict(p_scale=1e5))
        self.assertEqual(list(result['sigma'].v)+[result['e']]+list(result['h'].v)+[result['Omega']],[0.]*14)
    def test_strict_memory_radius_without_projection(self):
        c=copy.deepcopy(self.cases[0]);R=c['parameters']['R']
        for radial,accepted in [(math.nextafter(R,0.),True),(R,True),(math.nextafter(R,math.inf),False),(R*(1+8*math.ulp(1.)),False)]:
            c['state']['h']=[radial,0.,0.,0.,0.,0.];c['state']['Omega']=0.
            st=c['state']|dict(sigma=Sym(tuple(c['state']['sigma'])),h=Sym(tuple(c['state']['h'])))
            calls=[lambda:oracle(c['state'],c['de'],c['parameters']),lambda:typed(st,Sym(tuple(c['de'])),c['parameters']),lambda:interpret(self.model,c['state'],c['state'],c['de'],c['parameters']|dict(p_scale=1e5))]
            for call in calls:
                if accepted:call()
                else:
                    with self.assertRaises((ValueError,ValidationError)):call()

    def test_state_units_explicit_parameters_and_isolation(self):
        self.assertEqual([f['name'] for f in self.model['state']],['sigma','e','h','Omega'])
        self.assertEqual(len(self.model['parameters']),19)
        self.assertEqual(self.model['status'],'draft')
        self.assertEqual(self.model['integration'],'rate')
        for folder in (ROOT/'models',ROOT/'models/research'):
            self.assertNotIn(self.model['id'],[load(p)['id'] for p in folder.glob('*.json')])

@unittest.skipUnless(SOLVER.is_file(),'isolated GIS solver not built')
class NativeGIS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.model=load(MODEL_PATH);cls.cases=json.loads(REFERENCE_PATH.read_text())["cases"]
    def test_native14_rates_and_underflow_domain(self):
        records=[]
        for case in self.cases:
            r=make_request(case,self.model);records.append(dict(case=case['id'],request=r,response=native_call(SOLVER,r,mode='evaluate')))
        assess(records,self.model,self.cases)
        c=copy.deepcopy(self.cases[0]);c['parameters']['gamma_chi']=100.
        self.assertFalse(native_call(SOLVER,make_request(c,self.model),mode='evaluate')['ok'])
        c['de']=[0.]*6
        zero=native_call(SOLVER,make_request(c,self.model),mode='evaluate')
        self.assertTrue(zero['ok']);self.assertEqual(zero['values'],[0.]*14)
        c=copy.deepcopy(self.cases[0]);R=c['parameters']['R']
        for radius,accepted in [(R,True),(math.nextafter(R,math.inf),False)]:
            c['state']['h']=[radius,0.,0.,0.,0.,0.];c['state']['Omega']=0.
            self.assertIs(native_call(SOLVER,make_request(c,self.model),mode='evaluate')['ok'],accepted)


if __name__=='__main__':unittest.main()
