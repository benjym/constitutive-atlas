"""Document round trips using frozen native responses; never executes a solver."""
import json,subprocess,unittest
from atlas.model import ROOT
from tests.scoped_recorded_execution_cases import retained
class RecordedDocumentTests(unittest.TestCase):
    def test_saved_response_documents(self):
        catalogue,rows=retained()
        result=subprocess.run(['node','tests/test_recorded_document.mjs'],cwd=ROOT,input=json.dumps(dict(catalogue=catalogue,rows=rows)),capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        report=json.loads(result.stdout)
        self.assertEqual(report['roundtrips'],16)
        self.assertGreaterEqual(report['rejections'],170)
