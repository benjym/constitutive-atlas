"""Saved scoped-view receipts and destructive corruption witnesses; no engine."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from atlas.model import ROOT
PACKET=ROOT/'docs/reviews/recorded-scope-view-v1'
s=importlib.util.spec_from_file_location('recorded_scope_view_gate',PACKET/'verify.py');gate=importlib.util.module_from_spec(s);s.loader.exec_module(gate)
class RecordedScopeViewEvidenceTests(unittest.TestCase):
    def test_saved_evidence_without_processes(self):
        with patch('subprocess.run',side_effect=AssertionError('execution forbidden')):result=gate.assess(PACKET)
        self.assertEqual(result['wasm_pairs'],12);self.assertEqual(result['native_calls'],0)
    def test_scope_prefix_csv_and_catalogue_corruptions(self):
        for kind in ['scope','prefix','csv','catalogue']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                p=Path(temp)/'packet';shutil.copytree(PACKET,p)
                if kind=='csv':
                    f=p/'browser-total.csv';f.write_text(f.read_text().replace(',unavailable,',',unavailable,0',1))
                else:
                    f=p/('browser-failure.json' if kind=='prefix' else 'browser-total.json');d=json.loads(f.read_text())
                    if kind=='scope':d['result']['stress']['scope']='effective'
                    elif kind=='prefix':d['result']['state'][0]+=1
                    else:d['catalogue_hash']='0'*64
                    f.write_text(json.dumps(d))
                with self.assertRaises((AssertionError,RuntimeError,ValueError)):gate.assess(p)
