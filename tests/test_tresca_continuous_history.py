"""The temporal rejection remains a failure even when software checks pass."""
import copy,importlib.util,json,struct,unittest
from atlas.model import ROOT
P=ROOT/'catalogue/investigations/tresca-continuous-history-v1'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class TrescaContinuousHistoryTests(unittest.TestCase):
 def test_saved_failed_history_gate_and_exact_diagnosis(self):
  result=module('tresca_history_verify',P/'verify.py').verify();self.assertFalse(result['overall_pass'])
  for backend in ('native','wasm'):
   report=result[backend];self.assertEqual(report['attempted'],4);self.assertEqual(report['accepted'],3);self.assertEqual(len(report['failures']),10)
   self.assertEqual(report['failures'][0],{'step':2,'kind':'accepted-source-invalid-committed-state'})
   self.assertEqual(report['failures'][1],{'step':3,'kind':'step-rejected','source_parent_admissible':False})
 def test_own_parent_chain_and_unattempted_tail_preserved(self):
  for backend in ('native','wasm'):
   rows=[json.loads(l)for l in (P/(backend+'-responses.jsonl')).read_text().splitlines()]
   for i in range(1,4):self.assertEqual(rows[i]['parent_bits'],rows[i-1]['committed_bits'])
   self.assertEqual(rows[3]['output_bits'],rows[3]['parent_bits']);self.assertTrue(rows[3]['returned_parent'])
   self.assertTrue(all(not row['attempted']for row in rows[4:-1]));self.assertTrue(all(row['baseline_recovery']for row in rows[:4]))
 def test_assessor_rejects_additional_value_chain_and_recovery_corruption(self):
  a=module('tresca_history_assess',P/'assess.py');inputs=json.loads((P/'inputs.json').read_text());base=[json.loads(l)for l in (P/'native-responses.jsonl').read_text().splitlines()]
  rows=copy.deepcopy(base);rows[0]['baseline_recovery']=False;report=a.assess(rows,inputs);self.assertIn('baseline-recovery',[x['kind']for x in report['failures']])
  rows=copy.deepcopy(base);rows[2]['parent_bits'][0]='0'
  with self.assertRaises(AssertionError):a.assess(rows,inputs)
  rows=copy.deepcopy(base);value=int.from_bytes(struct.pack('>d',1.125),'big');rows[0]['output_bits'][6]=str(value);rows[0]['committed_bits'][6]=str(value);rows[1]['parent_bits'][6]=str(value)
  report=a.assess(rows,inputs);self.assertIn('update-value-accuracy',[x['kind']for x in report['failures']])
 def test_nearest_rounding_diagnostic_does_not_excuse_gate(self):
  d=module('tresca_history_rounding',P/'rounding_diagnostic.py').run()
  for backend in ('native','wasm'):
   row=d[backend][2];self.assertTrue(row['rounded_independent_stress_admissible']);self.assertFalse(row['actual_stress_matches_nearest_rounding']);self.assertEqual(row['different_components'],[3,4,5,9])
  self.assertFalse(json.loads((P/'assessment.json').read_text())['overall_pass'])
