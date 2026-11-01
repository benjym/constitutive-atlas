"""Replay the frozen endpoint-constraint study and challenge its decisive gates."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'docs/reviews/newton-endpoint-constraints-v1'
spec=importlib.util.spec_from_file_location('newton_endpoint_assessor',STUDY/'assess-v5.py')
assessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(assessor)

def rows(backend):
    return [json.loads(line) for line in (STUDY/f'{backend}-v5-newton.jsonl').read_text().splitlines()]

class NewtonEndpointEvidence(unittest.TestCase):
    def test_both_backends_meet_original_source_and_transaction_gates(self):
        for backend in ('native','wasm'):
            with self.subTest(backend=backend):
                data=rows(backend)
                self.assertEqual(len(data),81)
                self.assertTrue(assessor.assess(data)['pass_'])

    def test_inadmissible_endpoint_and_unbounded_correction_are_rejected(self):
        for mutation in ('endpoint_admissible','rounding','restarts','replay','recovery'):
            with self.subTest(mutation=mutation):
                data=rows('native')
                data[0][mutation]=False if mutation in ('endpoint_admissible','replay','recovery') else 100000
                self.assertFalse(assessor.assess(data)['pass_'])

    def test_partial_state_rollback_is_rejected(self):
        data=rows('native')
        failure=next(row for row in data if not row['ok'])
        failure['state'][-1]+=1
        self.assertFalse(assessor.assess(data)['pass_'])

    def test_missing_case_is_rejected(self):
        with self.assertRaises(AssertionError):assessor.assess(rows('native')[:-1])

if __name__=='__main__':unittest.main()
