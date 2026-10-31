"""Scoped laboratory JS boundary on retained data; no compiled execution."""
import json,subprocess,unittest
from atlas.model import ROOT
from tests.laboratory_scope_execution_cases import retained
class LaboratoryScopeExecutionTests(unittest.TestCase):
    def test_saved_responses_routing_pore_policy_and_corruptions(self):
        catalogue,rows=retained()
        r=subprocess.run(['node','tests/test_laboratory_scope_execution.mjs'],cwd=ROOT,input=json.dumps(dict(catalogue=catalogue,rows=rows)),capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        result=json.loads(r.stdout);self.assertEqual(result['saved_cases'],10);self.assertGreaterEqual(result['rejections'],220)
