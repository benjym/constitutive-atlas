"""Meaningful corruption checks; use importlib only to test staging in isolation."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from atlas.evidence import checked_receipt,verify_manifest_files

class ArchiveReceiptTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve()
  self.original='atlas/dsl.py';self.document='catalogue/investigations/example/manifest.json';self.pin=hashlib.sha256(b'old').hexdigest()
  self.archive='catalogue/source-snapshots/'+self.pin+'/'+self.original
  self.put(self.original,b'new');self.put(self.archive,b'old')
  self.doc={'files':{self.original:self.pin}};self.put(self.document,json.dumps(self.doc).encode())
  self.sidecar=Path(self.document).parent/'source-archive-map.json'
  self.mapping={'version':'immutable-source-archive-map-0.1','documents':{self.document:hashlib.sha256((self.root/self.document).read_bytes()).hexdigest()},'entries':[{'original_path':self.original,'sha256':self.pin,'archived_path':self.archive}]};self.save()
 def put(self,path,bytes):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(bytes)
 def save(self):self.put(self.sidecar,json.dumps(self.mapping).encode())
 def check(self):return checked_receipt(self.root,self.document,self.original,self.pin)
 def test_archival_identity_does_not_require_live_identity(self):
  self.assertEqual(self.check(),self.root/self.archive);self.assertEqual(verify_manifest_files(self.root,self.document),self.doc)
 def test_live_unchanged_source(self):
  (self.root/self.sidecar).unlink();self.put(self.original,b'old');self.assertEqual(self.check(),self.root/self.original)
 def test_missing_or_corrupt_archive_does_not_fallback(self):
  self.put(self.original,b'old');self.put(self.archive,b'wrong')
  with self.assertRaises(ValueError):self.check()
  (self.root/self.archive).unlink()
  with self.assertRaises(ValueError):self.check()
 def test_changed_manifest_rejected_even_for_unredirected_file(self):
  self.put(self.document,b'{}')
  with self.assertRaises(ValueError):self.check()
 def test_wrong_path_hash_binding_and_duplicates(self):
  for field,bad in [('original_path','atlas/model.py'),('sha256','0'*64),('archived_path','catalogue/elsewhere')]:
   old=self.mapping['entries'][0][field];self.mapping['entries'][0][field]=bad;self.save()
   with self.subTest(field=field),self.assertRaises(ValueError):self.check()
   self.mapping['entries'][0][field]=old
  self.mapping['entries']*=2;self.save()
  with self.assertRaises(ValueError):self.check()
 def test_missing_mapping_and_escape_rejected(self):
  self.mapping['documents']={};self.save()
  with self.assertRaises(ValueError):self.check()
  for document,path in [('../outside','atlas/dsl.py'),(self.document,'../outside'),(self.document,'/absolute')]:
   with self.assertRaises(ValueError):checked_receipt(self.root,document,path,self.pin)
 def test_sibling_receipt_requires_explicit_document_binding(self):
  sibling='catalogue/investigations/example/second-receipt.json'
  self.put(sibling,json.dumps(self.doc).encode())
  with self.assertRaises(ValueError):checked_receipt(self.root,sibling,self.original,self.pin)
  self.mapping['documents'][sibling]=hashlib.sha256((self.root/sibling).read_bytes()).hexdigest();self.save()
  self.assertEqual(checked_receipt(self.root,sibling,self.original,self.pin),self.root/self.archive)
  self.put(sibling,json.dumps(self.doc,indent=2).encode())
  with self.assertRaises(ValueError):checked_receipt(self.root,sibling,self.original,self.pin)
 def test_call_cannot_replace_document_pin_with_current_hash(self):
  current=hashlib.sha256(b'new').hexdigest()
  with self.assertRaises(ValueError):checked_receipt(self.root,self.document,self.original,current)
 def test_archive_symlink_escape_rejected(self):
  outside=Path(self.temp.name).parent/(Path(self.temp.name).name+'-outside');outside.write_bytes(b'old');self.addCleanup(outside.unlink)
  p=self.root/self.archive;p.unlink();p.symlink_to(outside)
  with self.assertRaises(ValueError):self.check()
class RepositoryArchiveCoverageTests(unittest.TestCase):
 def test_migration_inventory_replays_original_receipts(self):
  from atlas.model import ROOT
  inventory=json.loads((ROOT/'catalogue/investigations/symmetric-expm-v1/source-migration-inventory.json').read_text())
  self.assertEqual(inventory['reference_count'],len(inventory['references']))
  for row in inventory['references']:
   with self.subTest(document=row['document'],path=row['original_path']):
    self.assertEqual(hashlib.sha256((ROOT/row['document']).read_bytes()).hexdigest(),row['document_sha256'])
    resolved=checked_receipt(ROOT,row['document'],row['original_path'],row['sha256'])
    self.assertEqual(resolved,(ROOT/row['archived_path']).resolve())
 def test_every_sibling_file_manifest_has_explicit_document_binding(self):
  from atlas.model import ROOT
  for sidecar in sorted((ROOT/'catalogue').rglob('source-archive-map.json')):
   mapping=json.loads(sidecar.read_text())
   for receipt in sorted(sidecar.parent.glob('*.json')):
    if receipt==sidecar:continue
    document=json.loads(receipt.read_text())
    if isinstance(document,dict)and(isinstance(document.get('files'),dict)or isinstance(document.get('dependencies'),dict)or(document and all(isinstance(h,str)and len(h)==64 and all(c in '0123456789abcdef'for c in h)for h in document.values()))):
     relative=receipt.relative_to(ROOT).as_posix()
     with self.subTest(document=relative):
      self.assertIn(relative,mapping['documents'])
      self.assertEqual(hashlib.sha256(receipt.read_bytes()).hexdigest(),mapping['documents'][relative])
if __name__=='__main__':unittest.main()
