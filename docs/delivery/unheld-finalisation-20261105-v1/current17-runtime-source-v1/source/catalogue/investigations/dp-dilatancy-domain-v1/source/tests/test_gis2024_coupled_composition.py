"""Typed production fragment composition versus independent retained14-rate oracle."""
import copy,json,math,unittest
from pathlib import Path
from atlas.dsl import Sym,ValidationError
from tools.inspect_gis2024_coupled import coupled_rates
from tools.reference_gis2024_coupled import coupled_rates as reference
ROOT=Path(__file__).resolve().parents[1]

class CoupledCompositionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cases=json.loads((ROOT/'catalogue/investigations/gis2024-coupled-rates-v1/reference.json').read_text())['cases']
 def close(self,a,b,rel=5e-10):
  self.assertEqual(len(a),len(b))
  for x,y in zip(a,b):self.assertAlmostEqual(x,y,delta=rel*max(1,abs(x),abs(y)))
 def typed(self,c):
  return c['state']|dict(sigma=Sym(tuple(c['state']['sigma'])),h=Sym(tuple(c['state']['h'])))
 def test_all38_retained_and_fresh_independent_oracle_cases(self):
  for c in self.cases:
   with self.subTest(id=c['id']):
    state=self.typed(c);de=Sym(tuple(c['de']));parameters=copy.deepcopy(c['parameters']);before=copy.deepcopy((state,de,parameters))
    r=coupled_rates(state,de,parameters);ref=reference(c['state'],c['de'],c['parameters'])
    self.assertEqual((state,de,parameters),before)
    self.assertIsInstance(r['sigma_rhs'],Sym);self.assertIsInstance(r['h_rhs'],Sym)
    self.assertEqual(len(r['derivative']),14);self.assertTrue(all(math.isfinite(v) for v in r['derivative']))
    self.close(r['derivative'],c['reference']['derivative']);self.close(r['derivative'],ref['derivative'])
    self.close(r['h_rhs'].v,ref['h_rhs'],rel=1e-15)
    self.close([r['e_rhs'],r['Omega_rhs']],[ref['e_rhs'],ref['Omega_rhs']],rel=1e-14)
    for key,value in ref['diagnostics'].items():
     if value is None:self.assertIsNone(r['diagnostics'][key])
     else:self.close([r['diagnostics'][key]],[value])
 def test_exactzero_rates_and_undefined_directional_diagnostics(self):
  c=self.cases[1];r=coupled_rates(self.typed(c),Sym(tuple(c['de'])),c['parameters'])
  self.assertEqual(r['derivative'],[0.]*14)
  for name in ('k','q','suppression'):self.assertIsNone(r['diagnostics'][name])
 def test_no_defaults_exact_types_and_finite_domains(self):
  c=self.cases[0];state=self.typed(c);de=Sym(tuple(c['de']));p=c['parameters']
  invalid=[(state,de,{k:v for k,v in p.items() if k!='R'}),(state,de,p|dict(extra=1)),(state|dict(extra=1),de,p),(state|dict(e=True),de,p),(state|dict(Omega=2),de,p),(state|dict(sigma=c['state']['sigma']),de,p),(state,c['de'],p),(state,Sym((True,)*6),p),(state,de,p|dict(hs=10**1000)),(state,de,p|dict(C_Omega=False)),(state,de,p|dict(R=0)),(state,de,p|dict(gamma_Omega=0)),(state,Sym((1e-300,0.,0.,0.,0.,0.)),p)]
  for args in invalid:
   before=copy.deepcopy(args)
   with self.assertRaises(ValidationError):coupled_rates(*args)
   self.assertEqual(args,before)

if __name__=='__main__':unittest.main()
