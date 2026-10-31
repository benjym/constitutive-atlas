"""Scalar-only propagation export, source binding and retained failure checks."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools.build_development import ROOT
from tools.build_propagation import FOLDERS,PROP,REF,NEST,summary


class PropagationPageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        for folder in FOLDERS:
            dest=self.root/folder;dest.mkdir(parents=True)
            for name in ('manifest.json','policy.json','results.json'):shutil.copyfile(ROOT/folder/name,dest/name)
        policy=json.loads((self.root/PROP/'policy.json').read_text())
        self.identity=policy['input_sha256']['paper/results/pilot-matched96/models/hypoplastic-sand-vw96.json']

    def mutate(self,folder,change):
        path=self.root/folder/'results.json';data=json.loads(path.read_text());change(data);path.write_text(json.dumps(data))
        manifest=self.root/folder/'manifest.json';m=json.loads(manifest.read_text())
        m['files'][str(folder/'results.json')]=hashlib.sha256(path.read_bytes()).hexdigest();manifest.write_text(json.dumps(m))

    def test_complete_scalar_projection_without_experiments_or_private_outputs(self):
        self.mutate(NEST,lambda r:r.update(unused={'points':['PRIVATE_SENTINEL'],'command':['solver'],'state':[1,2]}))
        data=summary(self.root,self.identity);text=json.dumps(data)
        self.assertEqual(len(data['panels']),4);self.assertFalse(data['original_refinement']['passed'])
        self.assertEqual(data['original_refinement']['nonincrease_failures'],4)
        self.assertTrue(data['nested']['passed']);self.assertEqual(data['nested']['caller_points'],9984)
        self.assertEqual(len(data['nested']['rows']),8)
        for token in ('PRIVATE_SENTINEL','"points"','"state"','"command"','"parameters"','/private/tmp','"case_indices"'):
            self.assertNotIn(token,text)
        self.assertFalse((self.root/'paper').exists())

    def test_changed_hash_or_archived_definition_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'definition'):summary(self.root,'0'*64)
        (self.root/PROP/'results.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):summary(self.root,self.identity)

    def test_rebound_duplicate_factorial_panel_is_rejected(self):
        self.mutate(PROP,lambda r:r['panels'].__setitem__(1,r['panels'][0]))
        with self.assertRaises(ValueError):summary(self.root,self.identity)

    def test_passing_nested_result_cannot_hide_failed_original(self):
        self.mutate(REF,lambda r:r.update(gate_passed=True))
        with self.assertRaises(ValueError):summary(self.root,self.identity)

    def test_rebound_nested_status_or_scientific_promotion_is_rejected(self):
        self.mutate(NEST,lambda r:r.update(gate_passed=False))
        with self.assertRaises(ValueError):summary(self.root,self.identity)
        self.mutate(NEST,lambda r:r.update(gate_passed=True,scientific_admission=True))
        with self.assertRaisesRegex(ValueError,'promotion'):summary(self.root,self.identity)

    def test_browser_contracts(self):
        result=subprocess.run(['node','--test','tests/test_propagation_view.mjs'],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__=='__main__':unittest.main()
