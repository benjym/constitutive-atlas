"""Complete residual and physical-history qualification through the common API."""
import copy,importlib.util,json,gzip,tempfile,unittest
from pathlib import Path
from atlas.model import ROOT,load
from atlas.compiler import generate
P=ROOT/'catalogue/investigations/tresca-solution-constraints-v4'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class TrescaSolutionConstraintTests(unittest.TestCase):
 def test_complete_saved_gates_and_generic_failure_checks(self):
  a=module('v4_verify',P/'verify.py').verify();self.assertTrue(a['overall_pass'])
  for b in ['native','wasm']:
   self.assertTrue(a[b]['corpus']['qualification_pass']);self.assertEqual(a[b]['corpus']['derivative_components'],27816)
   self.assertTrue(a[b]['history']['qualification_pass']);self.assertEqual(a[b]['history']['accepted'],12)
   self.assertEqual(a[b]['checks'],{'pass':True,'raw_extension_ok':True,'invalid_physical_rejected':True,'nonfinite_rejections':48,'seed_rejections':1368})
 def test_candidate_and_normal_generation(self):
  old=load(ROOT/'catalogue/investigations/tresca-pressure-split-v2/frozen/model.json');new=load(P/'frozen/model.json')
  self.assertEqual({k for k in new if old.get(k)!=new[k]},{'id','name','description','solution_constraints'})
  self.assertEqual(new['solution_constraints'],['principal_range_le(sigma,2*k)']);self.assertEqual(old['domain'],new['domain'])
  with tempfile.TemporaryDirectory()as d:
   generate(d,[P/'frozen/model.json'])
   for n in ['models.hpp','models.json']:self.assertEqual((Path(d)/n).read_bytes(),(P/'generated-original'/n).read_bytes())
  self.assertFalse((ROOT/'models'/(new['id']+'.json')).exists())
 def test_full_column_and_history_recovery_corruption_rejected(self):
  c=module('v4_corpus',P/'assess_corpus.py');rows=[json.loads(l)for l in (P/'native-corpus-responses.jsonl').read_text().splitlines()];rows[1]['derivatives'][6][37]+=1
  a=c.assess(rows,json.loads((P/'corpus-requests.json').read_text())['requests'],json.loads(gzip.decompress((ROOT/'docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz').read_bytes())),json.loads((P/'corpus-policy.json').read_text()));self.assertFalse(a['qualification_pass'])
  h=module('v4_history',P/'assess_history.py');rows=[json.loads(l)for l in (P/'native-history-responses.jsonl').read_text().splitlines()];rows[0]['baseline_recovery']=False
  self.assertFalse(h.assess(rows,json.loads((P/'history-inputs.json').read_text()))['qualification_pass'])
 def test_prior_mixed_and_failed_studies_stay_unqualified(self):
  for name in ['tresca-feasible-domain-v3','tresca-continuous-history-v1','tresca-rounded-backends-v1']:
   self.assertFalse(json.loads((ROOT/'catalogue/investigations'/name/'assessment.json').read_text())['overall_pass'])
