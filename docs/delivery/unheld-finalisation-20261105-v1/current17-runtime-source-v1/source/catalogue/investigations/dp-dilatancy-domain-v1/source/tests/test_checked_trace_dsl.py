"""Current checked tensor expression semantics; no compiled execution."""
import json,math,struct,unittest
from pathlib import Path
from atlas.dsl import Sym,trace,dev,evaluate,parse,ValidationError
ROOT=Path(__file__).resolve().parents[1]
class CheckedTraceDsl(unittest.TestCase):
 def test_all_independent_exact_binary64_fixtures(self):
  corpus=json.loads((ROOT/'docs/reviews/tensor-trace-accuracy-v1/corpus.json').read_text())
  for row in corpus['records']:
   a=Sym(tuple(float.fromhex(x)for x in row['inputs_hex'])+(0.,0.,0.))
   with self.subTest(case=row['id']):
    if row['ok']:self.assertEqual(struct.pack('>d',trace(a)).hex(),row['expected_bits'])
    else:
     with self.assertRaises(ValidationError):trace(a)
 def test_full_component_validation_and_lazy_selected_failure(self):
  for component in range(6):
   for value in (math.inf,-math.inf,math.nan,True,None,1j):
    a=[0.]*6;a[component]=value
    with self.subTest(component=component,value=repr(value)),self.assertRaises(ValidationError):trace(Sym(tuple(a)))
  a=Sym((1e308,1e308,1e308,0.,0.,0.))
  for expr in ('select(trace(A)>0,1,2)','0*trace(A)','select(trace(dev(A))>0,1,2)'):
   with self.subTest(expr=expr),self.assertRaises(ValidationError):evaluate(parse(expr),{'A':a})
  self.assertEqual(evaluate(parse('select(1>0,7,trace(A))'),{'A':a}),7.)
  self.assertEqual(evaluate(parse('select(1<0,trace(A),9)'),{'A':a}),9.)
 def test_deviator_result_overflow_and_recovery(self):
  m=float.fromhex('0x1.fffffffffffffp1023')
  with self.assertRaises(ValidationError):dev(Sym((m,-m,-m,0.,0.,0.)))
  self.assertEqual(dev(Sym((3.,0.,0.,2.,-1.,4.))).v,(2.,-1.,-1.,2.,-1.,4.))
