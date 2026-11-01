"""Complete private material gate: immutable source, history, lab and exact reversal."""
import copy,gzip,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from atlas.model import ROOT,load
from atlas.compiler import generate
P=ROOT/'catalogue/investigations/tresca-certified-corners-v5'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class TrescaCertifiedCornerTests(unittest.TestCase):
 def test_all_original_saved_gates_without_material_execution(self):
  with patch('subprocess.run',side_effect=AssertionError('material calls forbidden')):a=module('v5_verify',P/'verify.py').verify()
  self.assertTrue(a['overall_pass'])
  for b in ['native','wasm']:
   self.assertEqual(a[b]['laboratory']['admissibility_checks'],97);self.assertEqual(a[b]['history']['accepted'],12);self.assertTrue(a[b]['reversal']['qualification_pass'])
 def test_only_identity_and_corner_predicates_change(self):
  old=load(ROOT/'catalogue/investigations/tresca-solution-constraints-v4/frozen/model.json');new=load(P/'frozen/model.json');self.assertEqual({k for k in new if new[k]!=old[k]},{'id','name','description','derived'})
  changed=[(a,b)for a,b in zip(old['derived'],new['derived'])if a!=b];self.assertEqual(len(changed),1);self.assertEqual(changed[0][0]['name'],'branch');self.assertEqual(changed[0][1]['expr'],'select(principal_range_le(trial_dev,width),0,select(principal_centered_mid_gt(trial_dev,width),1,select(principal_centered_mid_gt(-trial_dev,width),2,3)))')
  self.assertFalse((ROOT/'models'/(new['id']+'.json')).exists())
 def test_normal_generation_and_only_two_observation_lines(self):
  with tempfile.TemporaryDirectory()as d:
   generate(d,[P/'frozen/model.json'])
   for n in ['models.hpp','models.json']:self.assertEqual((Path(d)/n).read_bytes(),(P/'generated-original'/n).read_bytes())
  lines=(P/'generated/models.hpp').read_text().splitlines(True);lines=[l for l in lines if l.strip()not in ('inline int study_branch=-1;','study_branch=int(value(branch));')];self.assertEqual(''.join(lines),(P/'generated-original/models.hpp').read_text())
 def test_derivative_history_and_reversal_corruption_rejects(self):
  m=module('v5',P/'assess.py');c=module('v5_c',P/'assess_corpus.py');rows=[json.loads(x)for x in(P/'native-corpus-responses.jsonl').read_text().splitlines()];rows[1]['derivatives'][6][37]+=1
  a=c.assess(rows,json.loads((P/'corpus-requests.json').read_text())['requests'],json.loads(gzip.decompress((ROOT/'docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz').read_bytes())),json.loads((P/'corpus-policy.json').read_text()));self.assertFalse(a['qualification_pass'])
  l=module('v5_l',P/'assess_laboratory.py');rows=[json.loads(x)for x in(P/'native-laboratory-responses.jsonl').read_text().splitlines()];rows[0]['response']['points'].pop();self.assertFalse(l.assess(rows,json.loads((P/'laboratory-inputs.json').read_text()),json.loads((P/'laboratory-references.json').read_text()),json.loads((P/'laboratory-policy.json').read_text()))['qualification_pass'])
  r=json.loads((P/'native-reversal-responses.jsonl').read_text());r['raw_ok']=False;self.assertFalse(m.reversal(r,json.loads((P/'reversal-reference.json').read_text()),ROOT)['qualification_pass'])
 def test_original_failed_assessments_stay_failed(self):
  for name in ['tresca-rounded-backends-v1','tresca-continuous-history-v1','tresca-feasible-domain-v3','tresca-laboratory-v1']:self.assertFalse(json.loads((ROOT/'catalogue/investigations'/name/'assessment.json').read_text())['overall_pass'])
