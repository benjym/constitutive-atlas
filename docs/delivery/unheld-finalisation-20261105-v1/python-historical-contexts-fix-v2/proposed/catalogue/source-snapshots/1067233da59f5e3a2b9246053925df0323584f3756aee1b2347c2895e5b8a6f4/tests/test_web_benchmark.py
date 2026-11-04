"""The benchmark page must bind historical inputs and exclude private records."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.build_benchmark import ROOT, PACKET, FILES, bundle, digest


class BenchmarkSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'site'

    def test_historical_identity_public_allowlist_and_stale_cleanup(self):
        pins = bundle(self.output)
        target = self.output / 'benchmark-tmd2'
        self.assertEqual(set(pins), set(FILES) | {'model.json'})
        self.assertEqual(pins['model.json'], '83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86')
        for name, source in FILES.items():
            self.assertEqual((target / name).read_bytes(), (ROOT / PACKET / source).read_bytes())
        page = (self.output / 'tmd2.html').read_text()
        self.assertIn('Independent scientific review remains pending', page)
        self.assertIn('0.975', page)
        self.assertNotIn('0.975289261', page)  # Private measured void ratio in case.json.
        self.assertNotIn('100022.10666666666', page)  # Private first-row stress.
        (target / 'stale-private-record.json').write_text('not a public asset')
        self.assertEqual(bundle(self.output), pins)
        self.assertEqual(set(p.name for p in target.iterdir()), set(pins))

    def fixture(self):
        root = Path(self.temp.name) / 'fixture'
        packet = root / PACKET
        packet.mkdir(parents=True)
        for name in set(FILES.values()) | {'packet-manifest.json', 'source-manifest.json', 'source.tar.gz', 'inputs/case.json'}:
            dest = packet / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / PACKET / name, dest)
        return root, packet

    def test_corrupt_input_fails_before_public_output(self):
        root, packet = self.fixture()
        (packet / 'inputs/parameter-set.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            bundle(self.output, root)
        self.assertFalse(self.output.exists())

    def test_correct_hash_does_not_hide_request_binding_mismatch(self):
        root, packet = self.fixture()
        path = packet / 'inputs/requests.json'
        requests = json.loads(path.read_text())
        requests[0]['initial'][6] = .98
        path.write_text(json.dumps(requests))
        manifest = packet / 'packet-manifest.json'
        pins = json.loads(manifest.read_text())
        pins['inputs/requests.json'] = digest(path.read_bytes())
        manifest.write_text(json.dumps(pins))
        with self.assertRaisesRegex(ValueError, 'request/input binding'):
            bundle(self.output, root)
        self.assertFalse(self.output.exists())

    def test_live_model_not_used_and_non_allowlisted_siblings_not_read(self):
        root, packet = self.fixture()
        (root / 'models').mkdir()
        (root / 'models/hypoplastic-sand-igs97.json').write_text('changed live defaults')
        (packet / 'private-measurements.json').write_text('PRIVATE_SENTINEL')
        pins = bundle(self.output, root)
        self.assertEqual(pins['model.json'], '83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86')
        self.assertNotIn('private-measurements.json', pins)
