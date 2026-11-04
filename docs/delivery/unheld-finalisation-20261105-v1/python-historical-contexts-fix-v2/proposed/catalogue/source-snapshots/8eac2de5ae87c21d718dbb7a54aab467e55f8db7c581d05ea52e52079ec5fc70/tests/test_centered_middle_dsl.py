"""Certified centered-middle routing, independent oracle, strict typing and transactions."""
import copy,importlib.util,json,math,subprocess,sys,tempfile,unittest
from pathlib import Path
from atlas.model import ROOT
from atlas.dsl import Type,Sym,PRESSURE,ZERO,ValidationError,parse,infer,evaluate,cpp,has_value_only_dependency
from atlas.history import advance,make_snapshot,validate_program
P=ROOT/'docs/reviews/centered-middle-runtime-v1'
class CenteredMiddleDslTests(unittest.TestCase):
 def test_types_and_value_only_control(self):
  for dim in (ZERO,PRESSURE,(1,2,3,4)):
   self.assertEqual(infer(parse('principal_centered_mid_gt(A,Y)'),{'A':Type('sym',dim),'Y':Type(dim=dim)}),Type('bool'))
  symbols={'A':Type('sym',PRESSURE),'Y':Type(dim=PRESSURE),'Z':Type()}
  for e in ('principal_centered_mid_gt(A,Z)','principal_centered_mid_gt(Y,A)','principal_centered_mid_gt(A,A)','principal_centered_mid_gt(A)','principal_centered_mid_gt(A,Y,Y)','principal_centered_mid_gt(A,Y)+1','principal_centered_mid_gt(A,Y)*Y'):
   with self.subTest(expr=e),self.assertRaises(ValidationError):infer(parse(e),symbols)
  self.assertTrue(has_value_only_dependency(parse('select(principal_centered_mid_gt(A,Y),1,2)')))
  self.assertIn('atlas::principal_centered_mid_gt_or_mark(',cpp(parse('principal_centered_mid_gt(A,Y)')))
 def test_all_frozen_literal_oracles(self):
  inputs=json.loads((ROOT/'docs/reviews/certified-centered-middle-v1/inputs.json').read_text())['cases'];results=json.loads((ROOT/'docs/reviews/certified-centered-middle-v1/checks.json').read_text())['rows']
  for row,result in zip(inputs,results):
   self.assertEqual(row['id'],result['id']);env={'A':Sym(tuple(float.fromhex(x)for x in row['mandel'])),'Y':float.fromhex(row['width'])}
   self.assertIs(evaluate(parse('principal_centered_mid_gt(A,Y)'),env),result['result'],row['id'])
 def test_failure_masking_and_lazy_recovery(self):
  good={'A':Sym((1.,-1.,0.,0.,0.,0.)),'Y':2.};bad=good|{'Y':-1.}
  for e in ('principal_centered_mid_gt(A,Y)','select(principal_centered_mid_gt(A,Y),7,9)'):
   with self.assertRaises(ValidationError):evaluate(parse(e),bad)
   self.assertEqual(evaluate(parse(e),good),False if e.startswith('principal_centered_mid_gt')else 9.)
  self.assertEqual(evaluate(parse('select(1>0,7,select(principal_centered_mid_gt(A,Y),3,4))'),bad),7.)
  for y in (math.nan,math.inf,-math.inf):
   with self.assertRaises(ValidationError):evaluate(parse('principal_centered_mid_gt(A,Y)'),good|{'Y':y})
  with self.assertRaises(ValidationError):evaluate(parse('principal_centered_mid_gt(A,Y)'),good|{'A':Sym((0.,)*5)})
 def test_normal_generation_and_history_transaction(self):
  spec=importlib.util.spec_from_file_location('range_fixtures',P/'prepare_fixtures.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
  with tempfile.TemporaryDirectory()as tmp:
   m,h=f.prepare(tmp);header=(Path(tmp)/'generated/models.hpp').read_text();self.assertIn('#include "atlas/checked_centered_middle.hpp"',header)
   hh=(Path(tmp)/'generated/history.hpp').read_text();self.assertIn('atlas::centered_middle_accuracy::checked(',hh)
  # A negative operand evaluated in the selected history branch must roll back.
  h['phases'][0]['writes']['A']='select(g>0,select(principal_centered_mid_gt(X,-g),I,2*I),I)';validate_program(h)
  parent=make_snapshot(h,{'A':[0.]*6},generation=7,preparation_epoch=3);before=copy.deepcopy(parent)
  failed=advance(h,parent,{'X':[0.]*6,'gate':1.});self.assertFalse(failed['ok']);self.assertEqual(failed['snapshot'],parent);self.assertEqual(parent,before)
  recovered=advance(h,parent,{'X':[0.]*6,'gate':0.});self.assertTrue(recovered['ok']);self.assertEqual(parent,before)

 def test_value_only_reset_dependency_rejected(self):
  from atlas.model import load,validate
  m=load(ROOT/'models/linear-elastic.json')
  m['derived'].append({'name':'decision','expr':'select(principal_centered_mid_gt(sigma,p_ref),p_ref,-p_ref)'})
  m['increment_reset']={'scope':'parent_increment','updates':[{'target':'sigma','guard':'decision','value':'sigma'}]}
  with self.assertRaises(ValidationError):validate(m)
 def test_unchanged_public_generator_bytes(self):
  import shutil,os
  from atlas.compiler import generate
  old=json.loads((P/'previous-sources.json').read_text())
  with tempfile.TemporaryDirectory()as tmp:
   t=Path(tmp);shutil.copytree(ROOT/'atlas',t/'atlas',ignore=shutil.ignore_patterns('__pycache__'))
   (t/'models').symlink_to(ROOT/'models',target_is_directory=True);(t/'schemas').symlink_to(ROOT/'schemas',target_is_directory=True)
   for n in ('atlas/dsl.py','atlas/compiler.py','atlas/history_compiler.py'):shutil.copyfile(ROOT/old[n]['archived_path'],t/n)
   code="from atlas.compiler import generate;generate('old-generated')"
   result=subprocess.run([sys.executable,'-B','-c',code],cwd=t,env=dict(os.environ,PYTHONPATH=str(t)),capture_output=True,text=True,timeout=30)
   self.assertEqual(result.returncode,0,result.stderr);models=generate(t/'new-generated');self.assertEqual(len(models),9)
   for name in ('models.hpp','models.json'):self.assertEqual((t/'old-generated'/name).read_bytes(),(t/'new-generated'/name).read_bytes(),name)
 def test_saved_native_wasm_gate_and_corruptions(self):
  spec=importlib.util.spec_from_file_location('range_assess',P/'assess.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
  inputs=json.loads((P/'requests.json').read_text());reports=[]
  for backend in ('native','wasm'):
   text=(P/(backend+'-responses.txt')).read_text();report=f.assess(text,inputs);reports.append(report)
   lines=text.splitlines();row=lines[0].split();row[2]=str(1-int(row[2]));lines[0]=' '.join(row)
   with self.assertRaises(AssertionError):f.assess('\n'.join(lines),inputs)
   lines=text.splitlines();lines[-1]='summary 1160 819 0 1'
   with self.assertRaises(AssertionError):f.assess('\n'.join(lines),inputs)
  self.assertEqual(reports[0],reports[1]);self.assertEqual(reports[0]['seed_and_primal_rejections'],819)
