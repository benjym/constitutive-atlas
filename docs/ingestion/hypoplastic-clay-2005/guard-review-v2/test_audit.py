import json,os,unittest
from pathlib import Path
import audit
HERE=Path(__file__).resolve().parent

def repository():
 if os.environ.get('ATLAS_REVIEW_REPO'):return Path(os.environ['ATLAS_REVIEW_REPO'])
 return next(p for p in HERE.parents if(p/'atlas/model.py').is_file())
class IndependentGuardAudit(unittest.TestCase):
 def test_fresh_replay_and_complete_groups(self):
  r=audit.run(repository());self.assertEqual(r,json.loads((HERE/'results.json').read_text()));self.assertEqual(len(r['adversarial_guard_cases']),91);self.assertEqual(len(r['independent_isotropic_NCL']),9)
 def test_reviewed_exact_bytes(self):
  repo=repository();pins=json.loads((HERE/'reviewed-inputs.json').read_text())
  for n,h in pins['files'].items():self.assertEqual(audit.sha(repo/n),h,n)
 def test_corpus_roles_and_raw_count(self):
  r=json.loads((HERE/'results.json').read_text());self.assertEqual([r[k]for k in ('frozen_accuracy_count','frozen_support_count','frozen_support_accepted_finite_only','frozen_support_rejections','frozen_numeric_invalids','proposed_raw_rows')],[41,29,10,19,10,110]);self.assertFalse(r['compiled_execution']);self.assertFalse(r['admission'])
 def test_not_global_float_scale_invariance(self):
  r=json.loads((HERE/'results.json').read_text());different=[x['scale']for x in r['finite_regime_cases']if x['finite_domain_difference']];self.assertEqual(different,[1e-300,1e-200,1e200,1e300])
if __name__=='__main__':unittest.main()
