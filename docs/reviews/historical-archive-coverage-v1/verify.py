"""Verify additive archive repair and preserved receipts; no backend calls."""
from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
for p,h in read(D/'manifest.json')['files'].items():assert sha(D/p)==h,p
plan=read(D/'plan.json');repair=read(D/'repair.json')
for row in plan['documents']:assert sha(R/row['document'])==row['document_sha256'],row['document']
for path,pin in repair['new_maps'].items():
 current=R/path;new=read(current)
 assert sha(current)==pin,path
 oldpin=plan['old_maps'][path]
 if oldpin:
  archived=R/'catalogue/source-snapshots'/oldpin/path
  assert sha(archived)==oldpin;old=read(archived)
  assert all(new['documents'].get(k)==v for k,v in old['documents'].items())
  assert all(e in new['entries']for e in old['entries'])
for row in plan['documents']:assert read(R/row['sidecar'])['documents'][row['document']]==row['document_sha256']
for row in plan['affected_reverse_references']:
 if row['resolution']=='checked':assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256']
 elif row['resolution'].startswith('descriptive-'):
  assert sha(R/'catalogue/source-snapshots'/row['sha256']/row['original_path'])==row['sha256']
 else:raise AssertionError('Unexpected originally unresolved affected edge')
for row in plan['test_source']['receipts']:
 assert checked_receipt(R,row['document'],row['original_path'],row['sha256'])==R/'catalogue/source-snapshots'/row['sha256']/row['original_path']
assert sha(R/'tests/test_evidence_archives.py')==repair['new_test_sha256']
print('26 original documents, 57 reverse references, 4 old-test bindings and additive map semantics verified. No backend executed.')
