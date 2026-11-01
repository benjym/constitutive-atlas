"""Synthetic corruption tests; no candidate integrations or scientific claims."""
import importlib.util,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OLD=ROOT/'docs/reviews/gis2024-v03-backends-v1'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assess=mod('assess',HERE/'assess_gis.py');sys.modules['assess']=assess
sys.modules['driver']=mod('driver',OLD/'driver.py')
old=mod('isolated_qualification_tests',OLD/'test_qualification.py')
AssessorTests=old.AssessorTests;TransportTests=old.TransportTests
class MixedCatalogueTests(old.AssessorTests):
 # Inherit the 19 original corruption tests with genuine mixed descriptors.
 def setUp(self):
  super().setUp();self.catalogue=assess.load(HERE/'generated-eleven/models.json')['models'];cat=assess.digest(self.catalogue)
  for d in self.f.data['descriptors']:
   d['descriptor']={'models':self.catalogue,'sha256':cat};p=self.f.directory/'receipts'/f"{d['receipt']:04d}.json";r=assess.load(p);r['stdout']=json.dumps(d['descriptor'])+'\n';p.write_text(json.dumps(r))
  for row in self.f.data['rows']:
   for key in ['calls','restart_same','restart_fresh']:
    for item in row[key]:item['response']['catalogue_hash']=cat;self.f.sync(item)
  for item in [self.f.data['control']]+[i[k]for i in self.f.data['probes']for k in ['call','recovery']]:
   if 'catalogue_hash'in item['response']:item['response']['catalogue_hash']=cat;self.f.sync(item)
  self.f.assess=lambda:assess.audit(self.f.data,self.f.directory,self.f.model,self.f.rows,self.f.probes,self.f.policy,self.f.reference,self.catalogue)
 def test_missing_existing_model(self):
  self.catalogue.pop(0);self.assertRaisesRegex(ValueError,'catalogue identity',self.f.assess)
 def test_reordered_existing_models(self):
  self.catalogue[0],self.catalogue[1]=self.catalogue[1],self.catalogue[0];self.assertRaisesRegex(ValueError,'catalogue identity',self.f.assess)
 def test_changed_existing_model(self):
  import copy
  self.catalogue[0]=copy.deepcopy(self.catalogue[0]);self.catalogue[0]['name']+=' changed';self.assertRaisesRegex(ValueError,'catalogue identity',self.f.assess)
 def test_duplicate_candidate(self):
  self.catalogue.append(self.f.model);self.assertRaisesRegex(ValueError,'candidate membership',self.f.assess)
class RegressionTests(unittest.TestCase):
 def test_regression_and_poison(self):
  a=mod('existing_assessor',HERE/'assess_existing.py');rows=a.read(HERE/'old-nine-baseline-responses.json');cat=a.read(HERE/'generated-eleven/models.json')['sha256']
  def rewrite(v):
   if isinstance(v,dict):
    for k in v:
     if k=='catalogue_hash':v[k]=cat
     else:rewrite(v[k])
   elif isinstance(v,list):
    for x in v:rewrite(x)
  rewrite(rows);self.assertTrue(a.compare_old(rows,'native')['qualification_pass']);rows[0]['response']['points'][0]['state'][0]+=10;self.assertFalse(a.compare_old(rows,'native')['qualification_pass'])
if __name__=='__main__':unittest.main()
