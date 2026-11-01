"""Transport/receipt tests use mocks only; no compiled or candidate calls."""
import gzip
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from assess import context, read_records, sha
from run import invoke


class DriverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ctx=context()

    def test_native_recorded_wire_uses_files(self):
        request=self.ctx['requests'][-1]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'request'
            raw=json.dumps({'ok':True,'long_diagnostic':'x'*150000})
            with patch('run.subprocess.run',return_value=subprocess.CompletedProcess([],0,raw,'captured stderr')) as process:
                receipt=invoke('native',Path('/mock/atlas_solver'),request,path)
            self.assertEqual((path/'knots.csv').read_text(),request['args'][5])
            self.assertNotIn(request['args'][5],process.call_args.args[0])
            self.assertEqual(receipt['response']['long_diagnostic'],'x'*150000)
            self.assertEqual(receipt['stderr'],'captured stderr')
            self.assertIn('--recorded-stress-scope',receipt['argv'])

    def test_wasm_reads_request_file(self):
        request=self.ctx['probes']['probes'][-1]
        with tempfile.TemporaryDirectory() as td:
            with patch('run.subprocess.run',return_value=subprocess.CompletedProcess([],0,'{"ok":false}','')):
                receipt=invoke('wasm',Path('/mock/atlas.js'),request,Path(td)/'request')
            self.assertEqual(json.loads(Path(receipt['argv'][-1]).read_text()),request)

    def test_timeout_preserves_partial_stdout(self):
        with tempfile.TemporaryDirectory() as td:
            with patch('run.subprocess.run',side_effect=subprocess.TimeoutExpired(['mock'],300,output=b'partial',stderr=b'reason')):
                receipt=invoke('native',Path('/mock/atlas_solver'),self.ctx['probes']['probes'][0],Path(td)/'request')
            self.assertEqual(receipt['stdout'],'partial');self.assertEqual(receipt['exception'],'timeout')
            self.assertIsNone(receipt['returncode'])

    def test_literal_request_and_raw_response_binding(self):
        request=self.ctx['probes']['probes'][0]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td);(path/'build-receipt.json').write_text('{}')
            receipt={'request':request,'returncode':1,'response':{'ok':False},'stdout':'{"ok":false}'}
            def save():
                f=path/'result.json.gz';f.write_bytes(gzip.compress(json.dumps(receipt).encode()))
                (path/'index.json').write_text(json.dumps({'backend':'native','status':'completed','build_receipt_sha256':sha(path/'build-receipt.json'),'records':[{'id':request['id'],'file':f.name,'sha256':sha(f)}]}))
            save();self.assertEqual(read_records(path),{request['id']:{'ok':False}})
            receipt['request']=dict(request,args=list(request['args']));receipt['request']['args'][2]='0'
            save()
            with self.assertRaisesRegex(ValueError,'actual request differs'):read_records(path)
            receipt['request']=request;receipt['stdout']='{"ok":true}';save()
            with self.assertRaisesRegex(ValueError,'raw response mismatch'):read_records(path)


if __name__=='__main__':unittest.main()
