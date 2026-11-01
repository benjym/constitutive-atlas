from pathlib import Path
import json,hashlib,sys,tempfile,subprocess
H=Path(__file__).resolve().parent;R=H.parents[5];sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
P=R/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/header-fix-v1/preservation-v2'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(P/'SOURCE_FREEZE.json');assert sha(P/'SOURCE_FREEZE.json')=='f745753993ffee01c3cc1bea0c896461eec8d4658809353caa834a543b57b10b'
for row in f['files']:assert sha(R/row['original_path'])==row['old_sha256']
p=load(P/'PROPOSAL.json')
assert sha(R/p['source']['original_path'])==p['source']['old_sha256']=='b45122369222a0baf7dd4f4f049c534d961e31a9bda8945cfb008dbca5a21f71'
assert sha(P/p['source']['future_copy'])==p['source']['new_sha256']=='9612893e73052b905959d47affd535404f355986d27b2088c204857b53b55a4b'
source_review=P.parent/'header-source-review/review-receipt.json'
assert sha(source_review)=='704da5bdcfe6d8b98ac1cb0c6cba6ce1e54bad947f8677bc2e6ceda5925c40c8'
r=load(source_review);assert r['status']=='accepted'
virtual={p['source']['original_path']:P/p['source']['future_copy']}
for row in p['maps']:
 live=R/row['original_path'];assert (sha(live) if live.exists() else None)==row['old_sha256'];candidate=P/row['candidate'];assert sha(candidate)==row['new_sha256'];virtual[row['original_path']]=candidate
 if live.exists():
  old=load(live);new=load(candidate);assert all(new['documents'].get(k)==v for k,v in old['documents'].items());assert all(e in new['entries'] for e in old['entries'])
for row in p['archives']:
 candidate=P/row['snapshot'];assert sha(candidate)==row['old_sha256'];virtual[row['canonical_archive']]=candidate
 live=R/row['canonical_archive']
 assert (sha(live)==row['old_sha256']) if row['already_present'] else not live.exists()
with tempfile.TemporaryDirectory(dir=H) as d:
 d=Path(d)
 def copy(name):
  dest=d/name
  if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(virtual.get(name,R/name).read_bytes())
 for row in p['checks']:
  assert row['outcome']=='passed';doc=row['document'];name=row['original_path'];digest=row['old_sha256'];copy(doc)
  side=str(Path(doc).parent/'source-archive-map.json')
  if side in virtual or (R/side).exists():
   copy(side);m=load(d/side);matches=[e for e in m['entries'] if e['original_path']==name and e['sha256']==digest]
   selected=matches[0]['archived_path'] if matches else name
  else:selected=name
  copy(selected);checked_receipt(d,doc,name,digest)
assert len(p['checks'])==19 and len(p['maps'])==10 and len(p['archives'])==3
(H/'RESULTS.json').write_text(json.dumps(dict(status='passed',preservation_checks=19,maps=10,archives=3,scope='Prospective preservation review; separate root-code review accepted; no installation or numerical gate changes'),indent=2)+'\n')
print('PASS source identities, additive metadata,19 actual receipt checks')
import importlib.util
spec=importlib.util.spec_from_file_location('pair_source',R/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/shared-hook-install-v1/revision-v3/plan_preservation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
expected={(r['original_path'],r['old_sha256']) for r in p['archives']};covered={(r['document'],r['original_path'],r['old_sha256']) for r in p['checks']}
skip=(P.parent.relative_to(R).as_posix()+'/', 'catalogue/source-snapshots/')
# Independently scan the previously omitted active installation directories too.
seen=[];scanned=0;missing=[]
for base in ['docs','catalogue']:
 for f in (R/base).rglob('*.json'):
  name=f.relative_to(R).as_posix()
  if name.startswith(skip) or f.name=='source-archive-map.json':continue

  try:obj=load(f)
  except (ValueError,UnicodeDecodeError):continue
  scanned+=1
  for path,h in mod.pairs(obj)&expected:
   if (name,path,h) not in covered:missing.append(dict(document=name,original_path=path,old_sha256=h))
   seen.append((name,path,h))
w=load(P/'APPLY_WHITELIST.json')
assert len(w['metadata_writes'])==13 and w['source_replacement']==p['source']
assert {r['original_path']:r['new_sha256'] for r in w['metadata_writes']}==({r['original_path']:r['new_sha256'] for r in p['maps']}|{r['canonical_archive']:r['old_sha256'] for r in p['archives'] if not r['already_present']})
r=load(H/'RESULTS.json');r.update(status='blocked' if missing else 'passed',fresh_active_documents_scanned=scanned,fresh_affected_consumers=len(seen),metadata_writes=13,uncovered_transitive_consumers=missing);(H/'RESULTS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status=r['status'],scanned=scanned,affected=len(seen),missing=missing),indent=2))
