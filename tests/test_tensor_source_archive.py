"""Tensor-only source evolution preserves original identity receipts."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from atlas.evidence import checked_receipt

ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/'catalogue/source-replays/tensor-identity-v1/inventory.json'

class TensorSourceArchive(unittest.TestCase):
    def test_every_original_binding_survives_changed_live_tensor(self):
        inventory=json.loads(INVENTORY.read_bytes())
        self.assertEqual(len(inventory['references']),21)
        for row in inventory['references']+inventory['secondary_source_map_references']:
            with self.subTest(document=row['document']),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)
                self.assertEqual(hashlib.sha256((ROOT/row['document']).read_bytes()).hexdigest(),row['document_sha256'])
                for name in (row['document'],row['sidecar'],row['archived_path']):
                    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                live=root/row['original_path'];live.parent.mkdir(parents=True,exist_ok=True);live.write_text('new tensor implementation')
                self.assertEqual(checked_receipt(root,row['document'],row['original_path'],row['sha256']),(root/row['archived_path']).resolve())

    def test_missing_corrupt_snapshot_and_changed_document_reject(self):
        row=json.loads(INVENTORY.read_bytes())['references'][0]
        for mode in ('missing','corrupt','document'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)
                for name in (row['document'],row['sidecar'],row['archived_path']):
                    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                live=root/row['original_path'];live.parent.mkdir(parents=True,exist_ok=True);live.write_bytes((ROOT/row['archived_path']).read_bytes())
                if mode=='missing':((root/row['archived_path']).resolve()).unlink()
                elif mode=='corrupt':((root/row['archived_path']).resolve()).write_text('corrupt')
                else:(root/row['document']).write_bytes((root/row['document']).read_bytes()+b' ')
                with self.assertRaises(ValueError):checked_receipt(root,row['document'],row['original_path'],row['sha256'])

if __name__=='__main__':unittest.main()
