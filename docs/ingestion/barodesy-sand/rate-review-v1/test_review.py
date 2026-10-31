import json,os,unittest
from pathlib import Path
import audit
HERE=Path(__file__).resolve().parent


class RetainedReview(unittest.TestCase):
    def test_fresh_readonly_diagnostics(self):
        configured=os.environ.get('ATLAS_REVIEW_REPO')
        repo=Path(configured)if configured else next((p for p in HERE.parents if(p/'atlas/model.py').is_file()),None)
        self.assertIsNotNone(repo,'Set ATLAS_REVIEW_REPO for a staged packet')
        self.assertEqual(audit.run(repo),json.loads((HERE/'findings.json').read_text()))

    def test_cancellation_is_false_rejection_not_invalid_frozen_corpus(self):
        d=json.loads((HERE/'findings.json').read_text());self.assertEqual(d['frozen_corpus']['valid'],37)
        f=d['findings'][0];self.assertEqual(f['oracle_values']['80'][6],0);self.assertEqual(f['oracle_values']['120'][6],0)
        self.assertNotEqual(f['exact_fraction_rounded_void'],0);self.assertEqual(f['oracle_values']['200'][6],f['exact_fraction_rounded_void'])
        self.assertEqual(f['dsl_values'][6],f['exact_fraction_rounded_void']);self.assertTrue(f['assessor']['rejected'])

    def test_domain_mismatch_retained(self):
        f=json.loads((HERE/'findings.json').read_text())['findings'][1]
        self.assertEqual(f['oracle_ec_binary64'],f['input']['parameters']['emin']);self.assertTrue(f['dsl']['rejected'])


if __name__=='__main__':unittest.main()
