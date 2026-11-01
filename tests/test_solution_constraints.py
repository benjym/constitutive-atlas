"""Physical constraints and residual extensions have separate contracts."""
import copy,json,math,tempfile,unittest,importlib.util
from pathlib import Path
from atlas.model import ROOT,load,validate,check_solution_state,interpret
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError
P=ROOT/'catalogue/investigations/tresca-solution-constraints-v4'
class SolutionConstraintTests(unittest.TestCase):
 def model(self):return load(P/'frozen/model.json')
 def test_boolean_state_parameter_only_typing(self):
  base=self.model()
  for expr in ['trace(sigma)','trace(sigma)>1','trace(de)>0*p_ref','trace(sigma_n)>0*p_ref','time>0','dt>0','width>0*p_ref','trace(ep)>0*p_ref']:
   m=copy.deepcopy(base);m['solution_constraints']=[expr]
   if expr=='trace(ep)>0*p_ref':pass
   with self.subTest(expr=expr),self.assertRaises(ValidationError):validate(m)
  m=copy.deepcopy(base);m['solution_constraints']=['trace(ep)>-1'];validate(m)
  m=copy.deepcopy(base);m['state'][1]['semantics']['role']='increment_unknown';m['initialization']['required_state']=['sigma'];m['solution_constraints']=['trace(ep)>-1']
  with self.assertRaises(ValidationError):validate(m)
 def test_explicit_profile_limit(self):
  from atlas.model import migrate_formulation
  m=migrate_formulation(load(ROOT/'models/hypoplastic-sand-vw96.json'));m['solution_constraints']=['trace(sigma)>0*p_ref']
  with self.assertRaisesRegex(ValidationError,'incremental residual'):validate(m)
  m=load(ROOT/'models/research/terracotta-2024-fig1.json');m['solution_constraints']=['1>0']
  with self.assertRaisesRegex(ValidationError,'unknown field solution_constraints|incremental residual'):validate(m)
 def test_raw_extension_allowed_physical_state_rejected(self):
  m=self.model();m['initial_checks']=[];validate(m)
  pars={'p_ref':1.,'lame_lambda':3.,'mu':2.,'k':3.};good={'sigma':[0.]*6,'ep':[0.]*6};bad=copy.deepcopy(good);bad['sigma'][0]=12.
  self.assertFalse(check_solution_state(m,bad,pars));self.assertTrue(check_solution_state(m,good,pars));self.assertEqual(interpret(m,bad,good,[0.]*6,pars)['sigma'].v[0],12.)
  with self.assertRaisesRegex(ValidationError,'solution_constraints'):initialize_state(m,bad,pars)
  before=copy.deepcopy(good);self.assertEqual(initialize_state(m,good,pars)['initial'],[0.]*12);self.assertEqual(good,before)
 def test_malformed_nonfinite_inputs_and_recovery(self):
  m=self.model();pars={'p_ref':1.,'lame_lambda':3.,'mu':2.,'k':3.};good={'sigma':[0.]*6,'ep':[0.]*6}
  for state in [{'sigma':[0.]*6},{'sigma':[0.]*5,'ep':[0.]*6},{'sigma':[0.]*6,'ep':[math.nan]*6}]:
   with self.assertRaises(ValidationError):check_solution_state(m,state,pars)
  for p in [pars|{'k':math.inf},pars|{'k':-1.},pars|{'unknown':1.}]:
   with self.assertRaises(ValidationError):check_solution_state(m,good,p)
  self.assertTrue(check_solution_state(m,good,pars))
 def test_unused_public_generation_bytes_unchanged(self):
  from tests.historical_generation import compare_public_generation
  with tempfile.TemporaryDirectory() as tmp:
   compare_public_generation(self,tmp,ROOT/'docs/reviews/solution-state-constraints-v1','solution-constraints',('atlas/compiler.py', 'atlas/model.py'))
