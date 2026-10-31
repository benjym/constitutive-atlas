"""Retained native/Wasm evidence and rejection of corrupted creep studies."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from atlas.model import ROOT
from tools.verify_terracotta_creep_wasm import assess, verify_artifacts


EVIDENCE = ROOT/'catalogue/investigations/terracotta-creep-wasm-v1'


class CreepWasmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((EVIDENCE/'parity.json').read_bytes())
        cls.reference = json.loads((ROOT/'tests/reference/terracotta-2024-scalar-creep.json').read_bytes())
        cls.manifest = json.loads((EVIDENCE/'manifest.json').read_bytes())

    def check_report(self, report):
        return assess(report, self.reference, self.manifest['runtime_catalogue_sha256'])

    def test_retained_matrix_and_reference(self):
        summary = self.check_report(self.report)
        self.assertEqual(summary, json.loads((EVIDENCE/'reference-assessment.json').read_bytes()))
        self.assertEqual(set(summary), {'native', 'wasm'})
        for name, digest in self.manifest['inputs'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest, name)
        for name, digest in self.manifest['artifacts'].items():
            self.assertEqual(hashlib.sha256((EVIDENCE/name).read_bytes()).hexdigest(), digest, name)

    def test_rejects_incomplete_or_duplicate_matrix(self):
        for records in (self.report['records'][:-1], self.report['records']+[self.report['records'][0]]):
            bad = copy.deepcopy(self.report); bad['records'] = records
            with self.assertRaises(ValueError): self.check_report(bad)

    def test_rejects_corrupted_backend(self):
        for backend in ('native', 'wasm'):
            for defect in ('failure', 'state', 'mask', 'norm', 'catalogue', 'request', 'metrics'):
                with self.subTest(backend=backend, defect=defect):
                    bad = copy.deepcopy(self.report); row = bad['records'][0]; response = row[backend]
                    if defect == 'failure': response['ok'] = False
                    if defect == 'state': response['points'][-1]['state'][0] += .1
                    if defect == 'mask': response['points'][1]['strain_rate'][0] = 0
                    if defect == 'norm': response['points'][-1]['temporal_error_norm'] = float('nan')
                    if defect == 'catalogue': response['catalogue_hash'] = '0'*64
                    if defect == 'request': row['request']['solver']['relative_tolerance'] = .5
                    if defect == 'metrics': row['maximum_scaled_parity_errors']['state'] = .5
                    with self.assertRaises(ValueError): self.check_report(bad)

    def test_artifact_binding_rejects_changes(self):
        paths = {key: EVIDENCE/'parity.json' for key in self.report['artifacts']}
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            verify_artifacts(self.report, paths)
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            verify_artifacts(self.report, {})


if __name__ == '__main__': unittest.main()
