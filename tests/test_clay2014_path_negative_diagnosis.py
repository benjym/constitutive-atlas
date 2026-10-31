"""Retained negative evidence remains negative; no compiled calls."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import diagnose_clay2014_paths as d

class NegativeDiagnosisTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  # Fail immediately if a regression tries to execute a compiled collector.
  cls.forbid=patch.object(d.study.subprocess,'Popen',side_effect=AssertionError('compiled execution forbidden'));cls.forbid.start()
  cls.fresh=d.build_diagnosis()
 @classmethod
 def tearDownClass(cls):cls.forbid.stop()
 def test_exact_frozen_recomputation(self):
  stage=Path(d.__file__).resolve().parents[1]/'catalogue/investigations/clay2014-paths-v1/negative-diagnosis.json'
  self.assertEqual(json.loads(stage.read_text()),self.fresh)
 def test_original_acceptance_stays_failed_despite_parity(self):
  self.assertEqual(self.fresh['outcome'],'failed');self.assertIs(self.fresh['compiled_execution'],False)
  self.assertTrue(self.fresh['state_parent_parity']['passed']);self.assertEqual(self.fresh['state_parent_parity']['state_and_parent_updates'],288)
  for result in self.fresh['backends']:
   self.assertEqual(result['checks']['frozen_full_assessor'],'global refinement unresolved at physical endpoint: stress')
   self.assertEqual(result['summary']['endpoint_inequalities_checked'],144)
   self.assertEqual(result['summary']['endpoint_inequalities_failed'],4)
 def test_both_backends_fail_the_same_four_exact_inequalities(self):
  want={(1,'stress'),(1,'e'),(2,'e'),(3,'e')}
  for result in self.fresh['backends']:
   self.assertEqual({(r['segment'],r['channel'])for r in result['refinement_failures']},want)
   for r in result['refinement_failures']:
    self.assertEqual(r['case'],'isotropic-ratios-hydro-reversal');self.assertEqual(r['partitions'],7)
    self.assertEqual(r['inequality'],'middle<=.65loose')
    self.assertEqual(r['rhs'],.65*r['errors_loose_middle_tight'][0]+2*(r['floor']+r['reference_uncertainty']))
    self.assertGreater(r['lhs'],r['rhs'])
 def test_accuracy_transactions_and_raw_are_separate_checks(self):
  for result in self.fresh['backends']:
   self.assertEqual((result['trajectory_count'],result['call_count']),(24,288));self.assertEqual(result['checks']['raw']['rows'],295)
   self.assertEqual(result['accuracy_failures'],[]);self.assertEqual(result['partition_failures'],[]);self.assertTrue(all(r['passed']for r in result['covariance']))
   budget=result['probes'][0];self.assertFalse(budget['ok']);self.assertEqual(budget['substeps'],2);self.assertEqual(budget['coverage'],.015625)
   self.assertTrue(all(r['returned_exact_caller_parent']and r['recovery_exact_control']for r in result['probes']))
   self.assertTrue(result['adaptive_plateau_evidence']['first_segment_loose_middle_states_identical'])
   self.assertTrue(result['adaptive_plateau_evidence']['first_segment_loose_middle_diagnostics_identical'])
 def test_original_input_corruption_rejects_without_rehashing(self):
  # A changed copy cannot be silently treated as a new original observation.
  with tempfile.TemporaryDirectory()as tmp:
   target=Path(tmp);(target/'native.json').write_text('{}')
   with patch.object(d,'PACKET',target):
    with self.assertRaisesRegex(ValueError,'original input receipt:native.json'):d.build_diagnosis()
 def test_default_artifact_scope_is_receipt_only(self):
  for result in self.fresh['backends']:
   key='preobservation-'+result['backend']+'-build.json'
   self.assertEqual(result['receipts'][key]['artifact_byte_checks'],'receipt binding only; artifacts not reopened')

if __name__=='__main__':unittest.main()
