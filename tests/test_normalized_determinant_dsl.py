"""Normalized determinant typing, independent references and transaction routing."""
from tests.test_stress_scope import without_stress_scope_metadata
import copy,json,struct,tempfile,unittest
from fractions import Fraction as F
from pathlib import Path
from atlas.dsl import Type,Sym,PRESSURE,ZERO,ValidationError,cpp,evaluate,infer,parse
from atlas.compiler import generate
from atlas.history_compiler import _expression,generate as history_header
from atlas.history import advance,make_snapshot,validate_program
from atlas.evidence import checked_receipt
ROOT=Path(__file__).resolve().parents[1]
def bits(v):return struct.pack('>d',v).hex()
class NormalizedDeterminantDsl(unittest.TestCase):
 def test_dimensionless_for_all_tensor_units(self):
  for dim in (ZERO,PRESSURE,(1,2,3,4)):
   self.assertEqual(infer(parse('normalized_determinant(A)'),{'A':Type('sym',dim)}),Type())
  for expr in ('normalized_determinant(1)','normalized_determinant(A,A)','normalized_determinant()','normalized_determinant(A)+trace(A)'):
   with self.subTest(expr=expr),self.assertRaises(ValidationError):infer(parse(expr),{'A':Type('sym',PRESSURE)})
 def test_independent_scalar_references(self):
  p=json.loads((ROOT/'docs/reviews/normalized-determinant-reference-v1/cases.json').read_text())
  for c in p['cases']:
   env={'A':Sym(tuple(float(v)for v in c['values']))};e=c['primal_expectation']
   with self.subTest(case=c['id']):
    if e['ok']:self.assertEqual(bits(evaluate(parse('normalized_determinant(A)'),env)),bits(float.fromhex(e['hex'])))
    else:
     with self.assertRaises(ValidationError):evaluate(parse('normalized_determinant(A)'),env)
 def test_masking_and_lazy_branches(self):
  env={'A':Sym((1.,-1.,0.,0.,0.,0.))}
  for expr in ('0*normalized_determinant(A)','select(normalized_determinant(A)>0,1,2)','min(0,normalized_determinant(A))','normalized_determinant(A)*0'):
   with self.subTest(expr=expr),self.assertRaises(ValidationError):evaluate(parse(expr),env)
  self.assertEqual(evaluate(parse('select(1>0,7,normalized_determinant(A))'),env),7.)
  self.assertEqual(evaluate(parse('select(1<0,normalized_determinant(A),9)'),env),9.)
  self.assertEqual(bits(evaluate(parse('normalized_determinant(A)'),{'A':Sym((1e308,1e308,1e308,0.,0.,0.))})),bits(float(F(1,27))))
 def test_checked_cpp_registration(self):
  self.assertIn('atlas::normalized_determinant_or_mark(',cpp(parse('normalized_determinant(A)')))
  m=json.loads((ROOT/'models/hypoplastic-clay-2013.json').read_text());m['id']='synthetic-normalized-determinant'
  m['derived'].append({'name':'probe','expr':'normalized_determinant(sigma)'})
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);f=p/'fixture.json';f.write_text(json.dumps(m));generate(p/'generated',[f]);header=(p/'generated/models.hpp').read_text()
   self.assertIn('#include "atlas/checked_normalized_determinant.hpp"',header);self.assertIn('atlas::normalized_determinant_or_mark(',header)
 def test_unused_generation_unchanged(self):
  for study in ('clay2005-rates-v3','clay2005-determinant-rates-v1'):
   h=ROOT/'catalogue/investigations'/study
   with tempfile.TemporaryDirectory()as tmp:
    generate(tmp,[h/'model.json'])
    self.assertEqual((Path(tmp)/'models.json').read_bytes(),(h/'expected-generated/models.json').read_bytes())
    self.assertEqual(without_stress_scope_metadata((Path(tmp)/'models.hpp').read_text()),(h/'expected-generated/models.hpp').read_text())
 def test_history_header_and_transaction(self):
  p=json.loads((ROOT/'tests/fixtures/log1p-history/log1p.json').read_text());p['id']='synthetic-normalized-determinant-history';p['phases'][0]['writes']['A']='select(g>0,normalized_determinant(X)*I,I)';validate_program(p)
  parent=make_snapshot(p,{'A':[0.]*6},generation=7,preparation_epoch=3);before=copy.deepcopy(parent)
  good={'X':[1e308,1e308,1e308,0.,0.,0.],'gate':1.};valid=advance(p,parent,good)
  self.assertTrue(valid['ok']);self.assertEqual(valid['snapshot']['values']['A'],[float(F(1,27))]*3+[0.]*3)
  bad={'X':[1.,-1.,0.,0.,0.,0.],'gate':1.};failed=advance(p,parent,bad)
  self.assertFalse(failed['ok']);self.assertIs(failed['snapshot'],parent);self.assertEqual(parent,before);self.assertEqual(failed['events'],[])
  self.assertTrue(advance(p,parent,bad|{'gate':0.})['ok']);self.assertEqual(advance(p,parent,good),valid)
  header=history_header([p]);self.assertIn('#include "atlas/checked_normalized_determinant.hpp"',header);self.assertIn('atlas::normalized_determinant_accuracy::checked(',header);self.assertIn('unsupported/nonfinite history normalized determinant',header)
 def test_current_source_receipts_archived_exactly(self):
  inv=json.loads((ROOT/'catalogue/source-replays/dsl-identity-v6/inventory.json').read_text());self.assertEqual(len(inv['references']),10)
  for row in inv['references']:self.assertEqual(checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']),ROOT/row['archived_path'])
if __name__=='__main__':unittest.main()
