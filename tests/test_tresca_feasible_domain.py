"""Feasible physical history cannot hide residual-extension regressions."""
from tests.historical_generation import generate as historical_generate
import copy,importlib.util,json,gzip,tempfile,unittest
from pathlib import Path
from atlas.model import ROOT,load
from atlas.compiler import generate
P=ROOT/'catalogue/investigations/tresca-feasible-domain-v3'
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class TrescaFeasibleDomainTests(unittest.TestCase):
 def test_mixed_saved_result_is_preserved(self):
  a=module('v3_saved_verify',P/'verify.py').verify();self.assertFalse(a['overall_pass'])
  for backend in ['native','wasm']:
   self.assertTrue(a[backend]['history']['qualification_pass']);self.assertEqual(a[backend]['history']['accepted'],12)
   self.assertEqual(a[backend]['history']['value_components'],288)
   self.assertFalse(a[backend]['corpus']['qualification_pass']);self.assertEqual([x['id']for x in a[backend]['corpus']['failures']],['scaled-face--80/double','scaled-face--80/jet'])
 def test_only_domain_and_identity_change_and_normal_generation(self):
  base=json.loads((ROOT/'catalogue/investigations/tresca-pressure-split-v2/frozen/model.json').read_text());new=load(P/'frozen/model.json')
  self.assertEqual({k for k in base if base[k]!=new[k]},{'id','name','description','domain'})
  self.assertEqual(new['domain'],base['domain']+['principal_range_le(sigma,width)'])
  with tempfile.TemporaryDirectory()as d:
   historical_generate(d,[P/'frozen/model.json'],'tresca-feasible-domain-v3')
   for n in ['models.hpp','models.json']:self.assertEqual((Path(d)/n).read_bytes(),(P/'generated-original'/n).read_bytes())
  modified=(P/'generated/models.hpp').read_text();self.assertEqual(modified.replace('\ninline int study_branch=-1;','').replace('study_branch=int(value(branch));\n',''),(P/'generated-original/models.hpp').read_text())
  self.assertFalse((ROOT/'models'/(new['id']+'.json')).exists())
 def test_inventory_keeps_outside_current_extension_probe(self):
  inv=json.loads((P/'current-probe-inventory.json').read_text());self.assertEqual(len(inv['cases']),61);self.assertEqual(inv['outside'],['scaled-face--80'])
  exact=module('v3_inventory_exact',ROOT/'docs/reviews/certified-spectral-range-v1/exact.py');data=json.loads((ROOT/'docs/reviews/tresca-rounded-reference-v1/inputs.json').read_text())
  for row,case in zip(inv['cases'],data['cases']):self.assertEqual(row['current_admissible'],exact.range_le([float.fromhex(v)for v in case['current'][:6]],2*case['parameters']['k']))
 def test_unchanged_subgates_reject_additional_corruption(self):
  c=module('v3_corrupt_corpus',P/'assess_corpus.py');requests=json.loads((P/'corpus-requests.json').read_text())['requests'];reference=json.loads(gzip.decompress((ROOT/'docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz').read_bytes()));policy=json.loads((P/'corpus-policy.json').read_text());rows=[json.loads(l)for l in (P/'native-corpus-responses.jsonl').read_text().splitlines()];rows[1]['derivatives'][0][37]+=1
  a=c.assess(rows,requests,reference,policy);self.assertEqual(len(a['failures']),3);self.assertIn('derivative-accuracy',[x['kind']for x in a['failures']])
  h=module('v3_corrupt_history',P/'assess_history.py');rows=[json.loads(l)for l in (P/'native-history-responses.jsonl').read_text().splitlines()];rows[0]['baseline_recovery']=False
  a=h.assess(rows,json.loads((P/'history-inputs.json').read_text()));self.assertFalse(a['qualification_pass']);self.assertIn('baseline-recovery',[x['kind']for x in a['failures']])
