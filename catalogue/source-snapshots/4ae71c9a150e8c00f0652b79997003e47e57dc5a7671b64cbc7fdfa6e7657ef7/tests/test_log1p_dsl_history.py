"""Python-only checked log1p contract tests; no native/Wasm execution."""
import copy,json,math,tempfile,unittest
from pathlib import Path
from atlas.scalar_math import log1p
from atlas.dsl import DIMS,I,Sym,Type,ValidationError,cpp,evaluate,infer,parse
from atlas.model import ROOT,load,validate,interpret
from atlas.compiler import generate
from atlas.history import make_snapshot,advance,validate_program
from atlas.history_compiler import generate as history_header

class Log1pDslHistory(unittest.TestCase):
 def test_typing_arity_units_shape(self):
  symbols={'x':Type(),'S':Type('sym'),'p':Type('scalar',DIMS['Pa']),'flag':Type('bool')}
  self.assertEqual(infer(parse('log1p(x)'),symbols),Type())
  for expr in ('log1p()','log1p(x,x)','log1p(x=1)','log1p(S)','log1p(p)','log1p(flag)','log1p(1>0)'):
   with self.subTest(expr=expr),self.assertRaises(ValidationError):infer(parse(expr),symbols)
  self.assertEqual(cpp(parse('log1p(x)')),'atlas::scalar_log1p_or_mark(x, atlas_eval_ok)')
 def test_checked_scalar_domain_and_types(self):
  for x in (True,False,None,'0',complex(0),[0],Sym((0,)*6),float('nan'),float('inf'),-float('inf'),-1.,math.nextafter(-1.,-math.inf),10**1000):
   with self.subTest(x=repr(x)),self.assertRaises(ValueError):log1p(x)
  self.assertEqual(log1p(0),0.);self.assertEqual(log1p(1),math.log(2))
  with self.assertRaises(ValueError):evaluate(parse('log1p(x)'),{'x':True})
 def test_signed_zero_tiny_and_boundary(self):
  for x in (0.,-0.,math.ulp(0.),-math.ulp(0.),1e-300,-1e-300,1e-20,-1e-20):
   with self.subTest(x=x):
    value=evaluate(parse('log1p(x)'),{'x':x});self.assertEqual(value,x);self.assertEqual(math.copysign(1.,value),math.copysign(1.,x))
  x=math.nextafter(-1.,0.);self.assertTrue(math.isfinite(log1p(x)));self.assertAlmostEqual(log1p(x),-53*math.log(2),places=13)
 def test_lazy_arms_and_eager_mask(self):
  expr=parse('select(g > 0, log1p(x), log1p(y))')
  self.assertEqual(evaluate(expr,{'g':1.,'x':0.,'y':-2.}),0.)
  self.assertEqual(evaluate(expr,{'g':-1.,'x':-2.,'y':0.}),0.)
  with self.assertRaises(ValueError):evaluate(expr,{'g':-1.,'x':0.,'y':-2.})
  with self.assertRaises(ValueError):evaluate(parse('0 * log1p(x)'),{'x':-2.})
 def test_scale_restrictions(self):
  base=load(ROOT/'tests/fixtures/log1p/direct.json')
  for mode in ('state','observable'):
   m=copy.deepcopy(base)
   if mode=='state':m['state'][1]['scale']='1+log1p(0)'
   else:
    m=load(ROOT/'tests/fixtures/log1p/time-observable.json');m['observables'][0]['scale']='K*(1+log1p(0))'
   with self.subTest(mode=mode),self.assertRaisesRegex(ValidationError,'scale'):validate(m)
 def test_model_values_eager_failure_and_no_mutation(self):
  m=load(ROOT/'tests/fixtures/log1p/direct.json');state={'sigma':[0.]*6,'A':[.2,-.1,.3,.1,.05,-.2]};before=copy.deepcopy(state);de=[1.,0.,0.,0.,0.,0.]
  result=interpret(m,state,state,de);v=1+math.log1p(sum(state['A'][:3]));self.assertEqual(result['sigma'],Sym((v,v,v,0.,0.,0.)));self.assertEqual(state,before)
  bad=load(ROOT/'tests/fixtures/log1p/derived-cancel.json');state['A']=[-2.,0,0,0,0,0];before=copy.deepcopy(state)
  with self.assertRaises(ValueError):interpret(bad,state,state,de)
  self.assertEqual(state,before)
  # Compiler generation only: this test never invokes a compiler or binary.
  with tempfile.TemporaryDirectory() as tmp:
   generate(tmp,sorted((ROOT/'tests/fixtures/log1p').glob('*.json')))
   self.assertIn('scalar_log1p_or_mark',(Path(tmp)/'models.hpp').read_text())
 def test_history_transaction_lazy_rollback_recovery(self):
  p=json.loads((ROOT/'tests/fixtures/log1p-history/log1p.json').read_text());validate_program(p)
  parent=make_snapshot(p,{'A':[.1,.2,.3,.4,.5,.6]},generation=7,preparation_epoch=3);original=copy.deepcopy(parent)
  inputs={'X':[.2,-.1,.3,.1,.05,-.2],'gate':1.};good=advance(p,parent,inputs);self.assertTrue(good['ok'])
  v=1+math.log1p(sum(inputs['X'][:3]));self.assertEqual(good['snapshot']['values']['A'],[v]*3+[0.]*3);self.assertEqual(good['snapshot']['generation'],8);self.assertEqual(good['snapshot']['preparation_epoch'],3);self.assertEqual(len(good['events']),1)
  bad={'X':[-2.,0.,0.,0.,0.,0.],'gate':1.};failed=advance(p,parent,bad);self.assertFalse(failed['ok']);self.assertIs(failed['snapshot'],parent);self.assertEqual(failed['events'],[]);self.assertEqual(parent,original)
  inactive=advance(p,parent,bad|{'gate':0.});self.assertTrue(inactive['ok']);self.assertEqual(inactive['snapshot']['values']['A'],list(I.v));self.assertEqual(advance(p,parent,inputs),good)
  self.assertIn('scalar_log1p_checked',history_header([p]))
 def test_history_typed_boolean_argument_rejected(self):
  p=json.loads((ROOT/'tests/fixtures/log1p-history/log1p.json').read_text());p['phases'][0]['writes']['A']='log1p(g > 0)*I'
  with self.assertRaises(ValidationError):validate_program(p)
if __name__=='__main__':unittest.main()
