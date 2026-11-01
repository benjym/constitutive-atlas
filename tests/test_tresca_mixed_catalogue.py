"""Compatibility gates reject altered outputs; replay uses saved evidence only."""
import copy,importlib.util,unittest
from unittest.mock import patch
from atlas.model import ROOT
P=ROOT/'catalogue/investigations/tresca-mixed-catalogue-v1'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class MixedCatalogueTests(unittest.TestCase):
 def test_complete_saved_gate_without_build_or_material_execution(self):
  with patch('subprocess.run',side_effect=AssertionError('no execution')):self.assertTrue(module('mixed_saved',P/'verify.py').verify()['overall_pass'])
 def test_existing_model_result_or_failure_state_corruption_rejects(self):
  a=module('mixed_assess',P/'assess.py');rows=a.read(P/'native-old-nine-responses.json')
  changed=copy.deepcopy(rows);changed[0]['response']['points'][-1]['state'][0]+=100
  self.assertFalse(a.compare_old(changed,'native')['qualification_pass'])
  changed=copy.deepcopy(rows);failed=next(r for r in changed if not r['response']['ok']and 'state'in r['response']);failed['response']['state'][0]+=100
  self.assertFalse(a.compare_old(changed,'native')['qualification_pass'])
 def test_total_stress_pore_fabrication_rejects(self):
  a=module('mixed_lab',P/'assess_laboratory.py');read=lambda n:__import__('json').loads((P/n).read_text());rows=read('wasm-laboratory-responses.json');rows[0]['response']['points'][0]['u']=0
  self.assertFalse(a.assess(rows,read('laboratory-inputs.json'),read('laboratory-references.json'),read('laboratory-policy.json'),ROOT)['qualification_pass'])
 def test_history_missing_or_reordered_parent_rejects(self):
  a=module('mixed_history',P/'assess_history.py');read=lambda n:__import__('json').loads((P/n).read_text());rows=read('native-history-responses.json');rows[1]['parent_bits'][0]='18446744073709551615'
  with self.assertRaises(AssertionError):a.assess(rows,read('history-inputs.json'),ROOT)
