"""Independent source oracle and negative controls for bounded partition evidence."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'docs/reviews/bounded-partition-retry-v1'
def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
assessor=imported('bounded_partition_assessor',STUDY/'qualification-v2/assess_partition.py')
reference=imported('bounded_partition_source',STUDY/'qualification-v2/analytical_reference.py')
def rows(backend):
    path=STUDY/('native-v2-analytical.jsonl' if backend=='native' else 'wasm-analytical.jsonl')
    return [json.loads(line) for line in path.read_text().splitlines()]

class BoundedPartitionEvidence(unittest.TestCase):
    def test_exact_source_branch_solution(self):
        result=reference.reference()
        self.assertTrue(result['original_failed'])
        self.assertEqual((result['original_tentative'],result['committed'],result['total_work']),(9,3,12))
        self.assertEqual((result['endpoint'],result['tangent']),('77/96','22/3'))

    def test_both_backends_satisfy_independent_source_and_budget_checks(self):
        for backend in ('native','wasm'):
            with self.subTest(backend=backend):self.assertTrue(assessor.assess(rows(backend))['pass_'])

    def test_discarded_work_cannot_disappear_from_global_budget(self):
        data=rows('native');data[0]['attempted']=3
        self.assertFalse(assessor.assess(data)['pass_'])
        data=rows('native');data[3]['attempted']=12
        self.assertFalse(assessor.assess(data)['pass_'])

    def test_wrong_fraction_alignment_is_rejected_even_with_unit_sum(self):
        data=rows('native');data[0]['fractions'][0]+=.01;data[0]['fractions'][1]-=.01
        self.assertFalse(assessor.assess(data)['pass_'])

    def test_source_tangent_and_full_history_rollback_are_required(self):
        data=rows('native');data[5]['matrix'][6][3]=1.
        self.assertFalse(assessor.assess(data)['pass_'])
        data=rows('native');data[3]['state'][6]+=.01
        self.assertFalse(assessor.assess(data)['pass_'])

    def test_exact_split_defect_is_required(self):
        data=rows('native');data[0]['defect'][0]=.01
        self.assertFalse(assessor.assess(data)['pass_'])

if __name__=='__main__':unittest.main()
