from pathlib import Path
import hashlib,json,sys,shutil
ROOT=Path('/Users/bmar5496/code/constitutive-atlas')
STAGE=Path('/private/tmp/atlas-spectral-dsl-binding-audit-v1')
OUT=ROOT/'docs/reviews/spectral-dsl-source-bindings-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
manifest=read(STAGE/'manifest.json')
for path,record in manifest['files'].items():
 b=(STAGE/path).read_bytes();assert sha(b)==record['sha256'] and len(b)==record['bytes'],path
plan=read(STAGE/'supplement.json')['current_archive_plan']
assert not OUT.exists()
# Preflight every input before mutation.
for row in plan:
 assert sha((ROOT/row['document']).read_bytes())==row['document_sha256']
 if row['sidecar_exists']:assert sha((ROOT/row['sidecar']).read_bytes())==row['sidecar_sha256']
 else:assert not (ROOT/row['sidecar']).exists()
 for pair in row['bindings']:
  assert sha((ROOT/pair['original_path']).read_bytes())==pair['sha256']
  dest=ROOT/pair['canonical_archive']
  if dest.exists():assert sha(dest.read_bytes())==pair['sha256']
# Copy the unmodified reviewed audit, including pre-mutation map snapshots.
shutil.copytree(STAGE,OUT/'audit')
written=[]
def preserve(original,expected):
 src=ROOT/original;b=src.read_bytes();assert sha(b)==expected
 dest=ROOT/'catalogue/source-snapshots'/expected/original
 if dest.exists():assert dest.read_bytes()==b
 else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);written.append(dest.relative_to(ROOT).as_posix())
for row in plan:
 if row['sidecar_exists']:preserve(row['sidecar'],row['sidecar_sha256'])
 for pair in row['bindings']:preserve(pair['original_path'],pair['sha256'])
maps={};additional=[]
for row in plan:
 name=row['sidecar'];p=ROOT/name
 if name not in maps:
  maps[name]=read(p) if p.exists() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
  assert maps[name]['version']=='immutable-source-archive-map-0.1'
  # New sidecars must not invalidate other direct sibling receipt documents.
  if not p.exists():
   for sibling in sorted(p.parent.glob('*.json')):
    rel=sibling.relative_to(ROOT).as_posix();pin=sha(sibling.read_bytes())
    maps[name]['documents'][rel]=pin
    if not any(x['document']==rel for x in plan):additional.append({'document':rel,'sha256':pin,'sidecar':name})
 mapping=maps[name]
 old=mapping['documents'].get(row['document']);assert old is None or old==row['document_sha256']
 mapping['documents'][row['document']]=row['document_sha256']
 for pair in row['bindings']:
  entry={'original_path':pair['original_path'],'sha256':pair['sha256'],'archived_path':pair['canonical_archive']}
  same=[e for e in mapping['entries'] if e['original_path']==entry['original_path'] and e['sha256']==entry['sha256']]
  assert not same or same==[entry]
  if not same:mapping['entries'].append(entry)
for name,mapping in maps.items():(ROOT/name).write_text(json.dumps(mapping,indent=2)+'\n')
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
checks=[]
for row in plan:
 for pair in row['bindings']:
  path=checked_receipt(ROOT,row['document'],pair['original_path'],pair['sha256'])
  assert path==ROOT/pair['canonical_archive']
  checks.append({'document':row['document'],'source':pair['original_path'],'sha256':pair['sha256'],'resolved':path.relative_to(ROOT).as_posix()})
report={'scope':'Exact source identity preservation before spectral DSL edits; no numerical observations or new model admission.', 'checked_current_bindings':checks,'changed_sidecars':sorted(maps),'new_snapshots':written,'additional_new_sidecar_sibling_document_pins':additional,'historical_unresolved_pairs_expected':11}
(OUT/'archive-checks.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copyfile(__file__,OUT/'preserve.py')
print(json.dumps({'bindings':len(checks),'documents':len(plan),'maps':len(maps),'snapshots':len(written),'additional_sibling_pins':len(additional)}))
