"""Scope-aware documents on saved native/Wasm responses; no solver execution."""
import json,subprocess,unittest
from atlas.model import ROOT
from tests.laboratory_scope_execution_cases import retained
class LaboratoryDocumentTests(unittest.TestCase):
    def test_saved_response_documents(self):
        catalogue,rows=retained()
        captured=json.loads((ROOT/'docs/reviews/laboratory-scope-adapter-v1/responses.json').read_text())[-1]
        rows.append(dict(label=captured['label'],request=captured['request'],response=captured['result']))
        legacy=[]
        packet=ROOT/'docs/reviews/laboratory-scope-contract-v1/observations'
        for p in sorted(packet.glob('[0-9]*.json')):
            d=json.loads(p.read_text())
            if not d['label'].startswith('current-elastic-'):continue
            r=json.loads(d['stdout']);s=dict(model=r['model'],parameters=r['parameters'],initial=r['initial'],protocol=r['protocol'],target=r['target'],steps=r['steps'],cycles=r['cycles'],integration_settings=r['integration_settings'])
            legacy.append(dict(request=s,response=r))
        r=subprocess.run(['node','tests/test_laboratory_document.mjs'],cwd=ROOT,input=json.dumps(dict(catalogue=catalogue,rows=rows,legacy=legacy)),capture_output=True,text=True,timeout=30)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        report=json.loads(r.stdout);self.assertEqual(report['scoped_roundtrips'],11);self.assertEqual(report['legacy_roundtrips'],5);self.assertTrue(report['zero_sign_roundtrip']);self.assertGreaterEqual(report['rejections'],180)
