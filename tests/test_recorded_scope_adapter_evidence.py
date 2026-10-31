"""Saved scoped adapter receipts, with process execution disabled."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from atlas.model import ROOT
PACKET=ROOT/'docs/reviews/recorded-scope-adapters-v1'
spec=importlib.util.spec_from_file_location('scoped_adapter_saved',PACKET/'verify.py');VERIFIER=importlib.util.module_from_spec(spec);spec.loader.exec_module(VERIFIER)
class ScopedAdapterEvidenceTests(unittest.TestCase):
    def test_saved_adapter_receipts_without_execution(self):
        with patch('subprocess.run',side_effect=AssertionError('execution forbidden')):
            result=VERIFIER.verify(PACKET)
        self.assertEqual(result['native_calls'],0)
    def test_receipt_scope_wire_exit_and_descriptor_corruptions_reject(self):
        for kind in ['scope','wire','exit','descriptor']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                copy=Path(temp)/'packet';shutil.copytree(PACKET,copy);path=copy/('000.json' if kind=='descriptor' else '001.json');receipt=json.loads(path.read_text())
                if kind=='scope':receipt['command'][receipt['command'].index('--recorded-stress-scope')+1]='total'
                elif kind=='wire':receipt['wires']['--recorded-knots-file']='0'
                elif kind=='exit':receipt['returncode']=1
                else:
                    meta=json.loads(receipt['stdout']);meta['sha256']='0'*64;receipt['stdout']=json.dumps(meta)
                path.write_text(json.dumps(receipt))
                with self.assertRaises(AssertionError):VERIFIER.verify(copy)
