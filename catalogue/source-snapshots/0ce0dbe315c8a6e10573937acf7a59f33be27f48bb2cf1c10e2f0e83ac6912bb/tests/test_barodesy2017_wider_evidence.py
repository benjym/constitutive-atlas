"""Replay retained wider paths, raw transport and provenance without a solver."""
import json
import unittest
from atlas.model import ROOT
from atlas.evidence import verify_manifest_files
from tools import barodesy2017_wider_study as study

class RetainedWiderEvidence(unittest.TestCase):
    def test_archived_paths_and_both_transports_replay(self):
        relative = 'catalogue/investigations/barodesy2017-wider-integration-v1'
        packet = ROOT / relative
        manifest = verify_manifest_files(ROOT, relative + '/manifest.json')
        self.assertIs(manifest['public_admission'], False)
        self.assertIs(manifest['experimental_validation'], False)
        native = study.read(packet / 'native.json')
        wasm = study.read(packet / 'wasm.json')
        reference = study.checked_reference()[0]
        for report in (native, wasm):
            assessment = study.verify(report, reference)
            self.assertEqual(assessment['trajectory_count'], 48)
            self.assertEqual(assessment['call_count'], 576)
            raw = study.verify_transport(report, packet / (report['backend'] + '.transport.jsonl'))
            self.assertEqual(raw['rows'], 583)
        maximum = study.parity(wasm, native, packet / 'native.json',
                               packet / 'wasm.transport.jsonl', packet / 'native.transport.jsonl')
        self.assertEqual(maximum, study.read(packet / 'wasm-assessment.json')['maximum_native_wasm_scaled_difference'])
        self.assertEqual(maximum, manifest['verified_scope']['maximum_native_wasm_scaled_difference'])

if __name__ == '__main__':
    unittest.main()
