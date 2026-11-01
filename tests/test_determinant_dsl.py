"""Dimension/interpretation registration and independent archived receipt checks."""
from tests.historical_generation import generate as historical_generate
import copy
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path
from atlas.dsl import Type, Sym, PRESSURE, ZERO, ValidationError, cpp, evaluate, infer, parse
from atlas.compiler import generate
from atlas.history_compiler import _expression, generate as history_header
from atlas.history import advance, make_snapshot, validate_program
from atlas.evidence import checked_receipt
from atlas.source_replay import registered
ROOT=Path(__file__).resolve().parents[1]
def bits(v):return struct.pack('>d',v).hex()
class DeterminantDsl(unittest.TestCase):
 def test_dimensions_and_invalid_shapes(self):
  for dim in (ZERO,PRESSURE,(1,2,3,4)):
   self.assertEqual(infer(parse('determinant(A)'),{'A':Type('sym',dim)}),Type(dim=tuple(3*x for x in dim)))
  for expr in ('determinant(1)','determinant(A,A)','determinant()','determinant(A)+trace(A)'):
   with self.subTest(expr=expr),self.assertRaises(ValidationError):infer(parse(expr),{'A':Type('sym',PRESSURE)})
 def test_independent_primal_corpus_via_interpreter(self):
  cases=json.loads((ROOT/'catalogue/investigations/symmetric-determinant-v1/protocol.json').read_text())['cases']
  for c in cases:
   env={'A':Sym(tuple(float(v)for v in c['values']))};e=c['primal_expectation']
   with self.subTest(case=c['id']):
    if e['ok']:self.assertEqual(bits(evaluate(parse('determinant(A)'),env)),bits(float.fromhex(e['hex'])))
    else:
     with self.assertRaises(ValidationError):evaluate(parse('determinant(A)'),env)
 def test_masking_and_lazy_branches(self):
  bad=Sym((1e308,1e308,1e308,0.,0.,0.));env={'A':bad}
  for expr in ('0*determinant(A)','select(determinant(A)>0,1,2)','min(0,determinant(A))','determinant(A)*0'):
   with self.subTest(expr=expr),self.assertRaises(ValidationError):evaluate(parse(expr),env)
  self.assertEqual(evaluate(parse('select(1>0,7,determinant(A))'),env),7.)
  self.assertEqual(evaluate(parse('select(1<0,determinant(A),9)'),env),9.)
  # A later valid context is independent of prior failures.
  self.assertEqual(evaluate(parse('determinant(A)'),{'A':Sym((1.,1.,1.,0.,0.,0.))}),1.)
 def test_generated_registration_preserves_old_model_headers(self):
  # Compare against the exact pre-change compiler in an isolated capsule in
  # the separate historical replay. Here unused helper includes must be absent.
  with tempfile.TemporaryDirectory()as tmp:
   generate(tmp,[ROOT/'models/linear-elastic.json'])
   self.assertNotIn('checked_determinant.hpp',(Path(tmp)/'models.hpp').read_text())
  self.assertIn('atlas::determinant_or_mark(',cpp(parse('determinant(A)')))
  h=ROOT/'catalogue/investigations/clay2005-rates-v3'
  with tempfile.TemporaryDirectory()as tmp:
   historical_generate(tmp,[h/'model.json'],'clay2005-rates-v3')
   for name in ('models.hpp','models.json'):
    self.assertEqual((Path(tmp)/name).read_bytes(),(h/'expected-generated'/name).read_bytes())
 def test_history_registration_and_original_bindings(self):
  emitted=_expression(parse('select(1>0,determinant(A),0)'),{'A':'input_A'})
  self.assertIn('atlas::determinant_accuracy::checked(',emitted)
  self.assertIn('throw std::runtime_error("unsupported/nonfinite history determinant")',emitted)
  self.assertIn(' ? ',emitted)
  data=json.loads((ROOT/'catalogue/source-replays/dsl-identity-v4/inventory.json').read_text())
  self.assertEqual(len(data['references']),22)
  for row in data['references']+data['secondary_source_map_references']:
   self.assertEqual(checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']),(ROOT/row['archived_path']).resolve())
 def test_history_transaction_and_header(self):
  p=json.loads((ROOT/'tests/fixtures/log1p-history/log1p.json').read_text())
  p['id']='synthetic-determinant-history'
  p['phases'][0]['writes']['A']='select(g>0,determinant(X)*I,I)'
  validate_program(p)
  parent=make_snapshot(p,{'A':[0.]*6},generation=7,preparation_epoch=3)
  before=copy.deepcopy(parent)
  good={'X':[2.,3.,4.,0.,0.,0.],'gate':1.}
  result=advance(p,parent,good)
  self.assertTrue(result['ok']);self.assertEqual(result['snapshot']['values']['A'],[24.,24.,24.,0.,0.,0.])
  bad={'X':[1e308,1e308,1e308,0.,0.,0.],'gate':1.}
  failed=advance(p,parent,bad)
  self.assertFalse(failed['ok']);self.assertIs(failed['snapshot'],parent);self.assertEqual(parent,before)
  self.assertEqual(failed['events'],[])
  self.assertTrue(advance(p,parent,bad|{'gate':0.})['ok'])
  self.assertEqual(advance(p,parent,good),result)
  header=history_header([p]);self.assertIn('#include "atlas/checked_determinant.hpp"',header)
  self.assertIn('atlas::determinant_accuracy::checked(',header)
 def test_model_generator_includes_checked_operator(self):
  m=json.loads((ROOT/'models/hypoplastic-clay-2013.json').read_text())
  self.assertEqual(m['schema_version'],'0.3')
  m['id']='synthetic-determinant-registration'
  m['derived'].append({'name':'det_probe','expr':'determinant(sigma/p_ref)'})
  with tempfile.TemporaryDirectory()as tmp:
   path=Path(tmp)/'fixture.json';path.write_text(json.dumps(m))
   generate(Path(tmp)/'generated',[path])
   header=(Path(tmp)/'generated/models.hpp').read_text()
   self.assertIn('#include "atlas/checked_determinant.hpp"',header)
   self.assertIn('atlas::determinant_or_mark(',header)
 def test_documentation_source_bindings(self):
  h=ROOT/'catalogue/source-replays/dsl-identity-v5'
  data=json.loads((h/'inventory.json').read_text());self.assertEqual(len(data['references']),9)
  for row in data['references']:
   self.assertEqual(checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']),(ROOT/row['archived_path']).resolve())
  audit=json.loads((h/'complete-receipt-audit.json').read_text())
  self.assertEqual(audit['resolved'],59);self.assertEqual(audit['unresolved'],[])
 def test_original_receipt_identity_bindings(self):
  data=json.loads((ROOT/'catalogue/source-replays/dsl-identity-v3/inventory.json').read_text())
  self.assertEqual(len(data['references']),28)
  for row in data['references']+data['secondary_source_map_references']:
   with self.subTest(document=row['document'],source=row['original_path']):
    self.assertEqual(checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']),(ROOT/row['archived_path']).resolve())
 def test_original_tagged_raw_outcomes_are_reproduced(self):
  result=registered(ROOT,'catalogue/source-replays/tagged-rates-v3/registry.json','tagged-rates-v3',timeout=60)
  d=json.loads(result['stdout'])
  self.assertEqual([s['outcome']for s in d['studies']],['failed','passed'])
  self.assertFalse(d['compiled_execution']);self.assertFalse(d['artifact_reopen'])
if __name__=='__main__':unittest.main()
