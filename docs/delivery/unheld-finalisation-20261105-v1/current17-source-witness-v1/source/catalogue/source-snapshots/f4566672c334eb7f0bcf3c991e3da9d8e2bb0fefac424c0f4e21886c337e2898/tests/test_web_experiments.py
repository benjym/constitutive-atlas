"""Synthetic tests for reproducible experiment assets and release isolation."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.build_experiments import bundle, encode
from test_data import TMD, TMU
from atlas.data import normalize_member


class BrowserBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'data/raw').mkdir(parents=True)
        self.archive = self.root/'data/raw/synthetic.zip'
        with zipfile.ZipFile(self.archive, 'w') as archive:
            archive.writestr('TMD1.dat', TMD)
            archive.writestr('TMU1.dat', TMU)
        self.digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.write('sources.json', dict(sources=[dict(filename='synthetic.zip', sha256=self.digest)]))
        self.write('experiment_releases.json', dict(schema_version='0.1', grants=[]))
        self.output = self.root/'site/experiments'

    def write(self, name, data):
        (self.root/'data'/name).write_text(json.dumps(data))

    def grant(self, **changes):
        grant = dict(archive_sha256=self.digest, public_hosting=True, evidence='Synthetic test fixture created in this test',
                     recorded_at='2026-10-30', scope='Public hosting of synthetic test fixture', attribution='Synthetic data')
        grant.update(changes)
        self.write('experiment_releases.json', dict(schema_version='0.1', grants=[grant]))

    def test_public_build_excludes_pending_measurements_even_when_cached(self):
        bundle(self.output, preview=True, root=self.root)
        self.archive.unlink()  # Clean public builds do not need unapproved source archives.
        manifest = bundle(self.output, root=self.root)
        self.assertEqual(manifest['experiments'], [])
        self.assertEqual(list(self.output.iterdir()), [self.output/'index.json'])

    def test_preview_and_approved_public_builds_are_deterministic(self):
        preview = bundle(self.output, preview=True, root=self.root)
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        bundle(self.output, preview=True, root=self.root)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})
        self.assertEqual(preview['release'], 'local-preview')
        self.assertEqual(len(preview['experiments']), 2)
        self.grant()
        public = bundle(self.output, root=self.root)
        self.assertEqual(public['release'], 'public')
        for entry in public['experiments']:
            content = (self.output/entry['path']).read_bytes()
            self.assertEqual(len(content), entry['size_bytes'])
            self.assertEqual(hashlib.sha256(content).hexdigest(), entry['sha256'])
            data = json.loads(content)
            self.assertNotIn('normalized_at', data['metadata']['provenance'])
            self.assertEqual(data['metadata']['provenance']['attribution'], 'Synthetic data')

    def test_incomplete_grant_and_changed_archive_rejected(self):
        self.grant(evidence='')
        with self.assertRaisesRegex(ValueError, 'evidence'):
            bundle(self.output, root=self.root)
        self.grant()
        self.archive.write_bytes(b'changed source')
        with self.assertRaisesRegex(ValueError, 'pinned source'):
            bundle(self.output, root=self.root)

    def test_plotted_channels_preserve_every_value_and_order(self):
        for raw, name in [(TMD, 'TMD1.dat'), (TMU, 'TMU1.dat')]:
            record = normalize_member(raw, name, 'a'*64, 'b'*64)
            packed = encode(record)
            self.assertEqual(len(packed['values']), len(record['rows']))
            for original, values in zip(record['rows'], packed['values']):
                self.assertEqual(values, [original[c] for c in packed['columns']])
            if name.startswith('TMU'):
                self.assertNotIn('volumetric_strain', packed['columns'])
                self.assertNotIn('void_ratio', packed['metadata']['initial'])
