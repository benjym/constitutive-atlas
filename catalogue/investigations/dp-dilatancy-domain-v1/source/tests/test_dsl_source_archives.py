"""Original DSL/compiler receipt identity survives current code evolution."""
import json,shutil,tempfile,unittest
from pathlib import Path
from atlas.evidence import checked_receipt
ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/'catalogue/source-replays/dsl-identity-v1/inventory.json'
class DslSourceArchives(unittest.TestCase):
 def test_all_original_bindings_resolve_exact_archives(self):
  data=json.loads(INVENTORY.read_text())
  self.assertEqual(len(data['references']),42)
  for row in data['references']+data['secondary_source_map_references']:
   with self.subTest(document=row['document'],source=row['original_path']):
    self.assertEqual(checked_receipt(ROOT,row['document'],row['original_path'],row['sha256']),(ROOT/row['archived_path']).resolve())
 def test_missing_archive_never_falls_back_to_matching_live_bytes(self):
  rows=json.loads(INVENTORY.read_text())['references']
  for source in ['atlas/dsl.py','atlas/compiler.py']:
   row=next(x for x in rows if x['original_path']==source)
   with self.subTest(source=source),tempfile.TemporaryDirectory()as tmp:
    root=Path(tmp)
    for name in [row['document'],row['sidecar']]:
     p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
    p=root/source;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['archived_path'],p)
    with self.assertRaises(ValueError):checked_receipt(root,row['document'],source,row['sha256'])
