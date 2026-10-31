"""Caller-overlay contract checks with synthetic native responses only."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

PACKET=Path(__file__).resolve().parents[1]/'docs/benchmarks/kfs-nested-partitions-v1'
SPEC=importlib.util.spec_from_file_location('nested_counts_test',PACKET/'run_case.py')
R=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(R)


class FakeNative:
    def __init__(self,adapt=False,echo=False,knot=False):
        self.commands=[];self.adapt=adapt;self.echo=echo;self.knot=knot
    def run(self,command,**kwargs):
        self.commands.append(list(command))
        if '--describe' in command:return subprocess.CompletedProcess(command,0,'{}','')
        steps=int(command[command.index('--steps')+1]);target=float(command[command.index('--target')+1])
        points=[{'strain':[target*i/steps,0,0,0,0,0],'substeps':2,'rejected':0} for i in range(steps+1)]
        if self.adapt:points[1].update(substeps=4,rejected=1)
        if self.knot:points[-1]['strain'][0]+=1e-10
        raw={'steps':steps+int(self.echo),'target':target,'points':points}
        return subprocess.CompletedProcess(command,0,json.dumps(raw),'')


class NestedCountTests(unittest.TestCase):
    def setUp(self):
        self.base=[{'steps':2,'target':.001,'axial_coordinates':[0,.0005,.001]}]
        self.command=['solver','--parameters','1,2','--initial','3,4','--steps','2','--target','0.001']

    def test_overlay_changes_only_steps_and_preserves_original_request(self):
        for multiplier in (2,4):
            fake=FakeNative();nested=R.NestedCounts(fake,self.base,multiplier,1e-14)
            nested.run(['solver','--describe']);nested.run(self.command);nested.finish()
            expected=list(self.command);expected[6]=str(2*multiplier)
            self.assertEqual(fake.commands,[['solver','--describe'],expected])
            self.assertEqual(self.command[6],'2')
            self.assertTrue(nested.diagnostics()['rejection_free_two_substep_gate'])
            self.assertEqual(nested.caller_points,2*multiplier)
            self.assertLessEqual(nested.maximum_knot_difference,1e-14)

    def test_wrong_request_or_duplicate_steps_reject_before_forwarding(self):
        for position,value in ((6,'3'),(8,'0.002')):
            fake=FakeNative();nested=R.NestedCounts(fake,self.base,2,1e-14)
            command=list(self.command);command[position]=value
            with self.assertRaises(ValueError):nested.run(command)
            self.assertEqual(fake.commands,[])
        fake=FakeNative();nested=R.NestedCounts(fake,self.base,2,1e-14)
        with self.assertRaises(ValueError):nested.run(self.command+['--steps','2'])
        self.assertEqual(fake.commands,[])

    def test_missing_extra_invalid_multiplier_and_excessive_count_reject(self):
        for multiplier in (1,True,8):
            with self.assertRaises(ValueError):R.NestedCounts(FakeNative(),self.base,multiplier,1e-14)
        nested=R.NestedCounts(FakeNative(),self.base,2,1e-14)
        with self.assertRaises(ValueError):nested.finish()
        nested.run(self.command)
        with self.assertRaises(ValueError):nested.run(self.command)
        baseline=[dict(self.base[0],steps=2501)];command=list(self.command);command[6]='2501'
        with self.assertRaises(ValueError):R.NestedCounts(FakeNative(),baseline,2,1e-14).run(command)

    def test_wrong_echo_and_nonnested_knots_reject(self):
        for fake in (FakeNative(echo=True),FakeNative(knot=True)):
            with self.assertRaises(ValueError):R.NestedCounts(fake,self.base,2,1e-14).run(self.command)

    def test_adaptation_is_retained_as_failed_diagnostic_gate(self):
        nested=R.NestedCounts(FakeNative(adapt=True),self.base,2,1e-14)
        nested.run(self.command);nested.finish()
        self.assertFalse(nested.diagnostics()['rejection_free_two_substep_gate'])
        self.assertEqual(nested.rejected,1)
        self.assertEqual(nested.substeps,10)


if __name__=='__main__':unittest.main()
