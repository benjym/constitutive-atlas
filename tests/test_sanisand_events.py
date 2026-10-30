"""Decision-fixture checks only; no builds or native execution."""
import hashlib,json,unittest
from pathlib import Path
from tools import sanisand_event_study as study
from tools.sanisand_event_study import ROOT,generate,digest
HERE=Path(__file__).resolve().parents[1]
EVIDENCE=HERE/'catalogue/investigations/sanisand-events-v1/evidence.json'
class Events(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=json.loads(EVIDENCE.read_text())
    def test_manifest_and_reproducibility(self):
        self.assertEqual(self.d,generate())
        manifest=json.loads((EVIDENCE.parent/'manifest.json').read_text())
        for f,h in manifest.items():self.assertEqual(hashlib.sha256((HERE/f).read_bytes()).hexdigest(),h)
        for f,h in self.d['files_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h)
        self.assertEqual(digest(self.d['parameters']),self.d['parameter_sha256'])
        self.assertEqual(hashlib.sha256(Path(study.__file__).read_bytes()).hexdigest(),self.d['generator_sha256'])
        for row in self.d['elastic_entry']+self.d['hardening_limit']+self.d['rejections']:
            self.assertEqual(digest(row['inputs']),row['input_sha256'])
    def test_entry_bracket_and_partition(self):
        for row in self.d['elastic_entry']:
            ev=row['event'];lo=ev['lower'];hi=ev['upper']
            self.assertLess(lo['fraction'],hi['fraction']);self.assertLessEqual(hi['fraction']-lo['fraction'],1e-12)
            self.assertLess(lo['residual'],0);self.assertGreaterEqual(hi['residual'],0)
            self.assertLess(abs(row['recomposed_upper_fraction']-hi['fraction']),2e-12)
            if 'analytic_fraction' in row:self.assertLessEqual(lo['fraction'],row['analytic_fraction']);self.assertGreaterEqual(hi['fraction'],row['analytic_fraction'])
    def test_distinct_reversal_guards_and_scope(self):
        r=self.d['reversal_selection'];self.assertGreater(r['source_local_cone_guard'],0)
        self.assertEqual(digest(r['parent']),r['parent_sha256'])
        rows={x['name']:x for x in r['selection']}
        for name in ['reverse','oblique_reverse']:
            self.assertLess(rows[name]['guard'],0);self.assertTrue(rows[name]['reset'])
        for name in ['forward','zero','transverse']:self.assertFalse(rows[name]['reset'])
        for x in rows.values():
            self.assertTrue(x['preserved_fabric'])
            self.assertEqual(digest(dict(parent=r['parent'],increment=x['increment'])),x['input_sha256'])
            for k in r['parent']:
                if k!='alpha_in':self.assertEqual(x['prepared'][k],r['parent'][k])
        p=r['partition_selection'];self.assertGreater(p['unsplit_guard'],0);self.assertLess(p['split_first_guard'],0)
        self.assertNotEqual(p['unsplit_anchor'],p['split_first_anchor'])
    def test_regular_limit_and_rejections(self):
        for sign in [1,-1]:
            rows=[r for r in self.d['hardening_limit'] if r['sign']==sign];zero=rows[0]
            self.assertEqual(zero['distance'],0);self.assertGreater(zero['output']['hardening_numerator'],0)
            self.assertEqual(zero['output']['plastic_multiplier'],0)
            self.assertEqual(zero['output']['fabric_increment'],[0.]*6)
            for a,b in zip(zero['output']['backstress_increment'],zero['zero_limit_alpha']):self.assertLess(abs(a-b),1e-13)
            if sign==1:
                self.assertLess(abs(zero['yield_consistency_defect']),1e-8)
                self.assertGreater(sum(x*x for x in zero['output']['backstress_increment']),0)
                errors=[r['alpha_error_to_zero'] for r in rows[1:]]
                for a,b in zip(errors,errors[1:]):self.assertLess(b,a*.02)
                self.assertLess(errors[-1],1e-12)
            else:
                self.assertLess(zero['yield_consistency_defect'],0)
                for r in rows:self.assertEqual(r['output']['backstress_increment'],[0.]*6)
        self.assertEqual([r['name'] for r in self.d['rejections']],['negative-distance','nonpositive-Hbar-zero'])
if __name__=='__main__':unittest.main()
