"""Private-data evidence checks; never build or launch a native process.

Set ATLAS_CURRENT_TMD7_DIR to the retained output directory if needed. These
checks skip explicitly when private observations are unavailable in a checkout.
"""
import copy
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'docs/benchmarks/current-kfs-tmd7-v1'
SPEC=importlib.util.spec_from_file_location('tmd7_current_test',PACKET/'replay.py')
R=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(R)
PRIVATE=Path(os.environ.get('ATLAS_CURRENT_TMD7_DIR','/private/tmp/atlas-current-kfs-tmd7-v1'))

class CurrentTMD7(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        policy=R.read(PACKET/'policy.json')
        if not PRIVATE.is_dir() or not Path(policy['baseline_directory']).is_dir() or not (ROOT/'paper/results/pilot-matched96/report.json').exists():
            raise unittest.SkipTest('private KFS observations/source snapshots unavailable; no data download or native calls')

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='atlas-current-tmd7-audit-');self.addCleanup(self.tmp.cleanup)
        self.out=Path(self.tmp.name)/'observations';shutil.copytree(PRIVATE,self.out)

    def rebind(self):
        summary=R.read(self.out/'summary.json');summary['process_receipts_sha256']=R.sha(self.out/'processes.json')
        R.OLD.write(self.out/'summary.json',summary)

    def test_exact_scalar_reconstruction(self):
        self.assertEqual(R.audit(self.out),R.read(PACKET/'results.json'))

    def test_changed_actual_command(self):
        ledger=R.read(self.out/'processes.json');args=ledger[1]['command'];args[args.index('--target')+1]='0.099'
        R.OLD.write(self.out/'processes.json',ledger);self.rebind()
        with self.assertRaisesRegex(ValueError,'command/order|failed or partial'):R.audit(self.out)

    def test_nonzero_false_success(self):
        ledger=R.read(self.out/'processes.json');ledger[1]['returncode']=23;ledger[1]['accepted']=True
        R.OLD.write(self.out/'processes.json',ledger);self.rebind()
        with self.assertRaisesRegex(ValueError,'integer process code'):R.audit(self.out)

    def test_altered_native_step_echo_with_rebound_hashes(self):
        ledger=R.read(self.out/'processes.json');path=self.out/ledger[1]['stdout'];raw=R.read(path);raw['steps']+=1
        R.OLD.write(path,raw);ledger[1]['stdout_sha256']=R.sha(path);R.OLD.write(self.out/'processes.json',ledger);self.rebind()
        with self.assertRaisesRegex(ValueError,'target/count'):R.audit(self.out)

    def test_prediction_substitution_with_rebound_hash(self):
        path=self.out/'prediction.json';prediction=R.read(path);prediction['points'][1]['q']+=1
        R.OLD.write(path,prediction);summary=R.read(self.out/'summary.json');summary['prediction_sha256']=R.sha(path)
        R.OLD.write(self.out/'summary.json',summary)
        with self.assertRaisesRegex(ValueError,'full native prediction reconstruction'):R.audit(self.out)

    def test_excess_difference_stays_failed(self):
        policy,_,experiment,rows=R.inputs();baseline=R.read(Path(policy['baseline_directory'])/'prediction.json')
        altered=copy.deepcopy(baseline);point=altered['points'][-1];point['state'][0]+=11.;point['q']+=11.
        result=R.comparison(altered,baseline,policy,rows)
        self.assertFalse(result['overall_compatibility_pass']);self.assertFalse(result['gates']['stress_pa'])
        self.assertEqual(result['maximum_differences']['stress_pa'],11.)

if __name__=='__main__':unittest.main()
