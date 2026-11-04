"""Complete one-step/restart qualification stays distinct from admission."""
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,tempfile,unittest
from atlas.model import ROOT,load
from atlas.compiler import generate
P=ROOT/'catalogue/investigations/tresca-pressure-split-v2'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class TrescaPressureSplitBackendsTests(unittest.TestCase):
 def test_saved_complete_gate_without_material_execution(self):
  result=module('tresca_v2_verify',P/'verify.py').verify()
  self.assertTrue(result['overall_pass'])
  for backend in ('native','wasm'):
   self.assertEqual(result[backend]['requests'],219);self.assertEqual(result[backend]['derivative_components'],27816)
   self.assertEqual(result[backend]['failures'],[]);self.assertEqual(result[backend]['coverage_gaps'],[])
 def test_original_corpus_and_generated_candidate_identity(self):
  base=json.loads((ROOT/'docs/reviews/tresca-pressure-split-v1/model.json').read_text());candidate=load(P/'frozen/model.json')
  changed={k for k in base if base[k]!=candidate[k]};self.assertEqual(changed,{'id','name','description','initial_checks','derived'})
  self.assertEqual(candidate['initial_checks'],['principal_range_le(sigma,width)'])
  for old,new in zip(base['derived'],candidate['derived']):
   if old['name']=='branch':self.assertEqual(new['expr'],old['expr'].replace('vmax-vmin<=width','principal_range_le(trial_dev,width)'))
   else:self.assertEqual(old,new)
  with tempfile.TemporaryDirectory()as d:
   generate(d,[P/'frozen/model.json'])
   for n in ('models.hpp','models.json'):self.assertEqual((Path(d)/n).read_bytes(),(P/'generated-original'/n).read_bytes())
  self.assertFalse((ROOT/'models'/(candidate['id']+'.json')).exists())
 def test_assessor_rejects_values_all38_columns_membership_and_rollback_corruption(self):
  m=module('tresca_v2_assess',P/'assess.py');requests=json.loads((P/'requests.json').read_text())['requests'];reference=json.loads(gzip.decompress((ROOT/'docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz').read_bytes()));policy=json.loads((P/'policy.json').read_text());original=[json.loads(l)for l in (P/'native-responses.jsonl').read_text().splitlines()]
  for kind in ('value','derivative','initial','rollback','recovery','branch'):
   rows=copy.deepcopy(original)
   if kind=='value':rows[0]['values'][0]+=1
   elif kind=='derivative':rows[1]['derivatives'][6][37]+=1
   elif kind=='initial':next(row for row in rows if row['id']=='history-restart/7')['ok']=True
   elif kind=='rollback':next(row for row in rows if row['mode']=='transaction')['returned_parent']=False
   elif kind=='recovery':rows[0]['baseline_recovery']=False
   else:next(row for row in rows if row['id']=='dense-yield/jet')['branch']=0
   with self.subTest(kind=kind):self.assertFalse(m.assess(rows,requests,reference,policy)['qualification_pass'])
 def test_original_failed_gate_is_retained(self):
  old=json.loads((ROOT/'catalogue/investigations/tresca-rounded-backends-v1/assessment.json').read_text());self.assertFalse(old['overall_pass'])
  for backend in ('native','wasm'):
   rows={row['id']:row for row in map(json.loads,(P/(backend+'-responses.jsonl')).read_text().splitlines())}
   self.assertEqual(rows['near-isolation-upper/solve']['values'][6:9],[.625,.25,-.625]);self.assertEqual(rows['dense-yield/jet']['branch'],3)
   self.assertFalse(rows['history-restart/7']['ok']);self.assertTrue(rows['transaction/iteration-budget']['tentative_changed']);self.assertTrue(rows['transaction/iteration-budget']['returned_parent'])
