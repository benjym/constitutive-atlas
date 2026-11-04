"""Independent Decimal oracle tests; stdlib only, no Atlas/native imports."""
import json
import math
from decimal import Decimal,localcontext
from pathlib import Path
import unittest
from tools import reference_symmetric_expm as g

class DecimalExpmOracle(unittest.TestCase):
    def test_complete_corpus_and_refinement(self):
        path=Path(g.__file__).resolve().parents[1]/'catalogue/investigations/symmetric-expm-reference-v1/reference.json'
        saved=json.loads(path.read_text());current=g.corpus()
        self.assertEqual(saved,current)
        self.assertGreaterEqual(len(saved['cases']),30);self.assertLessEqual(len(saved['cases']),50)
        self.assertEqual(len({c['id']for c in saved['cases']}),len(saved['cases']))
        for case in saved['cases']:
            self.assertEqual(case['input_sha256'],g.digest(case['input']))
            self.assertEqual(len(case['oracle']['value']),6)
            self.assertEqual([len(row)for row in case['oracle']['jacobian']],[6]*6)
            self.assertLess(Decimal(case['refinement']['maximum_scaled_value']),Decimal('1e-65'))
            self.assertLess(Decimal(case['refinement']['maximum_scaled_jacobian']),Decimal('1e-65'))
            self.assertTrue(all(math.isfinite(x)for x in case['oracle']['value']))
    def test_zero_and_isotropic_all_six_directions(self):
        with localcontext()as ctx:
            ctx.prec=180
            for c in (-32.,-1.,0.,1.,32.):
                o=g.oracle([c,c,c,0.,0.,0.]);expected=Decimal.from_float(c).exp()
                for i,x in enumerate(o['value']):self.assertLess(abs(x-(expected if i<3 else 0))/max(Decimal(1),expected),Decimal('1e-120'))
                for i,row in enumerate(o['jacobian']):
                    for j,x in enumerate(row):self.assertLess(abs(x-(expected if i==j else 0))/max(Decimal(1),expected),Decimal('1e-120'))
    def test_actual_binary64_diagonal_frechet_divided_difference(self):
        # Independent analytic derivative, not differentiated matrix recurrence.
        with localcontext()as ctx:
            ctx.prec=180
            for gap in (0.,1e-4,1e-8,1e-12,math.ulp(1.)):
                v=[1.,1.+gap,-2.,0.,0.,0.];o=g.oracle(v);lam=[Decimal.from_float(x)for x in v[:3]]
                coeff=[x.exp()for x in lam]
                for i,j in ((0,1),(1,2),(0,2)):
                    coeff.append(lam[i].exp()if lam[i]==lam[j]else(lam[i].exp()-lam[j].exp())/(lam[i]-lam[j]))
                for i,row in enumerate(o['jacobian']):
                    for j,x in enumerate(row):self.assertLess(abs(x-(coeff[i]if i==j else 0)),Decimal('1e-115'))
    def test_pure_shear_closed_form(self):
        with localcontext()as ctx:
            ctx.prec=180;s2=Decimal(2).sqrt();a=Decimal(2)/s2
            co=(a.exp()+(-a).exp())/2;si=(a.exp()-(-a).exp())/2
            expected=[co,co,Decimal(1),s2*si,Decimal(0),Decimal(0)]
            for x,y in zip(g.oracle([0.,0.,0.,2.,0.,0.])['value'],expected):self.assertLess(abs(x-y),Decimal('1e-120'))
    def test_self_adjoint_full_jacobian(self):
        for case in g.cases():
            o=g.oracle(case['input'])
            with localcontext()as ctx:
                ctx.prec=180;scale=max(Decimal(1),*(abs(x)for row in o['jacobian']for x in row))
                for i in range(6):
                    for j in range(6):self.assertLess(abs(o['jacobian'][i][j]-o['jacobian'][j][i])/scale,Decimal('1e-115'))
    def test_actual_rounded_rotation_covariance_secondary(self):
        Q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
        columns=[g.rotate([float(i==j)for i in range(6)],Q)for j in range(6)]
        M=[[columns[j][i]for j in range(6)]for i in range(6)]
        v=[2.,-1.,.5,.7,-.2,.4];a=g.oracle(v);b=g.oracle(g.rotate(v,Q))
        expected=g.rotate([float(x)for x in a['value']],Q)
        for x,y in zip(b['value'],expected):self.assertLess(abs(float(x)-y),1e-13)
        J=[[float(x)for x in row]for row in a['jacobian']]
        for i in range(6):
            for j in range(6):
                expected=sum(M[i][k]*J[k][l]*M[j][l]for k in range(6)for l in range(6))
                self.assertLess(abs(float(b['jacobian'][i][j])-expected),1e-13)
    def test_invalid_inputs_separate_from_mathematical_domain(self):
        for v in ([True,0.,0.,0.,0.,0.],[0.]*5,[0.]*7,[math.nextafter(64.,math.inf),0.,0.,0.,0.,0.]):
            with self.assertRaises(ValueError):g.oracle(v)
        for value in (math.nan,math.inf,-math.inf):
            for j in range(6):
                v=[0.]*6;v[j]=value
                with self.assertRaises(ValueError):g.oracle(v)
        for precision in (True,40,1.5):
            with self.assertRaises(ValueError):g.oracle([0.]*6,precision)

if __name__=='__main__':unittest.main()
