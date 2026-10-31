"""Scope presentation plus actual chart/label handlers on saved responses."""
import json,subprocess,unittest
from atlas.model import ROOT
from tests.laboratory_scope_execution_cases import retained
class LaboratoryViewTests(unittest.TestCase):
    def test_view_and_worker_contract(self):
        c,rows=retained();r=subprocess.run(['node','tests/test_laboratory_view.mjs'],cwd=ROOT,input=json.dumps(dict(catalogue=c,rows=rows)),capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertEqual(json.loads(r.stdout)['model_protocol_cases'],10)
