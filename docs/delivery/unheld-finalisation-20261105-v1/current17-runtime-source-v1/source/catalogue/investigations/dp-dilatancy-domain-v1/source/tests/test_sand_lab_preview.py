"""Source identity, explicit initialization and frozen sand-preview integration."""
import hashlib,json,unittest
from pathlib import Path
from atlas.model import ROOT,load,defaults
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError

class SandLabPreview(unittest.TestCase):
 def test_root_draft_matches_frozen_tested_definition(self):
  model=ROOT/'models/barodesy-sand.json';study=ROOT/'catalogue/investigations/barodesy2015-preview-v1'
  self.assertEqual(model.read_bytes(),(study/'models/barodesy-sand.json').read_bytes())
  current=load(model);rate=load(ROOT/'catalogue/investigations/barodesy2015-rates-v2/model.json')
  for key in ('equations','derived','domain','parameters','state','formulation','initialization'):
   self.assertEqual(current[key],rate[key],key)
  self.assertEqual(current['status'],'draft');self.assertEqual(current['schema_version'],'0.3')
  urls={s['url']for s in current['sources']}
  self.assertTrue({'https://doi.org/10.1680/geot.14.P.151','https://doi.org/10.1002/nag.2984'}<=urls)
 def test_explicit_state_and_restricted_domain(self):
  model=load(ROOT/'models/barodesy-sand.json');p=defaults(model);sigma=[100000,100000,100000,0,0,0]
  self.assertEqual(initialize_state(model,{'sigma':sigma,'e':.75},p)['initial'],sigma+[.75])
  for state in ({'sigma':sigma},{'sigma':[0]*6,'e':.75},{'sigma':sigma,'e':.35}):
   with self.assertRaises(ValidationError):initialize_state(model,state,p)
 def test_catalogue_selection_preserves_six_existing_definitions(self):
  folder=ROOT/'catalogue/investigations/barodesy2015-preview-v1'
  for p in(folder/'models').glob('*.json'):
   self.assertEqual(p.read_bytes(),(ROOT/'models'/p.name).read_bytes(),p.name)
  catalogue=json.loads((ROOT/'catalogue/manifest.json').read_text())['models']
  self.assertEqual(len(catalogue),32);entry=next(m for m in catalogue if m['id']=='barodesy-sand')
  self.assertIs(entry['executable'],True);self.assertEqual(entry['status'],'draft')
  self.assertEqual(len(list((folder/'models').glob('*.json'))),7)
 def test_frozen_assessor_rejects_corrupt_outputs_after_raw_rebinding(self):
  import importlib.util,shutil,tempfile
  study=ROOT/'catalogue/investigations/barodesy2015-preview-v1'
  spec=importlib.util.spec_from_file_location('sand_preview_assessor',study/'assess.py')
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  self.assertTrue(module.assess()['pass'])
  for change in ('status','volume','parity','missing','duplicate'):
   with self.subTest(change=change),tempfile.TemporaryDirectory() as temp:
    copied=Path(temp)/'study';shutil.copytree(study,copied)
    path=copied/'wasm/journal.json';rows=json.loads(path.read_text())
    if change=='missing':rows.pop()
    else:
     response=json.loads(rows[1]['raw'])
     if change=='status':response.update(ok=False,message='synthetic failure')
     if change=='volume':response['points'][1]['state'][6]+=.01
     if change=='parity':response['points'][1]['state'][3]+=.001
     rows[1]['raw']=json.dumps(response)
     if change=='duplicate':rows[1]['raw']='{"ok":false,'+rows[1]['raw'][1:]
    path.write_text(json.dumps(rows)+'\n')
    receipt=copied/'wasm/receipt.json';doc=json.loads(receipt.read_text());doc['journal_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();receipt.write_text(json.dumps(doc)+'\n')
    if change=='duplicate':
     with self.assertRaisesRegex(ValueError,'duplicate'):module.assess(copied)
    else:self.assertFalse(module.assess(copied)['pass'])
