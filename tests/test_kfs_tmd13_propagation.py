"""Synthetic factorial/receipt gates; no native subprocesses or observations."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PACKET=Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-tmd13-evaluation-propagation-v1'
SPEC=importlib.util.spec_from_file_location('propagation_assessor_test',PACKET/'assess.py')
A=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(A)


class PropagationTests(unittest.TestCase):
    def fixture(self):
        ids=[f'test{i}' for i in range(6)]
        policy={'evaluation_ids':ids,'disputed_evaluation_ids':ids[-2:],'channels':['q','v']}
        records=[]
        for cal in (A.RUN.FILE,A.RUN.ALT):
            for eid in ids:
                for ev in ((A.RUN.FILE,A.RUN.ALT) if eid in ids[-2:] else (A.RUN.FILE,)):
                    value=(1 if cal==A.RUN.FILE else 4)+(3 if ev==A.RUN.ALT else 0)
                    records.append({'record':{'index':len(records),'experiment_id':eid,
                                               'calibration_scenario':cal,'evaluation_scenario':ev},
                                    'metrics':{c:{'scaled_mse':value} for c in ('q','v')}})
        return policy,records

    def test_factorial_coverage_and_equal_weighting(self):
        policy,records=self.fixture();panels,effects=A.aggregate(records,policy)
        self.assertEqual(len(records),16)
        for row,expected in zip(panels,(1,2,4,5)):
            self.assertAlmostEqual(row['root_scaled_mse']**2,expected)
        self.assertEqual(panels[0]['case_indices'][:4],panels[1]['case_indices'][:4])
        self.assertAlmostEqual(effects['calibration_only_change'],1)
        self.assertAlmostEqual(effects['combined_change'],5**.5-1)

    def test_missing_duplicate_and_nonfinite_panel_scores_reject(self):
        policy,records=self.fixture()
        for variant in (records[:-1],records+[records[0]]):
            with self.assertRaises(ValueError):A.aggregate(variant,policy)
        records[0]['metrics']['q']['scaled_mse']=float('nan')
        with self.assertRaises(ValueError):A.aggregate(records,policy)

    def saved(self,path,command=None,returncode=0,accepted=True,raw=None):
        raw={'ok':True,'catalogue_hash':'catalogue'} if raw is None else raw
        (path/'out').write_text(json.dumps(raw));(path/'err').write_text('')
        receipt={'index':0,'command':command or ['solver','--target','0.001'],
                 'returncode':returncode,'accepted':accepted,'stdout':'out','stderr':'err',
                 'stdout_sha256':hashlib.sha256((path/'out').read_bytes()).hexdigest(),
                 'stderr_sha256':hashlib.sha256(b'').hexdigest()}
        (path/'processes.json').write_text(json.dumps([receipt]))
        summary={'processes':1,'native_calls':0,
                 'process_receipts_sha256':hashlib.sha256((path/'processes.json').read_bytes()).hexdigest()}
        return A.SavedProcesses(path,summary,'catalogue')

    def test_offline_reconstruction_checks_command_order_and_exhaustion(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);tracker=self.saved(path)
            with self.assertRaises(ValueError):tracker.run(['solver','--target','0.002'])
            with self.assertRaises(ValueError):tracker.finish()
            result=tracker.run(['solver','--target','0.001']);tracker.finish()
            self.assertEqual(result.returncode,0)
            with self.assertRaises(ValueError):tracker.run(['solver'])

    def test_offline_reconstruction_rejects_nonzero_false_success_and_wrong_catalogue(self):
        with tempfile.TemporaryDirectory() as directory:
            for kwargs in ({'returncode':23},{'accepted':False},
                           {'raw':{'ok':False,'catalogue_hash':'catalogue'}},
                           {'raw':{'ok':True,'catalogue_hash':'other'}}):
                tracker=self.saved(Path(directory),**kwargs)
                with self.assertRaises(ValueError):tracker.run(['solver','--target','0.001'])

    def test_changed_raw_bytes_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);tracker=self.saved(path);(path/'out').write_text('{}')
            with self.assertRaises(ValueError):tracker.run(['solver','--target','0.001'])

    def test_elapsed_normalization_preserves_scientific_and_failure_fields(self):
        self.assertEqual(A.without_elapsed({'elapsed_seconds':1,'x':[{'elapsed_seconds':2,'ok':False}]}),
                         {'x':[{'ok':False}]})
        self.assertNotEqual(A.without_elapsed({'ok':False}),A.without_elapsed({'ok':True}))


if __name__=='__main__':unittest.main()
