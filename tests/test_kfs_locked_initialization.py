"""Synthetic process-gate checks; no native executable is launched."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

PATH=Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-locked-initialization-sensitivity-v1/run_case.py'
SPEC=importlib.util.spec_from_file_location('locked_init_runner',PATH)
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ProcessReceiptTests(unittest.TestCase):
    def run_stub(self, code=0, stdout=None, command=None):
        command=command or ['synthetic-solver','--model','synthetic']
        stdout=stdout or '{"ok":true,"catalogue_hash":"frozen"}'
        with tempfile.TemporaryDirectory() as directory:
            tracker=MODULE.RecordedProcesses(Path(directory),'frozen')
            process=subprocess.CompletedProcess(command,code,stdout,'diagnostic stderr')
            with patch.object(MODULE.subprocess,'run',return_value=process) as launch:
                if code or 'false' in stdout:
                    with self.assertRaises(ValueError):tracker.run(command,capture_output=True,text=True)
                else:
                    tracker.run(command,capture_output=True,text=True)
                launch.assert_called_once()
            retained=json.loads((Path(directory)/'processes.json').read_text())
            self.assertEqual(len(retained),1)
            for name in ('stdout','stderr'):
                content=(Path(directory)/retained[0][name]).read_bytes()
                self.assertEqual(MODULE.digest(content),retained[0][name+'_sha256'])
            return retained[0]

    def test_success_is_recorded_and_bound_to_exact_output(self):
        self.assertTrue(self.run_stub()['accepted'])

    def test_nonzero_exit_rejects_even_when_payload_says_ok(self):
        record=self.run_stub(code=23)
        self.assertEqual(record['returncode'],23)
        self.assertFalse(record['accepted'])

    def test_false_success_flag_rejects_zero_exit(self):
        self.assertFalse(self.run_stub(stdout='{"ok":false,"catalogue_hash":"frozen"}')['accepted'])

    def test_describe_requires_frozen_catalogue(self):
        record=self.run_stub(stdout='{"sha256":"frozen"}',command=['synthetic-solver','--describe'])
        self.assertTrue(record['accepted'])

    def test_duplicate_nonfinite_and_wrong_catalogue_retain_failure(self):
        for stdout in ('{"ok":true,"ok":false,"catalogue_hash":"frozen"}',
                       '{"ok":true,"catalogue_hash":"frozen","unused":1e999}',
                       '{"ok":true,"catalogue_hash":"other"}',
                       '{"ok":true,"catalogue_hash":"frozen","unused":NaN}'):
            with self.subTest(stdout=stdout), tempfile.TemporaryDirectory() as directory:
                tracker=MODULE.RecordedProcesses(Path(directory),'frozen')
                process=subprocess.CompletedProcess(['synthetic'],0,stdout,'')
                with patch.object(MODULE.subprocess,'run',return_value=process):
                    with self.assertRaises(ValueError):tracker.run(['synthetic'],text=True)
                self.assertFalse(tracker.records[0]['accepted'])
                self.assertEqual((Path(directory)/'process-0000.stdout').read_text(),stdout)

    def test_timeout_preserves_partial_output_without_score(self):
        with tempfile.TemporaryDirectory() as directory:
            tracker=MODULE.RecordedProcesses(Path(directory),'frozen')
            failure=subprocess.TimeoutExpired(['synthetic'],1,output=b'partial',stderr=b'stopped')
            with patch.object(MODULE.subprocess,'run',side_effect=failure):
                with self.assertRaises(subprocess.TimeoutExpired):tracker.run(['synthetic'])
            self.assertEqual(tracker.records[0]['error'],'timeout')
            self.assertEqual((Path(directory)/'process-0000.stdout').read_bytes(),b'partial')

    def test_launch_failure_is_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            tracker=MODULE.RecordedProcesses(Path(directory),'frozen')
            with patch.object(MODULE.subprocess,'run',side_effect=OSError('launch failed')):
                with self.assertRaises(OSError):tracker.run(['synthetic'])
            self.assertFalse(tracker.records[0]['accepted'])
            self.assertIn('launch failed',tracker.records[0]['error'])


if __name__=='__main__':unittest.main()
