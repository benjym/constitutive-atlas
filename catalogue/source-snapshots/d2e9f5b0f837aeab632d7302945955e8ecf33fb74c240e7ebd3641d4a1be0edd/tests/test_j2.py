"""Independent analytical J2 identities and declarative-residual checks."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.model import load, interpret
from atlas.initialization import initialize_state
from tools.study_j2 import BASE, P, ZERO, cases, oracle, tangent, assess_rows

class J2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=load(ROOT/'models/research/j2/j2-linear-isotropic-hardening-be.json')

    def test_all_reference_residuals(self):
        for c in cases():
            if not c['ok']:continue
            z=list(map(float,c['args'][2].split(',')));de=list(map(float,c['args'][3].split(',')))
            p=list(map(float,c['args'][1].split(',')));x=c['expected']
            state=lambda a:dict(sigma=a[:6],alpha=a[6],gamma=a[7])
            r=interpret(self.model,state(x),state(z),de,dict(zip(self.model['parameters'],p)))
            self.assertLess(max(abs(v) for v in r['sigma'].v),1e-7,c['id'])
            self.assertLess(abs(r['alpha']),1e-14,c['id'])
            self.assertLess(abs(r['gamma']),1e-12,c['id'])

    def test_closed_form_uniaxial_strain(self):
        e=.01;_,K,G,sy,H=P;qtrial=2*G*e;g=(qtrial-sy)/(3*G+H)
        z=oracle(ZERO,[e,0,0,0,0,0],P)
        self.assertAlmostEqual(z[6],g,places=15)
        self.assertAlmostEqual(z[0],K*e+4*G*e/3-2*G*g,places=8)

    def test_tangent_directional_differences(self):
        for de in ([.0001,-.00005,-.00005,.00003,0,0],[.003,-.001,-.002,.001,-.002,.001]):
            t=tangent(ZERO,de,P)
            for j in range(6):
                h=1e-7;a=list(de);b=list(de);a[j]+=h;b[j]-=h
                x=oracle(ZERO,a,P);y=oracle(ZERO,b,P)
                for i in range(8):
                    self.assertLess(abs((x[i]-y[i])/(2*h)-t[i][j]),.05 if i<6 else 1e-8)

    def test_initialization_rejects_missing_overstress_and_negative_history(self):
        p=dict(zip(self.model['parameters'],P))
        good=dict(sigma=[0]*6,alpha=0)
        result=initialize_state(self.model,good,p)
        self.assertEqual(result['initial'],ZERO)
        for bad in (dict(sigma=[0]*6),dict(sigma=[0]*6,alpha=-.01),
                    dict(sigma=[1e6,-5e5,-5e5,0,0,0],alpha=0)):
            with self.assertRaises((ValueError,AssertionError)):
                initialize_state(self.model,bad,p)

    def test_frozen_references_match_prospective_generator(self):
        self.assertEqual(json.loads((BASE/'references.json').read_text())['cases'],cases())

    def test_assessor_rejects_corrupted_output(self):
        path=BASE/'native-raw.json'
        if not path.exists():return  # source-only phase; final run has raw evidence
        cs=json.loads((BASE/'references.json').read_text())['cases'];rows=json.loads(path.read_text())
        assess_rows(cs,rows)
        for mutation in ('stress','history','success','tangent'):
            bad=copy.deepcopy(rows)
            idx=next(i for i,c in enumerate(cs) if 'tangent' in c) if mutation=='tangent' else 0
            d=json.loads(bad[idx]['calls'][0]['stdout'])
            if mutation=='stress':d['state'][0]+=1
            elif mutation=='history':d['state'][6]+=.01
            elif mutation=='success':d['ok']=False
            else:d['state_tangent'][0][0]+=10
            bad[idx]['calls'][0]['stdout']=json.dumps(d)
            with self.assertRaises(AssertionError):assess_rows(cs,bad)

if __name__=='__main__':unittest.main()
