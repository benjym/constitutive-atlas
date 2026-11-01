"""Verify limited clay draft identity, preserved failures and frozen acceptance."""
from tests.historical_sources import preserved_model
import unittest,json,importlib.util,hashlib,shutil,tempfile
from pathlib import Path
from atlas.model import ROOT,load,defaults
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError
S=ROOT/'catalogue/investigations/clay2013-preview-v2'
def assessor():
 spec=importlib.util.spec_from_file_location('clay2013_preview_v2',S/'assess.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class Clay2013LaboratoryPreview(unittest.TestCase):
 def test_draft_preserves_tested_math_and_source_identity(self):
  p=ROOT/'models/hypoplastic-clay-2013.json';self.assertEqual(p.read_bytes(),(S/'models/hypoplastic-clay-2013.json').read_bytes())
  m=load(p);old=load(ROOT/'models/research/clay2013/hypoplastic-clay-2013-research.json')
  for k in ['equations','derived','domain','parameters']:self.assertEqual(m[k],old[k])
  self.assertEqual(m['schema_version'],'0.3');self.assertEqual(m['status'],'draft')
  self.assertIn('https://doi.org/10.1007/s11440-012-0199-y',{x['url']for x in m['sources']})
  self.assertEqual(m['initialization']['default_policy'],'examples_only')
  self.assertEqual(initialize_state(m,{'sigma':[10000]*3+[0]*3,'e':.8},defaults(m))['initial'],[10000]*3+[0]*3+[.8])
  for state in [{'sigma':[10000]*3+[0]*3},{'sigma':[-10000,10000,10000,0,0,0],'e':.8}]:
   with self.assertRaises(ValidationError):initialize_state(m,state,defaults(m))
 def test_frozen_v2_pass_and_v1_failure_remain_distinct(self):
  m=assessor();actual=m.assess();self.assertTrue(actual['pass'],actual['errors']);self.assertEqual(actual,json.loads((S/'assessment.json').read_text()))
  self.assertEqual(actual['requests_per_backend'],20);self.assertFalse(actual['scientific_admission'])
  old=json.loads((S.parent/'clay2013-preview-v1/assessment.json').read_text());self.assertFalse(old['pass']);self.assertEqual(len(old['errors']),4)
  requests=json.loads((S/'requests.json').read_text());default=next(x for x in requests if x['id']=='actual-consumer-default');legacy=next(x for x in requests if x['id']=='legacy-100kPa-drained-incompatible')
  self.assertTrue(default['initial'].startswith('10000,10000,10000,'));self.assertTrue(legacy['initial'].startswith('100000,100000,100000,'));self.assertIs(legacy['expected_ok'],False)
 def test_existing_definitions_and_catalogue_entries_are_preserved(self):
  for p in(S/'models').glob('*.json'):self.assertEqual(p.read_bytes(),preserved_model(ROOT,p.name))
  rows=json.loads((ROOT/'catalogue/manifest.json').read_text())['models'];self.assertEqual(len(rows),32)
  entry=next(x for x in rows if x['id']=='hypoplastic-clay-2013');self.assertIs(entry['executable'],True);self.assertEqual(entry['status'],'draft')
 def test_assessor_rejects_corrupt_success_and_failed_transaction_after_rebinding(self):
  m=assessor()
  for change in ['volume','parity','lost_failed_state','false_failed_status']:
   with self.subTest(change=change),tempfile.TemporaryDirectory() as temp:
    target=Path(temp)/'study';shutil.copytree(S,target);p=target/'wasm/journal.json';rows=json.loads(p.read_text());case='legacy-100kPa-drained-incompatible'if change.startswith(('lost','false'))else'actual-consumer-default';row=next(x for x in rows if x['id']==case);doc=json.loads(row['raw'])
    if change=='volume':doc['points'][1]['state'][6]+=.01
    if change=='parity':doc['points'][1]['state'][3]+=.001
    if change=='lost_failed_state':doc['points'][0]['state'][0]+=1
    if change=='false_failed_status':doc['ok']=True
    row['raw']=json.dumps(doc);p.write_text(json.dumps(rows)+'\n');receipt=target/'wasm/receipt.json';d=json.loads(receipt.read_text());d['journal_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();receipt.write_text(json.dumps(d)+'\n')
    self.assertFalse(m.assess(target)['pass'])
