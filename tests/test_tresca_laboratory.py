"""Saved-only laboratory corpus and independent reference checks; no builds."""
from pathlib import Path
import copy,json,importlib.util,unittest
from unittest.mock import patch
from atlas.model import ROOT,load
P=ROOT/'catalogue/investigations/tresca-laboratory-v1'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class TrescaLaboratoryTests(unittest.TestCase):
 def test_frozen_evidence_keeps_failed_gate_with_execution_denied(self):
  with patch('subprocess.run',side_effect=AssertionError('material execution forbidden')):a=module('lab_verify',P/'verify.py').verify()
  self.assertFalse(a['overall_pass']);self.assertEqual(a['native']['failures'],a['wasm']['failures'])
 def test_unchanged_model_and_full_protocol_references(self):
  self.assertEqual((P/'frozen/model.json').read_bytes(),(ROOT/'catalogue/investigations/tresca-solution-constraints-v4/frozen/model.json').read_bytes())
  inputs=json.loads((P/'inputs.json').read_text());refs=module('lab_ref',P/'reference.py').generate(inputs)
  self.assertEqual(refs,json.loads((P/'references.json').read_text()));self.assertEqual(sum(r['exact_hooke_certificates']for r in refs.values()),510)
  self.assertEqual({c['protocol']for c in inputs['cases']if c['kind']=='success'},set(range(5)));self.assertEqual(refs['unattainable-stress-prefix']['failure_step'],4)
 def test_full_history_pore_controls_and_recovery_corruptions_add_failures(self):
  m=module('lab_assess',P/'assess.py');inputs=json.loads((P/'inputs.json').read_text());refs=json.loads((P/'references.json').read_text());policy=json.loads((P/'policy.json').read_text());original=[json.loads(l)for l in(P/'native-responses.jsonl').read_text().splitlines()]
  for change in ['plastic','strain','pore','controls','recovery','point']:
   rows=copy.deepcopy(original);r=rows[1]['response']
   if change=='plastic':r['points'][3]['state'][9]+=1e-4
   elif change=='strain':r['points'][3]['strain'][2]+=1e-4
   elif change=='pore':r['points'][3]['u']=0
   elif change=='controls':r['loading']['controls_bits'][1]='0'*16
   elif change=='recovery':rows[1]['recovery']['points'][1]['state'][6]=1e-3
   else:r['points'].pop()
   with self.subTest(change=change):self.assertGreater(len(m.assess(rows,inputs,refs,policy)['failures']),2)
 def test_failed_reversal_has_exact_admissible_solution(self):
  d=module('lab_diag',P/'diagnose.py').run()
  for b in ['native','wasm']:
   self.assertEqual(d['backends'][b]['old_q'],'-16');self.assertEqual(d['backends'][b]['trial_q'],'16');self.assertTrue(d['backends'][b]['nearest_solution_source_admissible']);self.assertTrue(d['backends'][b]['plastic_increment_exactly_zero'])
