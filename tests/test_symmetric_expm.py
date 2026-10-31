"""Checked operator typing, interpreter and transaction checks; no native build."""
import copy,json,math,unittest
from atlas.dsl import DIMS,I,Sym,Type,ValidationError,cpp,evaluate,infer,parse,tensor_expm
from atlas.model import ROOT,load,validate,interpret
from atlas.compiler import generate
from atlas.history import make_snapshot,advance
from atlas.history_compiler import generate as history_header

class SymmetricExpm(unittest.TestCase):
 def test_actual_binary64_corpus_against_independent_decimal_values(self):
  ref=json.loads((ROOT/'catalogue/investigations/symmetric-expm-reference-v1/reference.json').read_text())
  self.assertEqual(len(ref['cases']),44)
  for c in ref['cases']:
   actual=tensor_expm(Sym(tuple(c['input']))).v;target=c['oracle']['value']
   with self.subTest(case=c['id']):self.assertLessEqual(max(abs(x-y)for x,y in zip(actual,target))/max(1.,math.hypot(*target)),2e-13)
 def test_types_units_arity_and_scalar_exp_unchanged(self):
  symbols={'A':Type('sym'),'S':Type('sym',DIMS['Pa']),'x':Type()}
  self.assertEqual(infer(parse('expm(A)'),symbols),Type('sym'))
  for expr in ('expm(x)','expm(S)','expm()','expm(A,A)','expm(A=I)','expm(1>0)','exp(A)'):
   with self.subTest(expr=expr),self.assertRaises(ValidationError):infer(parse(expr),symbols)
  self.assertEqual(evaluate(parse('exp(1)'),{}),math.exp(1))
  self.assertEqual(cpp(parse('expm(A)')),'atlas::tensor_expm_or_mark(A, atlas_eval_ok)')
 def test_exact_cases_and_implementation_range(self):
  self.assertEqual(tensor_expm(Sym((0.,)*6)),I)
  a=tensor_expm(Sym((1.,1.,1.,0.,0.,0.)))
  for v in a.v[:3]:self.assertAlmostEqual(v,math.e,places=14)
  tensor_expm(Sym((64.,0.,0.,0.,0.,0.)))
  for values in ((math.nextafter(64.,math.inf),0,0,0,0,0),(float('nan'),0,0,0,0,0),(1e308,)*6,(True,0,0,0,0,0),(0,)*5):
   with self.subTest(values=values),self.assertRaises(ValidationError):tensor_expm(Sym(values))
 def test_select_preserves_lazy_unsupported_arm(self):
  expr=parse('select(g > 0, I, expm(A))');env={'g':1.,'I':I,'A':Sym((100.,0,0,0,0,0))}
  self.assertEqual(evaluate(expr,env),I)
  with self.assertRaises(ValidationError):evaluate(expr,env|{'g':-1.})
 def test_scale_context_restriction_and_internal_identifier(self):
  base=load(ROOT/'tests/fixtures/expm/direct.json')
  for mode in ('state-scale','observable-scale','flag-name'):
   m=copy.deepcopy(base)
   if mode=='state-scale':m['state'][1]['scale']='trace(expm(sym(0,0,0,0,0,0)))'
   if mode=='observable-scale':m['observables']=[dict(name='display',shape='scalar',unit='1',expr='trace(A)',scale='trace(expm(sym(0,0,0,0,0,0)))')]
   if mode=='flag-name':m['derived']=[dict(name='atlas_eval_ok',expr='1')]
   with self.subTest(mode=mode),self.assertRaises(ValidationError):validate(m)
 def test_schema_fixture_loading_interpretation_and_generation(self):
  paths=sorted((ROOT/'tests/fixtures/expm').glob('*.json'));self.assertEqual(len(paths),9)
  for path in paths:load(path)
  model=load(ROOT/'tests/fixtures/expm/direct.json');state={'sigma':[0.]*6,'A':[.2,-.1,.3,.1,.2,.4]}
  got=interpret(model,state,state,[1.,0,0,0,0,0])['sigma'];self.assertEqual(got,tensor_expm(Sym(tuple(state['A']))))
  bad=load(ROOT/'tests/fixtures/expm/derived-cancel.json');state['A']=[100.,0,0,0,0,0]
  with self.assertRaises(ValueError):interpret(bad,state,state,[1.,0,0,0,0,0])
  import tempfile
  with tempfile.TemporaryDirectory()as tmp:
   generate(tmp,paths);text=(__import__('pathlib').Path(tmp)/'models.hpp').read_text()
   self.assertIn('atlas_eval_ok',text);self.assertIn('atlas::finite_value',text)
 def test_history_success_lazy_failure_rollback_and_recovery(self):
  p=json.loads((ROOT/'tests/fixtures/expm-history/expm.json').read_text());parent=make_snapshot(p,{'A':[0.]*6},generation=7,preparation_epoch=3)
  X=[.2,-.1,.3,.1,.2,.4];got=advance(p,parent,{'X':X,'gate':1.});self.assertTrue(got['ok']);self.assertEqual(got['snapshot']['values']['A'],list(tensor_expm(Sym(tuple(X))).v))
  self.assertEqual(got['snapshot']['generation'],8);self.assertEqual(got['snapshot']['preparation_epoch'],3)
  bad={'X':[65.,0,0,0,0,0],'gate':1.};failed=advance(p,parent,bad);self.assertFalse(failed['ok']);self.assertIs(failed['snapshot'],parent);self.assertEqual(failed['events'],[])
  inactive=advance(p,parent,bad|{'gate':0.});self.assertTrue(inactive['ok']);self.assertEqual(inactive['snapshot']['values']['A'],list(I.v))
  self.assertEqual(advance(p,parent,{'X':X,'gate':1.}),got)
  self.assertIn('tensor_expm_checked',history_header([p]))

if __name__=='__main__':unittest.main()
