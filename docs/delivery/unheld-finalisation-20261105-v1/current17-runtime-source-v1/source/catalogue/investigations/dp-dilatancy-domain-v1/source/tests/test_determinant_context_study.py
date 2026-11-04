"""Frozen generated-context expectations and assessor corruption witnesses."""
import copy,importlib.util,json,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'catalogue/investigations/determinant-expressions-v1'
spec=importlib.util.spec_from_file_location('det_context_assessor',HERE/'assess.py');assessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(assessor)
class DeterminantContextProtocol(unittest.TestCase):
 def test_reference_inputs_and_expectations_are_unchanged(self):
  refs={c['id']:c for c in json.loads((ROOT/'docs/reviews/symmetric-determinant-reference-v1/cases.json').read_text())['cases']}
  rows=[c for c in json.loads((HERE/'cases.json').read_text())if'reference_id'in c]
  self.assertEqual(len(rows),8*78)
  for row in rows:
   ref=refs[row['reference_id']];e=row['expectation']
   self.assertEqual(row['values'],ref['values']);self.assertEqual(row['seeds'],ref['seeds'])
   self.assertIs(e['ok'],ref['expectation']['ok'])
   if e['ok']:
    self.assertEqual(e['scalar_bits'],struct.pack('>d',float.fromhex(ref['expectation']['value_hex'])).hex())
    self.assertEqual(e['derivative_bits'],[struct.pack('>d',float.fromhex(v)).hex()for v in ref['expectation']['derivatives_hex']])
 def test_all_models_are_explicit_v03_and_recovery_literal_controls_match(self):
  for p in (HERE/'models').glob('*.json'):self.assertEqual(json.loads(p.read_text())['schema_version'],'0.3')
  controls={};previous=None
  for c in json.loads((HERE/'cases.json').read_text()):
   if'recovery_of'in c:
    self.assertEqual(previous['id'],c['after_rejection']);self.assertFalse(previous['expectation']['ok'])
    original=controls[c['recovery_of']]
    for name in ('model','values','seeds','parameter','initial','check_only','observables_only','expectation'):self.assertEqual(c[name],original[name])
   controls[c['id']]=c;previous=c
 def test_every_context_and_all38_poison_columns(self):
  rows=json.loads((HERE/'cases.json').read_text());self.assertEqual(len({c['context']for c in rows}),9)
  for context in ('equation','derived','domain','initial','observable','reset-guard','reset-value'):
   poison=[c for c in rows if c['context']==context and '/poison-column-'in c['id']and not c['id'].endswith('/recover')]
   self.assertEqual(len(poison),38);self.assertTrue(all(not c['expectation']['ok']for c in poison))
 def test_assessor_rejects_each_direction_and_status_identity_corruption(self):
  c=next(c for c in json.loads((HERE/'cases.json').read_text())if c['expectation']['ok']and len(c['expectation']['derivative_bits'])==38)
  identity=(c['model_id'],'abc');row=dict(c['expectation'],id=c['id'],model_id=identity[0],catalogue_hash=identity[1]);assessor.check_row(row,c,identity)
  for col in range(38):
   changed=copy.deepcopy(row);changed['derivative_bits'][col]=format(int(changed['derivative_bits'][col],16)^1,'016x')
   with self.assertRaises(AssertionError):assessor.check_row(changed,c,identity)
  for field,value in [('ok',1),('input_unchanged',False),('catalogue_hash','bad'),('model_id','bad'),('output_count',True)]:
   changed=copy.deepcopy(row);changed[field]=value
   with self.assertRaises(AssertionError):assessor.check_row(changed,c,identity)
if __name__=='__main__':unittest.main()
