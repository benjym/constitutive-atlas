"""Saved native scope receipts: no build or material process is invoked."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from atlas.model import ROOT
PACKET=ROOT/'docs/reviews/recorded-scope-native-v1'
spec=importlib.util.spec_from_file_location('recorded_scope_saved_gate',PACKET/'gate.py')
GATE=importlib.util.module_from_spec(spec);spec.loader.exec_module(GATE)

class RecordedScopeNativeTests(unittest.TestCase):
    def test_saved_gate_with_native_execution_denied(self):
        with patch('subprocess.run',side_effect=AssertionError('native execution forbidden')):
            result=GATE.assess(PACKET)
        self.assertEqual(result['processes'],46);self.assertEqual(result['native_calls'],0)

    def test_scope_wire_exit_prefix_and_restart_corruptions_reject(self):
        for mutation in ['scope','version','wire','exit','prefix','restart','missing']:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                target=Path(directory)/'packet';shutil.copytree(PACKET,target)
                cases=json.loads((target/'cases.json').read_text())
                label='scope-failed-1' if mutation in ['prefix','restart'] else 'total-mixed'
                i=next(i for i,c in enumerate(cases) if c['label']==label);path=target/'observations'/f'{i:03d}.json'
                if mutation=='missing':path.unlink()
                else:
                    receipt=json.loads(path.read_text());data=json.loads(receipt['stdout'])
                    if mutation=='scope':data['stress']['scope']='effective'
                    elif mutation=='version':data['api_version']='experimental-recorded-replay-0.1'
                    elif mutation=='wire':data['controls_wire'][0]=9
                    elif mutation=='exit':receipt['returncode']=1
                    elif mutation=='prefix':data['state'][0]+=1
                    elif mutation=='restart':data['restart_settings']['max_restarts']=0
                    receipt['stdout']=json.dumps(data);path.write_text(json.dumps(receipt))
                with self.assertRaises((AssertionError,ValueError,KeyError,FileNotFoundError)):GATE.assess(target)

    def test_captured_commands_select_declared_scope_and_no_legacy_fallback(self):
        cases=json.loads((PACKET/'cases.json').read_text())
        for i,case in enumerate(cases):
            receipt=json.loads((PACKET/'observations'/f'{i:03d}.json').read_text());argv=receipt['command'];args=dict(zip(argv[1::2],argv[2::2]))
            self.assertEqual(args['--mode'],'recorded');self.assertEqual(args['--model'],case['model'])
            if case['scope'] is None:self.assertNotIn('--recorded-stress-scope',args)
            else:self.assertEqual(args['--recorded-stress-scope'],case['scope'])
            self.assertEqual('--recorded-restarts' in args,case['restart'] is not None)

if __name__=='__main__':unittest.main()
