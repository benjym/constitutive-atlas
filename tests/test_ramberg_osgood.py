"""Source oracle, explicit preparation and exact prospective requests; no builds."""
import copy
import json
import math
import unittest
from atlas.dsl import ValidationError
from atlas.initialization import initialize_state
from atlas.model import ROOT, defaults, load, validate
from tools.check_ramberg_osgood import make_requests, rotate, strain_from_stress, stress_oracle

class RambergOsgoodTests(unittest.TestCase):
    def setUp(self):
        self.model=load(ROOT/'models/ramberg-osgood-ansys242.json')
        self.p=defaults(self.model)

    def test_schema_and_consistent_nonzero_initialization(self):
        validate(self.model)
        for n in (1.5,2.5,5,8):
            p=dict(self.p,n=n)
            for s in ([0]*6,[100000]*3+[0]*3,[120000,30000,-20000,5000,-8000,6000]):
                e=strain_from_stress(s,p)
                result=initialize_state(self.model,{'sigma':s,'epsilon':e},p)
                self.assertEqual(result['initial'],s+e)
                oracle=stress_oracle(e,p)
                for a,b in zip(s,oracle):self.assertAlmostEqual(a,b,delta=1e-8)

    def test_inconsistent_state_and_excluded_parameters_reject(self):
        with self.assertRaises(ValidationError):initialize_state(self.model,{'sigma':[100000]*3+[0]*3,'epsilon':[0]*6},self.p)
        for key,value in [('alpha',0),('n',1),('nu',.5),('E',-1)]:
            with self.subTest(key=key),self.assertRaises(ValidationError):initialize_state(self.model,{'sigma':[0]*6,'epsilon':[0]*6},dict(self.p,**{key:value}))
        with self.assertRaises(ValidationError):initialize_state(self.model,{'sigma':[0]*6},self.p)

    def test_source_closed_uniaxial_offset_and_hydrostatic(self):
        p=self.p;s=p['sigma0'];e=strain_from_stress([s,0,0,0,0,0],p)
        self.assertAlmostEqual(e[0],(1+p['alpha'])*s/p['E'])
        self.assertAlmostEqual(sum(e[:3]),(1-2*p['nu'])*s/p['E'])
        for v in [-.002,0,.002]:
            out=stress_oracle([v,v,v,0,0,0],p)
            self.assertAlmostEqual(out[0],p['E']*v/(1-2*p['nu']))
            self.assertEqual(out[3:],[0,0,0])

    def test_oracle_covariance_units_and_reversal(self):
        e=[.003,-.001,.0005,.0004,-.0002,.0006];s=stress_oracle(e,self.p)
        rotated=stress_oracle(rotate(e),self.p)
        scaled=stress_oracle(e,dict(self.p,E=self.p['E']*1000,sigma0=self.p['sigma0']*1000))
        reversed_s=stress_oracle([-v for v in e],self.p)
        for a,b in zip(rotated,rotate(s)):self.assertAlmostEqual(a,b,delta=1e-8)
        for a,b in zip(scaled,s):self.assertAlmostEqual(a/1000,b,delta=1e-8)
        for a,b in zip(reversed_s,s):self.assertAlmostEqual(a,-b,delta=1e-8)

    def test_frozen_requests_are_reproducible(self):
        frozen=json.loads((ROOT/'docs/ingestion/ramberg-osgood-ansys242/execution-v1/requests.json').read_text())
        self.assertEqual(frozen,make_requests())
        self.assertEqual(len({c['id'] for c in frozen['cases']}),len(frozen['cases']))
        self.assertTrue(any(c.get('require_rollback') for c in frozen['cases']))
        self.assertEqual(frozen['parameter_order'],list(self.model['parameters']))

if __name__=='__main__':unittest.main()
