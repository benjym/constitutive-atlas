"""Finish verification after the retained scanner's metadata-shape mismatch."""
from pathlib import Path
import hashlib,json,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((OUT/'frozen/bindings-before.json').read_text());plan=json.loads((OUT/'planned-preservation.json').read_text());pins={r['document']:r['document_sha256'] for r in before['primary_references']+before['secondary_source_map_references']}
checks=[]
for row in plan['bindings']:
 doc,path,h=row['document'],row['original_path'],row['sha256'];assert sha(ROOT/doc)==pins[doc]
 archive=ROOT/row['archived_path'];assert sha(archive)==h
 try:
  assert checked_receipt(ROOT,doc,path,h)==archive;kind='checked-receipt'
 except ValueError as e:
  assert str(e)=='source path/hash pair absent from original receipt document'
  refs=[r for r in before['secondary_source_map_references'] if r['document']==doc and r['original_path']==path and r['sha256']==h];assert len(refs)==1
  assert all(loc['shape']=='original_path-object' for loc in refs[0]['locations'])
  # Historical diagnostic metadata is not a primary checked_receipt document.
  kind='secondary-original-path-metadata-exact-canonical-archive'
 checks.append(dict(row,verification=kind))
(OUT/'preservation.json').write_text(json.dumps({'bindings':checks,'changed_sidecars':plan['sidecars'],'original_documents_unchanged':True,'retained_initial_failure':'preservation.log','scope':'Exact sources/sidecars; checked primary receipts distinguished from original_path-only diagnostic metadata'},indent=2)+'\n');print(json.dumps({'bindings':len(checks),'metadata_shapes':sum(r['verification']!='checked-receipt' for r in checks)}))
