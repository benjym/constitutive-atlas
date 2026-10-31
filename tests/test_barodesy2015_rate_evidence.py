"""Original six negative-study checks execute against their immutable source closure."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from atlas.source_replay import registered

ROOT=Path(__file__).resolve().parents[1]
REGISTRY='catalogue/source-replays/sand-negative-v1/registry.json'


class SandRateEvidence(unittest.TestCase):
    def test_original_six_checks_and_negative_cli_reproduce(self):
        result=registered(ROOT,REGISTRY,'sand-negative')
        summary=json.loads(result['stdout'])
        self.assertTrue(result['historical_output_reproduced'])
        self.assertEqual(summary,dict(admission=False,compiled_execution=False,
            failed_case='valid:audit-trace-cancellation',failed_component=6,
            original_cli_exit=1,original_complete_comparison_exact=True,
            original_tests=6,outcome='failed',parity_passed=True))

    def test_packet_manifest_and_export_ignore_current_engine(self):
        folder=ROOT/'catalogue/source-replays/sand-negative-v1'
        manifest=json.loads((folder/'manifest.json').read_bytes())
        for name,pin in manifest['files'].items():
            self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),pin,name)
        spec=json.loads((ROOT/REGISTRY).read_bytes());record=spec['replays']['sand-negative']
        names=[REGISTRY,record['capsule']['path'],*(x['path'] for x in record['documents'])]
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)
            for name in names:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((ROOT/name).read_bytes())
            for name in ('cpp/include/atlas/tensor.hpp','tools/research_rate_observations.py'):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text('current file deliberately replaced')
            result=registered(root,REGISTRY,'sand-negative')
            self.assertEqual(json.loads(result['stdout'])['outcome'],'failed')
            self.assertFalse((root/'.git').exists())


if __name__=='__main__':unittest.main()
