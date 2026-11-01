"""Preserve bytes, references and mutable work during local archive consolidation."""
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

from tools.artifact_store import STORE, apply, contained, detach, digest, plan, verify


class ArtifactStoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root/'archive').mkdir()

    def write(self, name, content=b'immutable numerical evidence\n'*100):
        path = self.root/'archive'/name
        path.write_bytes(content)
        return path

    def scan(self, **kwargs):
        return plan(self.root, ['archive'], minimum_bytes=1, minimum_age_hours=0, **kwargs)

    def test_consolidation_preserves_paths_hashes_and_private_permissions(self):
        a, b = self.write('a.json'), self.write('b.json')
        a.chmod(0o600); b.chmod(0o600)
        sha = digest(a)
        document = self.scan()
        receipt = apply(document, self.root/'receipt.json')
        self.assertEqual(verify(receipt), {'complete':True, 'verified_paths':2, 'verified_objects':1})
        self.assertEqual(digest(a), sha)
        self.assertEqual(digest(b), sha)
        self.assertEqual(a.stat().st_ino, b.stat().st_ino)
        self.assertEqual(stat.S_IMODE(a.stat().st_mode), 0o400)
        self.assertFalse(a.is_symlink())
        self.assertEqual(self.scan()['groups'], [])  # Existing hard links need no further work.

    def test_detaching_allows_private_edits_without_mutating_other_evidence(self):
        a, b = self.write('a.json'), self.write('b.json')
        receipt = apply(self.scan(), self.root/'receipt.json')
        sha = digest(b)
        detach(self.root, 'archive/a.json')
        a.write_bytes(b'new independent result')
        self.assertNotEqual(a.stat().st_ino, b.stat().st_ino)
        self.assertEqual(digest(b), sha)
        self.assertEqual(digest(self.root/receipt['entries'][0]['object']), sha)
        with self.assertRaises(ValueError): detach(self.root, receipt['entries'][0]['object'])

    def test_future_snapshot_reuses_the_existing_object(self):
        a = self.write('a.json'); self.write('b.json')
        apply(self.scan(), self.root/'first-receipt.json')
        c = self.write('new-snapshot.json')
        document = self.scan()
        self.assertEqual(len(document['groups']), 1)
        self.assertTrue(document['groups'][0]['object_exists'])
        self.assertEqual(len(document['groups'][0]['entries']), 1)
        receipt = apply(document, self.root/'next-receipt.json')
        self.assertEqual(verify(receipt)['verified_paths'],1)
        self.assertEqual(a.stat().st_ino,c.stat().st_ino)

    def test_tracked_code_symlinks_and_existing_hardlinks_are_untouched(self):
        tracked = self.write('tracked.json')
        subprocess.run(['git','-C',str(self.root),'add','archive/tracked.json'], check=True)
        executable = self.write('executable.json'); executable.chmod(0o755)
        code = self.write('source.py')
        shared = self.write('shared.json'); os.link(shared, self.root/'outside.json')
        symlink = self.root/'archive/link.json'; symlink.symlink_to(tracked)
        self.write('a.json'); self.write('b.json')
        before = {p:p.lstat() for p in [tracked, executable, code, shared, symlink]}
        receipt = apply(self.scan(), self.root/'receipt.json')
        self.assertEqual(len(receipt['entries']),2)
        for path, old in before.items(): self.assertEqual(path.lstat(), old)

    def test_recent_and_different_files_are_not_frozen(self):
        a = self.write('a.json'); self.write('b.json')
        self.assertEqual(plan(self.root,['archive'],minimum_bytes=1,minimum_age_hours=2)['groups'],[])
        self.write('b.json', b'different bytes of a different length')
        self.assertEqual(self.scan()['groups'],[])
        self.assertTrue(a.stat().st_mode & 0o200)

    def test_changed_file_rejects_whole_plan_before_any_mutation(self):
        a, b = self.write('a.json'), self.write('b.json')
        document = self.scan()
        b.write_bytes(b'new work')
        with self.assertRaises(ValueError):apply(document,self.root/'receipt.json')
        self.assertTrue(a.stat().st_mode & 0o200)
        self.assertFalse((self.root/STORE).exists())

    def test_read_access_policies_do_not_get_widened(self):
        a, b = self.write('a.json'), self.write('b.json')
        a.chmod(0o600); b.chmod(0o644)
        self.assertEqual(self.scan()['groups'],[])

    def test_paths_cannot_escape_or_follow_symlinked_parents(self):
        (self.root/'alias').symlink_to(self.root/'archive',target_is_directory=True)
        for relative in ['../escape.json','alias/a.json', str(self.root/'archive/a.json')]:
            with self.subTest(relative=relative),self.assertRaises(ValueError):contained(self.root,relative)

    def test_corrupt_canonical_object_is_detected(self):
        self.write('a.json'); self.write('b.json')
        receipt = apply(self.scan(),self.root/'receipt.json')
        obj = self.root/receipt['entries'][0]['object']
        obj.chmod(0o600);obj.write_bytes(b'corrupt')
        with self.assertRaises(ValueError):verify(receipt)
