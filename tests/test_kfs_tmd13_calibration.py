"""Synthetic native-failure accounting and unchanged archived optimizer witnesses."""
import importlib
import hashlib
import sys
import types
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

PATH=Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-tmd13-calibration-sensitivity-v1/run_fit.py'
SPEC=importlib.util.spec_from_file_location('tmd13_calibration_runner',PATH)
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)


class CalibrationAccountingTests(unittest.TestCase):
    def test_valid_solver_failure_is_retained_for_original_penalty(self):
        for code,ok in ((0,False),(23,True)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as directory:
                tracker=MODULE.CalibrationProcesses(Path(directory),'frozen')
                response=subprocess.CompletedProcess(['synthetic'],code,json.dumps({'ok':ok,'catalogue_hash':'frozen','points':[]}),'retained')
                with patch.object(MODULE.subprocess,'run',return_value=response):
                    self.assertIs(tracker.run(['synthetic']),response)
                self.assertFalse(tracker.records[0]['accepted'])
                self.assertEqual(tracker.records[0]['native_outcome'],'constitutive_failure')
                self.assertEqual(tracker.records[0]['returncode'],code)

    def test_malformed_payload_or_catalogue_aborts_rather_than_receiving_penalty(self):
        for text in ('{"ok":true,"ok":false,"catalogue_hash":"frozen"}',
                     '{"ok":false,"catalogue_hash":"wrong"}',
                     '{"ok":1,"catalogue_hash":"frozen"}',
                     '{"ok":false,"catalogue_hash":"frozen","unused":1e999}'):
            with self.subTest(text=text),tempfile.TemporaryDirectory() as directory:
                tracker=MODULE.CalibrationProcesses(Path(directory),'frozen')
                response=subprocess.CompletedProcess(['synthetic'],0,text,'')
                with patch.object(MODULE.subprocess,'run',return_value=response):
                    with self.assertRaises(ValueError):tracker.run(['synthetic'])
                self.assertFalse(tracker.records[0]['accepted'])
                self.assertIn('error',tracker.records[0])

    def test_timeout_keeps_partial_receipt_for_failed_test(self):
        with tempfile.TemporaryDirectory() as directory:
            tracker=MODULE.CalibrationProcesses(Path(directory),'frozen')
            with patch.object(MODULE.subprocess,'run',side_effect=subprocess.TimeoutExpired(['synthetic'],1,output=b'partial')):
                with self.assertRaises(subprocess.TimeoutExpired):tracker.run(['synthetic'])
            self.assertEqual(tracker.records[0]['error'],'timeout')
            self.assertEqual((Path(directory)/'process-0000.stdout').read_bytes(),b'partial')

    def test_control_comparison_removes_only_elapsed_times(self):
        a={'elapsed_seconds':1,'trace':[{'objective':2,'elapsed_seconds':3,'completed':False}]}
        b={'elapsed_seconds':4,'trace':[{'objective':2,'elapsed_seconds':5,'completed':False}]}
        self.assertEqual(MODULE.strip_elapsed(a),MODULE.strip_elapsed(b))
        b['trace'][0]['completed']=True
        self.assertNotEqual(MODULE.strip_elapsed(a),MODULE.strip_elapsed(b))

    def test_archived_optimizer_counts_failed_candidate_and_all_three_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(__file__).parent/'fixtures/kfs-matched96-source'
            receipt=json.loads((folder/'receipt.json').read_text())
            for name,pin in receipt['files'].items():
                self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),pin['sha256'])
            package=types.ModuleType('fixture_kfs_native');package.__path__=[str(folder)]
            with patch.dict(sys.modules, {'fixture_kfs_native':package}):
                pilot=importlib.import_module('fixture_kfs_native.pilot')
            prepared=[{'experiment':{'id':name},'target':0.02,'scales':{'q':1,'volumetric_strain':0.01},
                       'curves':{'q':[(0,0),(0.02,0)],'volumetric_strain':[(0,0),(0.02,0)]}}
                      for name in ('cal-a','cal-b','cal-c')]
            class Adapter:
                calls=[]
                def simulate(self,mid,parameters,experiment,*args):
                    self.calls.append(experiment['id'])
                    if parameters['x']<0.5:return {'status':'integration_failure','points':[]}
                    return {'status':'success','points':[{'axial_strain':x,'q':parameters['x'],'volumetric_strain':0} for x in (0,0.02)]}
            model={'id':'synthetic','fit':{'x':{'bounds':[0,1],'transform':'linear'}},'baseline_parameters':{'x':0.5},'fixed_parameters':{}}
            config={'optimizer':{'max_evaluations':3,'initial_step':0.25,'minimum_step':0.001,'failure_objective':1e30},'steps':1,'timeout_seconds':1,'samples':3}
            adapter=Adapter();journal=[]
            result=pilot.calibrate(model,prepared,config,adapter,0,journal.append)
            self.assertEqual(result['evaluation_count'],3);self.assertEqual(len(adapter.calls),9)
            self.assertFalse(journal[1]['completed']);self.assertEqual(journal[1]['objective'],1e30)
            self.assertEqual(len(journal[1]['tests']),3);self.assertEqual(result['best']['parameters'],{'x':0.5})


if __name__=='__main__':unittest.main()
