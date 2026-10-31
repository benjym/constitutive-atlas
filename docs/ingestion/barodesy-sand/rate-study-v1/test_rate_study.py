import copy
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from atlas.model import load
from atlas.compiler import generate
import check
import reference

HERE=Path(__file__).resolve().parent


def rotate(v,q):
    x,y,z,u,v,w=v;r=math.sqrt(2)
    a=[[x,u/r,w/r],[u/r,y,v/r],[w/r,v/r,z]]
    b=[[math.fsum(q[i][k]*a[k][l]*q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    return [b[0][0],b[1][1],b[2][2],r*b[0][1],r*b[1][2],r*b[0][2]]


class RateStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=reference.read_inputs()
        cls.cases={c['id']:c for c in cls.inputs['valid']}
        cls.ref=reference.build_reference(cls.inputs)
        cls.expected={c['id']:c for c in cls.ref['records']}

    def test_reference_complete_fresh_precision_replay(self):
        self.assertEqual(check.checked_reference(),self.ref)
        self.assertEqual(len(self.ref['records']),37)
        self.assertEqual(len(self.ref['invalid']),19)
        for c in self.ref['records']:
            with localcontext() as ctx:
                ctx.prec=140
                for x,y in zip(c['oracle80']['decimal_values'],c['oracle120']['decimal_values']):
                    self.assertLessEqual(abs(Decimal(x)-Decimal(y)),Decimal('1e-55')*max(1,abs(Decimal(y))))

    def test_typed_model_seven_states_existing_cpp_generation_only(self):
        m=load(HERE/'model-draft.json')
        self.assertEqual(m['status'],'draft')
        self.assertEqual([f['name']for f in m['state']],['sigma','e'])
        self.assertEqual(list(m['parameters']),list(reference.ORDER))
        self.assertEqual(sum(6 if f['shape']=='sym'else 1 for f in m['state']),7)
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp,[HERE/'model-draft.json'])
            text=(Path(tmp)/'models.hpp').read_text()
            self.assertIn('atlas::tensor_expm_or_mark',text)
            self.assertIn('atlas::scalar_log1p_or_mark',text)
            self.assertNotIn('barodesy_rate(',text)

    def test_all_predeclared_rate_and_rejection_gates(self):
        result=check.run()
        self.assertEqual(len(result['records']),37)
        self.assertEqual(len(result['invalid']),19)
        self.assertTrue(all(x['stress_scaled_error']<=2e-12 and x['void_ulp_error']<=4 for x in result['records']))
        self.assertFalse(result['compiled_execution'])
        self.assertFalse(result['admission'])

    def test_expm_argument_envelope_parameter_corners(self):
        bound=2*math.exp(1.5*math.sqrt(3))
        self.assertLess(bound,64)
        corners=[c for c in self.ref['records'] if c['id'].startswith('corner-')]
        self.assertEqual(len(corners),12)
        for c in corners:
            self.assertLessEqual(c['oracle120']['argument_norm'],bound*(1+1e-15))
        # Hydroextension reaches the analytic supremum; no parameter sampling proof.
        key='corner--2.0-1.5-extension'
        self.assertAlmostEqual(self.expected[key]['oracle120']['argument_norm']/bound,1.,places=14)

    def test_rotational_and_reflection_covariance(self):
        base=check.draft_rate(self.cases['oblique'])
        for name,q in self.inputs['rotations'].items():
            got=check.draft_rate(self.cases[name]);target=rotate(base[:6],q)
            scale=math.hypot(*base[:6])
            self.assertLess(max(abs(x-y)for x,y in zip(got[:6],target))/scale,2e-12)
            self.assertLessEqual(abs(got[6]-base[6]),4*math.ulp(base[6]))
            # Oracle covariance checked separately; not just shared interpreter parity.
            oracle=self.expected[name]['oracle120']['values']
            obase=self.expected['oblique']['oracle120']['values']
            target=rotate(obase[:6],q)
            self.assertLess(max(abs(x-y)for x,y in zip(oracle[:6],target))/math.hypot(*obase[:6]),2e-12)

    def test_positive_homogeneity_and_reversal(self):
        base=check.draft_rate(self.cases['oblique'])
        for name,factor in [('homogeneous-quarter',.25),('homogeneous-four',4.)]:
            got=check.draft_rate(self.cases[name])
            for x,y in zip(base,got):self.assertAlmostEqual(y/(factor*x),1.,places=13)
        rev=check.draft_rate(self.cases['reverse'])
        self.assertGreater(math.hypot(*(x+y for x,y in zip(base[:6],rev[:6]))),1.)

    def test_stress_unit_scaling_with_c4_physical_parameter(self):
        base=check.draft_rate(self.cases['oblique'])
        for factor in [.01,100.]:
            got=check.draft_rate(self.cases['unit-scale-'+str(factor)])
            for x,y in zip(base[:6],got[:6]):self.assertAlmostEqual(y/(factor*x),1.,places=13)
            self.assertEqual(base[6],got[6])

    def test_exact_zero_loading_extension_and_reject_underflow(self):
        self.assertEqual(check.draft_rate(self.cases['zero']),[0.]*7)
        self.assertEqual(self.expected['zero']['oracle120']['values'],[0.]*7)
        bad=next(c for c in self.inputs['invalid'] if c['id']=='tiny-loading')
        with self.assertRaises(ValueError):check.draft_rate(bad)
        with self.assertRaises(ValueError):reference.evaluate(bad)

    def test_independent_source_diagonal_sign_mandel(self):
        c=copy.deepcopy(self.cases['oblique'])
        c['state']=[120000.,90000.,70000.,0.,0.,0.,.75]
        c['loading']=[.001,-.0003,.0002,0.,0.,0.]
        p=c['parameters'];t=[-x for x in c['state'][:3]];d=[-x for x in c['loading'][:3]]
        sn=math.hypot(*t);dn=math.hypot(*d);u=[x/dn for x in d];delta=math.fsum(u)
        r=[-math.exp(p['c1']*math.exp(p['c2']*delta)*x)for x in u];rn=math.hypot(*r)
        b=(p['ec0']-p['emin'])/(p['ec0']+1)*((p['c4']+p['c5']*sn)/p['c4'])**(-(1+p['emin'])/p['c5'])
        ec=(p['emin']+b)/(1-b);h=-(p['c4']+p['c5']*sn)/(.75-p['emin'])
        source=[-h*((delta+p['c3']*ec)*x/rn-p['c3']*.75*y/sn)*dn for x,y in zip(r,t)]
        got=check.draft_rate(c)
        self.assertLess(max(abs(x-y)for x,y in zip(got[:3],source))/math.hypot(*source),2e-13)
        self.assertEqual(got[3:6],[0.,0.,0.])
        self.assertAlmostEqual(got[6],-(1+.75)*math.fsum(c['loading'][:3]),places=17)

    def test_parent_immutability_failure_then_recovery_python_only(self):
        good=copy.deepcopy(self.cases['oblique']);parent=copy.deepcopy(good)
        first=check.draft_rate(good)
        for bad in self.inputs['invalid']:
            original=copy.deepcopy(bad)
            with self.assertRaises((ValueError,ArithmeticError)):check.draft_rate(bad)
            self.assertEqual(bad,original)
        self.assertEqual(good,parent)
        self.assertEqual(first,check.draft_rate(good))
        # This is pure evaluation immutability, not a common-engine integration transaction.

    def test_reference_forgery_missing_duplicate_precision_failure_rejected(self):
        variants=[]
        r=copy.deepcopy(self.ref);r['records'][0]['oracle120']['values'][0]+=1;variants.append(r)
        r=copy.deepcopy(self.ref);r['records'].pop();variants.append(r)
        r=copy.deepcopy(self.ref);r['records'][1]=copy.deepcopy(r['records'][0]);variants.append(r)
        r=copy.deepcopy(self.ref);r['records'][0]['oracle80']['decimal_values'][0]='0';variants.append(r)
        r=copy.deepcopy(self.ref);r['invalid'][0]['rejected']=False;variants.append(r)
        r=copy.deepcopy(self.ref);r['invalid'][0]['rejected']=1;variants.append(r)
        r=copy.deepcopy(self.ref);next(x for x in r['records'] if x['id']=='zero')['oracle120']['values'][0]=False;variants.append(r)
        for r in variants:
            with self.assertRaises(ValueError):check.checked_reference(r)

    def test_frozen_dependency_change_rejected(self):
        original=check.sha
        with patch.object(check,'sha',side_effect=lambda p:'0'*64 if Path(p).name=='model-draft.json'else original(p)):
            with self.assertRaises(ValueError):check.checked_reference(self.ref)

    def test_accuracy_gate_corruptions_and_bool_aliases(self):
        c=self.cases['oblique'];target=self.expected[c['id']]['oracle120']['values']
        for kind in ['bool','nan','state','void','short']:
            got=list(target)
            if kind=='bool':got[0]=True
            if kind=='nan':got[1]=float('nan')
            if kind=='state':got[2]+=1.
            if kind=='void':got[6]+=1e-10
            if kind=='short':got.pop()
            with self.assertRaises(ValueError):check.assess_values(c,got,target)
        zero=list(self.expected['zero']['oracle120']['values']);zero[0]=1e-300
        with self.assertRaises(ValueError):check.assess_values(self.cases['zero'],zero,[0.]*7)

if __name__=='__main__':unittest.main()
