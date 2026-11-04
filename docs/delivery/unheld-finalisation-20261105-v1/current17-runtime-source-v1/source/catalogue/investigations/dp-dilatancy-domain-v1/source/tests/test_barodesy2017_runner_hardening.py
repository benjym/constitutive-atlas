"""Pure Python runner hardening; subprocess is mocked, never executed."""
import copy,json,pathlib,tempfile,types,unittest
from unittest.mock import patch
from atlas.model import ROOT
from tools import barodesy2017_rate_study as s
class Hardened(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  # Also permits a staging overlay without copying any repository files.
  s.ROOT=ROOT;s.MODEL=ROOT/'models/research/barodesy2017/body-zero-spin.json';s.REFERENCE=ROOT/'catalogue/investigations/barodesy2017-rates-v1/reference.json'
  cls.m,cls.h=s.catalogue();cls.report=s.collect(lambda w:s.python_call(w,cls.m,cls.h),'python')
 def test_fresh_and_support_corpus(self):
  a=s.assess(self.report);self.assertEqual(a['cases'],111);self.assertEqual(a['support_cases'],3);self.assertEqual(a['invalids'],16);self.assertTrue(a['fresh_reference_verified']);self.assertLessEqual(a['maximum_void_closure_ulps'],4)
 def test_forged_reference_recomputed(self):
  ref=s.read(s.REFERENCE);ref['cases'][0]['oracle']['sigma_rhs'][0]=0.
  with patch.object(s,'read',return_value=ref),self.assertRaises(ValueError):s.reference()
 def test_perchannel_corruptions(self):
  # Changes remain tiny compared with large stress rates, but violate channel policy.
  for mutate in (lambda r:r['records'][0]['response']['values'].__setitem__(3,1e-30),lambda r:r['records'][0]['response']['values'].__setitem__(6,r['records'][0]['response']['values'][6]+1e-10),lambda r:r['support_records'][0]['response']['values'].__setitem__(0,1.),lambda r:r['support_records'].pop(),lambda r:r['invalid_records'].pop()):
   r=copy.deepcopy(self.report);mutate(r)
   with self.assertRaises(ValueError):s.assess(r)
 def test_artifact_structure_always_checked(self):
  for artifacts in ([{'path':'missing','sha256':'x'}],[{'path':True,'sha256':'0'*64}],[{'path':'missing','sha256':'0'*64,'extra':1}]):
   r=copy.deepcopy(self.report);r.update(backend='native',artifacts=artifacts)
   with self.assertRaises(ValueError):s.assess(r,check_artifacts=False)
  r=copy.deepcopy(self.report);r.update(backend='native',artifacts=[{'path':'unavailable-native','sha256':'0'*64}]);self.assertFalse(s.assess(r,check_artifacts=False)['artifacts_verified_now'])
 def test_portable_native_override(self):
  with tempfile.TemporaryDirectory()as tmp:
   native=copy.deepcopy(self.report);native.update(backend='native',artifacts=[{'path':'unavailable-native','sha256':'0'*64}]);p=pathlib.Path(tmp)/'native.json';s.write_report(p,native)
   wasm=copy.deepcopy(native);wasm.update(backend='wasm',artifacts=[{'path':'unavailable-js','sha256':'1'*64},{'path':'unavailable-wasm','sha256':'2'*64}],native_report_path='/missing/old/location.json',native_report_sha256=s.sha(p),maximum_native_parity=0.)
   self.assertEqual(s.assess(wasm,check_artifacts=False,native_report_path=p)['support_cases'],3)
   wasm['native_report_sha256']='0'*64
   with self.assertRaises(ValueError):s.assess(wasm,check_artifacts=False,native_report_path=p)
 def test_raw_checkpoint_before_collector_failure(self):
  snapshots=[];calls=0
  def call(req):
   nonlocal calls;calls+=1
   if calls==2:raise ValueError('simulated backend failure')
   return s.python_call(req,self.m,self.h)
  with self.assertRaises(ValueError):s.collect(call,'python',checkpoint=lambda r:snapshots.append(copy.deepcopy(r)))
  self.assertIn('response',snapshots[-1]['records'][0]);self.assertNotIn('response',snapshots[-1]['records'][1])
 def test_transport_saved_before_exit_status_rejection(self):
  with tempfile.TemporaryDirectory()as tmp:
   binary=pathlib.Path(tmp)/'fake';binary.write_bytes(b'not executable');transport=pathlib.Path(tmp)/'transport.jsonl';checkpoints=[]
   req=s.wire(s.reference()['cases'][0],self.m);good=s.python_call(req,self.m,self.h)
   responses=[types.SimpleNamespace(returncode=0,stdout=json.dumps({'sha256':self.h,'models':[self.m]}),stderr=''),types.SimpleNamespace(returncode=1,stdout=json.dumps(good),stderr='')]
   with patch.object(s.subprocess,'run',side_effect=responses),self.assertRaisesRegex(ValueError,'exit status'):
    s.native_report(binary,lambda r:checkpoints.append(copy.deepcopy(r)),transport)
   self.assertEqual(len(transport.read_text().splitlines()),2);self.assertEqual(checkpoints[-1]['records'][0]['request'],req)
if __name__=='__main__':unittest.main()
