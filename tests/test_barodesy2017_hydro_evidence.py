"""Retained exact-hydro analytic replay and raw transport corruption checks."""
import copy,json,tempfile,unittest
from pathlib import Path
from atlas.evidence import verify_manifest_files
from atlas.model import ROOT,all_models
from tools import barodesy2017_hydro_ad as h
from tools.barodesy2017_hydro_transport import audit
PACKET=ROOT/'catalogue/investigations/barodesy2017-hydro-ad-v1'
class HydroEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.manifest=verify_manifest_files(ROOT,str((PACKET/'manifest.json').relative_to(ROOT)))
 def test_bounded_scope_and_source_identity(self):
  self.assertFalse(self.manifest['public_admission']);self.assertFalse(self.manifest['complete_model'])
  self.assertEqual(self.manifest['verified_scope']['exact_hydro_cases'],36)
  self.assertEqual(self.manifest['verified_scope']['invalid_recovery_pairs'],48)
  self.assertNotIn(h.rate.read(PACKET/'native.json')['model_definition']['id'],{m['id']for m in all_models()})
 def test_fresh_analytic_replay_and_bound_parity(self):
  self.assertEqual(h.verify_frozen(),36)
  n=h.rate.read(PACKET/'native.json');w=h.rate.read(PACKET/'wasm.json')
  for report in(n,w):
   result=h.assess(report,False,native_report_path=PACKET/'native.json');self.assertTrue(result['exact_hydro_AD_validated']);self.assertFalse(result['artifacts_verified_now']);self.assertFalse(result['near_hydro_AD'])
  receipt=h.rate.read(PACKET/'build-receipt.json')['files']
  self.assertEqual(n['artifacts'][0]['sha256'],receipt['build/atlas_barodesy_hydro_ad_probe'])
  self.assertEqual(w['artifacts'][0]['sha256'],receipt['build-wasm/barodesy-hydro-ad.js'])
  self.assertEqual(w['artifacts'][1]['sha256'],receipt['build-wasm/barodesy-hydro-ad.wasm'])
 def test_complete_persistent_transport(self):
  for b in('native','wasm'):
   result=audit(PACKET/(b+'.json'));self.assertEqual(result['raw_calls'],133);self.assertTrue(result['all_arguments_responses_bound'])
 def test_transport_corruptions(self):
  changes={
   'native':[
    lambda t:t.__setitem__('returncode',True),
    lambda t:t['request_lines'].pop(),
    lambda t:t['request_lines'].__setitem__(1,t['request_lines'][1].replace('120000.0','1.0')),
    lambda t:t.__setitem__('stdout',t['stdout'].replace('"ok":true','"ok":false',1)),
   ],
   'wasm':[
    lambda t:t['calls'].pop(),
    lambda t:t['calls'][1].__setitem__('name','wrong'),
    lambda t:t['calls'][1]['arguments'].__setitem__(1,'NaN'),
    lambda t:t['calls'][1].__setitem__('raw','{}'),
   ]}
  with tempfile.TemporaryDirectory()as tmp:
   path=Path(tmp)/'transport.json'
   for backend,mutations in changes.items():
    original=h.rate.read(PACKET/(backend+'.json.transport.json'))
    for mutate in mutations:
     t=copy.deepcopy(original);mutate(t);path.write_text(json.dumps(t))
     with self.subTest(backend=backend,mutation=mutate),self.assertRaises((ValueError,TypeError,KeyError)):
      audit(PACKET/(backend+'.json'),path)
if __name__=='__main__':unittest.main()
