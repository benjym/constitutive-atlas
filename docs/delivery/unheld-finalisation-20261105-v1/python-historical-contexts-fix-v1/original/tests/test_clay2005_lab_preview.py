"""Ninth draft identity, explicit inputs, preserved catalogue and frozen preview gates."""
from tests.historical_generation import catalogue as historical_catalogue
from tests.historical_sources import preserved_model
import importlib.util,json,unittest
from pathlib import Path
from atlas.model import ROOT,load,defaults
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError
from atlas.evidence import checked_receipt
S=ROOT/'catalogue/investigations/clay2005-preview-v1';I=ROOT/'docs/reviews/nine-model-lab-integration'
class Clay2005LabPreview(unittest.TestCase):
 def test_exact_frozen_candidate_and_source_math(self):
  path=ROOT/'models/hypoplastic-clay-2005.json';self.assertEqual(path.read_bytes(),(S/'models'/path.name).read_bytes())
  model=load(path);research=load(ROOT/'catalogue/investigations/clay2005-homogeneous-rates-v1/model.json')
  for key in research:
   if key not in ('id','name','description','sources'):self.assertEqual(model[key],research[key],key)
  self.assertEqual(model['status'],'draft');self.assertEqual(model['schema_version'],'0.3');self.assertIn('https://doi.org/10.1002/nag.416',{s['url']for s in model['sources']})
 def test_explicit_initialization_and_domain_rejection(self):
  m=load(ROOT/'models/hypoplastic-clay-2005.json');p=defaults(m);sigma=[100000]*3+[0]*3
  self.assertEqual(initialize_state(m,{'sigma':sigma,'e':.8},p)['initial'],sigma+[.8])
  for state in ({'sigma':sigma},{'sigma':[0]*6,'e':.8},{'sigma':sigma,'e':-.1}):
   with self.assertRaises(ValidationError):initialize_state(m,state,p)
 def test_catalogue_and_prior_models_preserved(self):
  prior=json.loads((I/'prior-models.json').read_text())
  import hashlib
  for name,pin in prior.items():self.assertEqual(hashlib.sha256(preserved_model(ROOT,Path(name).name)).hexdigest(),pin)
  before=json.loads((I/'prior-catalogue.json').read_text())['models'];after=historical_catalogue('clay2005')['models'];self.assertEqual(len(after),32)
  for old,new in zip(before,after):
   if old['id']!='hypoplastic-clay-2005':self.assertEqual(old,new)
   else:self.assertIs(new['executable'],True);self.assertEqual(new['status'],'draft')
  receipt=json.loads((I/'historical-catalogue-archive.json').read_text());snapshot=checked_receipt(ROOT,str((I/'historical-catalogue-archive.json').relative_to(ROOT)),'catalogue/manifest.json',receipt['sha256']);self.assertEqual(snapshot.read_bytes(),(I/'prior-catalogue.json').read_bytes())
 def test_retained_finite_and_browser_gates(self):
  import sys
  sys.path.insert(0,str(S))
  try:
   spec=importlib.util.spec_from_file_location('clay2005_preview',S/'assess.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);result=m.assess()
  finally:sys.path.remove(str(S))
  self.assertTrue(result['pass'],result['errors']);self.assertEqual(result,json.loads((S/'assessment.json').read_text()));self.assertEqual(result['requests_per_backend'],27);self.assertFalse(result['scientific_admission']);self.assertTrue(json.loads((S/'browser/comparison.json').read_text())['pass'])
if __name__=='__main__':unittest.main()
