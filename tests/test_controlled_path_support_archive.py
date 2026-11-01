"""Packaging must preserve exact reviewed support bytes across policy updates."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import build_controlled_path_web as host


class ControlledPathSupportArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = 'docs/MODEL_DELIVERY_CHECKLIST.md'
        self.review = 'catalogue/agent-reviews/example.json'
        self.old = b'original reviewed policy'
        self.digest = hashlib.sha256(self.old).hexdigest()
        self.approval = {'review': {'path': self.review}, 'supporting_files': [{'path': self.path, 'sha256': self.digest}]}
        self.put(self.path, self.old)
        self.put(self.review, json.dumps({'artifacts': self.approval['supporting_files']}).encode())
        self.archive = 'catalogue/source-snapshots/' + self.digest + '/' + self.path
        self.sidecar = 'catalogue/agent-reviews/source-archive-map.json'
        self.root_patch = patch.object(host, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def put(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def archive_original(self):
        self.put(self.archive, self.old)
        self.put(self.path, b'new policy')
        self.put(self.sidecar, json.dumps({'version': 'immutable-source-archive-map-0.1',
            'documents': {self.review: hashlib.sha256((self.root / self.review).read_bytes()).hexdigest()},
            'entries': [{'original_path': self.path, 'sha256': self.digest, 'archived_path': self.archive}]}).encode())

    def test_exact_current_support_passes(self):
        host.validate_supporting_files(self.approval)

    def test_reviewed_original_passes_after_policy_update(self):
        self.archive_original()
        host.validate_supporting_files(self.approval)

    def test_changed_live_without_archive_rejects(self):
        self.put(self.path, b'new policy')
        with self.assertRaises(ValueError):
            host.validate_supporting_files(self.approval)

    def test_corrupt_or_missing_archive_never_falls_back_to_matching_live(self):
        self.archive_original()
        self.put(self.path, self.old)
        self.put(self.archive, b'corrupt')
        with self.assertRaises(ValueError):
            host.validate_supporting_files(self.approval)
        (self.root / self.archive).unlink()
        with self.assertRaises(ValueError):
            host.validate_supporting_files(self.approval)

    def test_changed_review_document_rejects(self):
        self.archive_original()
        with (self.root / self.review).open('ab') as stream:
            stream.write(b' ')
        with self.assertRaises(ValueError):
            host.validate_supporting_files(self.approval)

    def test_unpinned_support_hash_rejects_even_if_live_matches(self):
        other = b'new policy'
        self.put(self.path, other)
        self.approval['supporting_files'][0]['sha256'] = hashlib.sha256(other).hexdigest()
        with self.assertRaises(ValueError):
            host.validate_supporting_files(self.approval)
