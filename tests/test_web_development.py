"""Source binding and scalar allowlist for the provisional development page."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools.build_development import ROOT,LOCKED,REFINED,bundle
from tools.build_propagation import FOLDERS,CURRENT_FOLDERS


class DevelopmentPageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.output=Path(self.temp.name)/'site'

    def fixture(self):
        root=Path(self.temp.name)/'fixture'
        for folder in (LOCKED,REFINED,*FOLDERS):
            destination=root/folder;destination.mkdir(parents=True)
            for name in ('manifest.json','results.json','policy.json'):
                shutil.copyfile(ROOT/folder/name,destination/name)
        for folder in CURRENT_FOLDERS:shutil.copytree(ROOT/folder,root/folder,ignore=shutil.ignore_patterns('__pycache__'))
        from tools.build_reporting_review import PACKET
        for folder in (PACKET,Path('docs/benchmarks/kfs-development-review-v1')):
            shutil.copytree(ROOT/folder,root/folder)
        (root/'web').mkdir()
        for name in ('development.html','development.mjs','propagation.mjs','reporting-review.mjs'):shutil.copyfile(ROOT/'web'/name,root/'web'/name)
        return root

    def repin(self,root,folder,name):
        path=root/folder/name;manifest=root/folder/'manifest.json';m=json.loads(manifest.read_text())
        m['files'][str(folder/name)]=hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(m))

    def test_only_explicit_scalar_view_is_exported(self):
        root=self.fixture();(root/LOCKED/'private-response.json').write_text('PRIVATE_SENTINEL')
        data=bundle(self.output,root)
        self.assertEqual({p.name for p in self.output.iterdir()},{'development.html','development.mjs','propagation.mjs','reporting-review.mjs','development.json','reporting-review'})
        self.assertEqual(data['status'],'provisional');self.assertFalse(data['scientific_admission'])
        self.assertEqual(len(data['scores']),4);self.assertEqual(len(data['refinement']['shifts']),12)
        text=(self.output/'development.json').read_text()
        for forbidden in ('PRIVATE_SENTINEL','"points"','"state"','effective_stress','/private/tmp','native_calls','"parameters"'):
            self.assertNotIn(forbidden,text)
        self.assertEqual(set(data['scores'][0]),{'package','scenario','root_scaled_mse'})
        self.assertEqual(set(data['refinement']['shifts'][0]),{'package','test','maximum_increment','q','volume'})

    def test_changed_evidence_fails_before_writing(self):
        root=self.fixture();(root/LOCKED/'results.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):bundle(self.output,root)
        self.assertFalse(self.output.exists())

    def test_rebound_hash_cannot_hide_duplicate_scores_or_changed_gate(self):
        for variant in ('scores','gate'):
            with self.subTest(variant=variant):
                root=self.fixture() if variant=='scores' else Path(self.temp.name)/'fixture'
                if variant=='scores':
                    path=root/LOCKED/'results.json';r=json.loads(path.read_text());r['panels'][1]=r['panels'][0]
                    path.write_text(json.dumps(r));self.repin(root,LOCKED,'results.json')
                else:
                    shutil.copyfile(ROOT/LOCKED/'results.json',root/LOCKED/'results.json');self.repin(root,LOCKED,'results.json')
                    path=root/REFINED/'results.json';r=json.loads(path.read_text());r['gate_passed']=False
                    path.write_text(json.dumps(r));self.repin(root,REFINED,'results.json')
                with self.assertRaises(ValueError):bundle(self.output,root)
                self.assertFalse(self.output.exists())

    def test_browser_contracts(self):
        r=subprocess.run(['node','--test','tests/test_development_view.mjs'],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)


if __name__=='__main__':unittest.main()
