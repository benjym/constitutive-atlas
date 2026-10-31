"""Saved receipt and semantic corruption checks; never execute native code."""
import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

PACKET=Path(__file__).resolve().parents[1]/'docs/benchmarks/current-archived-vw96-v1'
SPEC=importlib.util.spec_from_file_location('vw96_saved',PACKET/'check_saved.py')
SAVED=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(SAVED)
S=SAVED.STUDY

class EngineEvidence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='atlas-engine-audit-')
        self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)/'observations'
        shutil.copytree(PACKET/'observations',self.out)

    def rebind(self,index):
        """Update hashes to test semantic guards beyond accidental corruption."""
        stem=f'process-{index:02d}';p=self.out/(stem+'.json');r=S.read(p)
        r['stdout_sha256']=S.sha(self.out/(stem+'.stdout'));S.write(p,r)
        ledger=S.read(self.out/'processes.json');ledger[index]['receipt_sha256']=S.sha(p)
        S.write(self.out/'processes.json',ledger)

    def test_exact_reconstruction(self):
        self.assertEqual(S.audit(self.out),S.read(self.out/'results.json'))

    def test_actual_command_substitution(self):
        p=self.out/'process-05.json';r=S.read(p);r['command'][r['command'].index('--steps')+1]='31';S.write(p,r)
        ledger=S.read(self.out/'processes.json');ledger[5]['command']=r['command'];S.write(self.out/'processes.json',ledger)
        self.rebind(5)
        with self.assertRaisesRegex(ValueError,'ledger differs|command differs'):S.audit(self.out)

    def test_nonzero_process_even_with_rebound_hashes(self):
        p=self.out/'process-05.json';r=S.read(p);r['returncode']=1;S.write(p,r);self.rebind(5)
        with self.assertRaisesRegex(ValueError,'nonzero'):S.audit(self.out)

    def test_altered_input_echo_even_with_rebound_hashes(self):
        p=self.out/'process-05.stdout';r=S.read(p);r['steps']-=1;S.write(p,r);self.rebind(5)
        with self.assertRaisesRegex(ValueError,'input echo'):S.audit(self.out)

    def test_incomplete_points_even_with_rebound_hashes(self):
        p=self.out/'process-05.stdout';r=S.read(p);r['points'].pop();S.write(p,r);self.rebind(5)
        with self.assertRaisesRegex(ValueError,'incomplete run'):S.audit(self.out)

    def test_excess_difference_is_retained_as_failed_gate(self):
        # Current drained32 is process16. Preserve its control constraints and
        # observable identities while making the engine difference exceed10Pa.
        p=self.out/'process-16.stdout';r=S.read(p);point=r['points'][-1]
        point['state'][0]+=11.;point['p']+=11./3;point['q']+=11.;point['q_signed']+=11.
        S.write(p,r);self.rebind(16)
        result=S.audit(self.out)
        self.assertFalse(result['overall_compatibility_pass'])
        self.assertFalse(result['path_comparisons'][0]['pass'])
        self.assertGreater(result['path_comparisons'][0]['maximum_differences']['stress_pa'],10.)

if __name__=='__main__':unittest.main()
