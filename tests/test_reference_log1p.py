import importlib.util, json, math, pathlib, sys, unittest
from decimal import Decimal,localcontext
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('independent_log1p',ROOT/'tools/reference_log1p.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Oracle(unittest.TestCase):
 def test_exact_identities(self):
  for x,n in ((0.,0),(1.,1),(3.,2),(7.,3)):
   v,d=m.oracle(x)
   with localcontext() as ctx:
    ctx.prec=650
    self.assertLessEqual(abs(v-Decimal(n)*Decimal(2).ln()),Decimal('1e-648'))
    self.assertEqual(d,Decimal(2)**(-n))
  self.assertTrue(m.oracle(-0.)[0].is_signed())
 def test_actual_binary64_near_minus_one(self):
  x=math.nextafter(-1.,0.);v,d=m.oracle(x)
  self.assertEqual(d,Decimal(2)**53)
  with localcontext() as ctx:
   ctx.prec=650
   self.assertLess(abs(v+53*Decimal(2).ln()),Decimal('1e-646'))
 def test_tiny_series_bound(self):
  for x in m.inputs():
   if x and abs(x)<1e-12:
    v,d=m.oracle(x)
    with localcontext() as ctx:
     ctx.prec=700;t=Decimal.from_float(x); approx=t-t*t/2
     # Third-order series remainder bounded for |x|<1e-12; allow oracle rounding.
     self.assertLessEqual(abs(v-approx),abs(t)**3/(3*(1-abs(t)))+abs(t)*Decimal('1e-170'))
    self.assertEqual(float(v),x if abs(x)<1e-20 else float(v))
 def test_precision_refinement_and_math_secondary(self):
  data=m.corpus();self.assertEqual(data['case_count'],38)
  for row in data['cases']:
   self.assertEqual(float.fromhex(row['x_hex']),row['x'])
   for r in row['precision_refinement']:self.assertLessEqual(Decimal(r['relative']),Decimal('1e-170'))
   self.assertLessEqual(abs(math.log1p(row['x'])-row['value']),2*math.ulp(row['value']))
   self.assertTrue(math.isfinite(row['derivative']))
 def test_invalid(self):
  for x in (-1.,math.nextafter(-1.,-math.inf),float('nan'),float('inf'),-float('inf'),True,0):
   with self.assertRaises(ValueError):m.oracle(x)
 def test_retained_reproducibility(self):
  self.assertEqual(m.corpus(),json.loads((ROOT/'catalogue/investigations/scalar-log1p-reference-v1/log1p.json').read_text()))
if __name__=='__main__':unittest.main()
