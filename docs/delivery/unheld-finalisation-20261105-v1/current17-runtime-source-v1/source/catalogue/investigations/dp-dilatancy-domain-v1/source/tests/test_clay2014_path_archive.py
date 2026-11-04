"""The new solver target must not invalidate original instantaneous-rate receipts."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from atlas.evidence import checked_receipt
from atlas.model import ROOT
class Clay2014PathArchive(unittest.TestCase):
    def test_retained_migration_resolves_original_receipt(self):
        packet=ROOT/'catalogue/investigations/clay2014-paths-v1'
        inventory=json.loads((packet/'source-migration-inventory.json').read_text())
        for row in inventory['references']:
            self.assertEqual(hashlib.sha256((ROOT/row['document']).read_bytes()).hexdigest(),row['document_sha256'])
            self.assertEqual(checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']),(ROOT/row['archived_path']).resolve())
    def test_corrupt_snapshot_or_original_document_never_falls_back(self):
        row=json.loads((ROOT/'catalogue/investigations/clay2014-paths-v1/source-migration-inventory.json').read_text())['references'][0]
        folder=Path(row['document']).parent
        for mode in ('changed-live','missing','corrupt','document'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)
                for relative in (row['document'],(folder/'source-archive-map.json').as_posix(),row['archived_path']):
                    target=root/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/relative).read_bytes())
                (root/'CMakeLists.txt').write_bytes((ROOT/row['archived_path']).read_bytes())
                if mode=='changed-live':
                    (root/'CMakeLists.txt').write_text('new source')
                    self.assertEqual(checked_receipt(root,row['document'],row['original_path'],row['sha256']),(root/row['archived_path']).resolve());continue
                if mode=='missing':(root/row['archived_path']).unlink()
                elif mode=='corrupt':(root/row['archived_path']).write_text('corrupt')
                else:(root/row['document']).write_bytes((root/row['document']).read_bytes()+b' ')
                with self.assertRaises(ValueError):checked_receipt(root,row['document'],row['original_path'],row['sha256'])
