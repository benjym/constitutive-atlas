import hashlib,json,shutil,tempfile,unittest
from pathlib import Path
from tools.build_development import ROOT
from tools.build_reporting_review import PACKET,projection,bundle
class ReportingExportTests(unittest.TestCase):
 def fixture(self):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
  for p in (PACKET,Path('docs/benchmarks/kfs-development-review-v1')):shutil.copytree(ROOT/p,root/p)
  return root
 def test_exact_public_decision_and_scalar_allowlist(self):
  root=self.fixture();out=root/'site';view=projection(root);bundle(out,root)
  self.assertEqual((out/'reporting-review/decision.json').read_bytes(),(root/PACKET/'decision.json').read_bytes())
  self.assertEqual(len(view['claims']),7);self.assertFalse(view['model_admission']);self.assertFalse(view['redistribution_permission'])
  text=json.dumps(view)
  for forbidden in ('"points"','"parameters"','/private/tmp','"state"'):self.assertNotIn(forbidden,text)
 def test_changed_review_or_handoff_rejects_before_output(self):
  for name in (PACKET/'decision.json',Path('docs/benchmarks/kfs-development-review-v1/manifest.json')):
   root=self.fixture();(root/name).write_text('{}')
   with self.assertRaisesRegex(ValueError,'hash mismatch'):bundle(root/'site',root)
   self.assertFalse((root/'site').exists())
 def test_rebound_review_cannot_promote_model_or_omit_claims(self):
  for mutation in ('permission','claims','qualifications'):
   root=self.fixture();p=root/PACKET/'decision.json';d=json.loads(p.read_text())
   if mutation=='permission':d['redistribution_permission']=True
   elif mutation=='claims':d['claim_decisions']=d['claim_decisions'][:-1]
   else:d['mandatory_qualifications']=[]
   p.write_text(json.dumps(d));mp=root/PACKET/'manifest.json';m=json.loads(mp.read_text());m['files'][str(PACKET/'decision.json')]=hashlib.sha256(p.read_bytes()).hexdigest();mp.write_text(json.dumps(m))
   with self.assertRaises(ValueError):projection(root)
