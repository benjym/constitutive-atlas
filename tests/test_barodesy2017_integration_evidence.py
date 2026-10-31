"""Fresh scalar replay and raw-response corruption checks; no builds/execution."""
import copy,json,tempfile,unittest
from pathlib import Path
from atlas.evidence import verify_manifest_files
from atlas.model import ROOT,all_models
from tools import barodesy2017_integration_study as study
from tools.barodesy2017_transport import audit
PACKET=ROOT/'catalogue/investigations/barodesy2017-integration-v1'
class FiniteEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=verify_manifest_files(ROOT,str((PACKET/'manifest.json').relative_to(ROOT)))
 def test_scope_and_public_exclusion(self):
  self.assertFalse(self.manifest['public_admission']);self.assertFalse(self.manifest['complete_model'])
  self.assertEqual(self.manifest['verified_scope']['trajectories_per_backend'],45)
  self.assertEqual(self.manifest['verified_scope']['chained_updates_per_backend'],459)
  self.assertNotIn(study.read(PACKET/'native.json')['model_definition']['id'],{m['id']for m in all_models()})
 def test_fresh_reference_and_bound_backend_parity(self):
  n=study.read(PACKET/'native.json');w=study.read(PACKET/'wasm.json')
  for report in (n,w):
   result=study.verify(report);self.assertEqual((result['trajectory_count'],result['call_count']),(45,459))
  self.assertLessEqual(study.parity(w,n,PACKET/'native.json'),study.PARITY_BOUND)
  receipt=study.read(PACKET/'build-receipt.json')['files']
  self.assertEqual(n['native_sha256'],receipt['build/atlas_barodesy_solver'])
  self.assertEqual(w['wasm_loader_sha256'],receipt['build-wasm/barodesy-isotropic.js'])
  self.assertEqual(w['wasm_binary_sha256'],receipt['build-wasm/barodesy-isotropic.wasm'])
 def test_all_raw_responses_bind_to_requests(self):
  for backend in ('native','wasm'):
   result=audit(PACKET/(backend+'.json'))
   self.assertEqual(result['raw_rows'],466);self.assertTrue(result['all_requests_responses_bound'])
 def test_corrupt_transport_rejected(self):
  changes={
   'native':[
    lambda r:r.pop(),
    lambda r:r[0].__setitem__('returncode',True),
    lambda r:r[1]['request']['initial'].__setitem__(0,1.),
    lambda r:r[1].__setitem__('stdout','{}'),
    lambda r:r[1]['args'].__setitem__(1,'--describe'),
    lambda r:r[1].__setitem__('returncode',True),
   ],
   'wasm':[
    lambda r:r[0].__setitem__('name','wrong'),
    lambda r:r[1].__setitem__('raw','{}'),
    lambda r:r[1]['args'].__setitem__(1,'NaN'),
    lambda r:r[1]['types'].__setitem__(0,'number'),
   ]}
  with tempfile.TemporaryDirectory()as tmp:
   path=Path(tmp)/'transport.jsonl'
   for backend,mutations in changes.items():
    original=[json.loads(line)for line in(PACKET/(backend+'.transport.jsonl')).read_text().splitlines()]
    for mutation in mutations:
     rows=copy.deepcopy(original);mutation(rows);path.write_text(''.join(json.dumps(row)+'\n'for row in rows))
     with self.subTest(backend=backend,mutation=mutation),self.assertRaises((ValueError,TypeError,KeyError)):
      audit(PACKET/(backend+'.json'),path)
if __name__=='__main__':unittest.main()
