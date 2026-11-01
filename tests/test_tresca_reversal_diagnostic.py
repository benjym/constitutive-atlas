"""Reopen exact-source diagnostic without building or running a material solver."""
import copy,json,importlib.util,unittest
from unittest.mock import patch
from atlas.model import ROOT
P=ROOT/'catalogue/investigations/tresca-reversal-diagnostic-v1'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class TrescaReversalDiagnosticTests(unittest.TestCase):
 def test_saved_cause_with_material_execution_denied(self):
  with patch('subprocess.run',side_effect=AssertionError('material calls forbidden')):a=module('trace_verify',P/'verify.py').verify()
  for b in ['native','wasm']:self.assertTrue(a[b]['initial_raw_jacobian_failed']);self.assertEqual(a[b]['newton_corrections'],0);self.assertEqual(a[b]['backtracking_trials'],0)
 def test_instrumentation_removal_recovers_exact_sources(self):
  self.assertEqual(len(module('trace_recovery',P/'check_instrumentation.py').check()),22)
 def test_branch_trace_and_rollback_corruptions_reject(self):
  m=module('trace_a',P/'assess.py');original=json.loads((P/'native-response.json').read_text());inputs=json.loads((P/'inputs.json').read_text());ref=json.loads((P/'rounded-reference.json').read_text())
  for change in ['branch','tensor','baseline','recovery']:
   r=copy.deepcopy(original)
   if change=='branch':r['derived'][-1]['branch']=2
   elif change=='tensor':r['derived'][-1]['trial'][0]+=1e-4
   elif change=='baseline':r['baseline']['state'][6]+=1e-4
   else:r['recovery']=False
   with self.subTest(change=change),self.assertRaises(AssertionError):m.assess(r,inputs,ref)
 def test_reference_exposes_exact_vs_rounded_predicate_disagreement(self):
  from fractions import Fraction as F
  ref=module('trace_r',P/'reference.py').run(json.loads((P/'inputs.json').read_text()))
  self.assertEqual(F(ref['trial_range_exact'])-16,F(1,2**49));self.assertEqual(ref['three_vmid'],ref['trace_minus_width']);self.assertFalse(ref['projector_min_unique'])
