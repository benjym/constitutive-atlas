"""Actual view/worker module contracts on saved data, without an engine build."""
import json,subprocess,unittest
from atlas.model import ROOT
from tests.scoped_recorded_execution_cases import retained
class ScopedRecordedViewTests(unittest.TestCase):
    def test_view_and_worker_contract(self):
        catalogue,rows=retained()
        result=subprocess.run(['node','tests/test_recorded_scope_view.mjs'],cwd=ROOT,input=json.dumps(dict(catalogue=catalogue,rows=rows)),text=True,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout),dict(scoped_view_runs=3,legacy_view_runs=1,missing_export_no_fallback=True))
