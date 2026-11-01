"""Nonmutating narrow consumer supplement to frozen v4."""
from pathlib import Path
from collections import defaultdict,deque
import json,hashlib,shutil,sys,importlib.util,tempfile
H=Path(__file__).resolve().parent;R=H.parents[5];P=H.parent/'revision-v4';V3=H.parent/'revision-v3'
sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
spec=importlib.util.spec_from_file_location('v4',P/'rebase.py');v4=importlib.util.module_from_spec(spec);spec.loader.exec_module(v4)
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):
 p=H/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def put(n,b):
 p=H/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def main():
 oldplan=read(P/'PLAN.json');oldchecks=read(P/'CHECK_RESULTS.json')
 for row in read(P/'SOURCE_FREEZE.json')['files']:assert sha((R/row['original_path']).read_bytes())==row['old_sha256']
 for folder in ['candidates','prior-map-bytes','snapshots','receipt-bytes']:shutil.copytree(P/folder,H/folder,dirs_exist_ok=True)
 maps={r['original_path']:read(H/r['candidate']) for r in oldplan['maps']};oldmaps={n:(R/n).read_bytes() if (R/n).exists() else None for n in maps}
 for row in oldplan['maps']:assert (sha(oldmaps[row['original_path']]) if oldmaps[row['original_path']] else None)==row['old_sha256']
 archives={(r['original_path'],r['old_sha256']):(H/r['snapshot']).read_bytes() for r in oldplan['archives']}
 documents={};index=defaultdict(set);exclude=(H.parent.relative_to(R).as_posix()+'/',v4.previous.A+'profile-install-v1/','catalogue/source-snapshots/')
 for directory in ['docs','catalogue']:
  for p in sorted((R/directory).rglob('*.json')):
   n=p.relative_to(R).as_posix()
   if n.startswith(exclude):continue
   try:b=p.read_bytes();d=json.loads(b)
   except (ValueError,UnicodeDecodeError):continue
   pairs=set() if p.name=='source-archive-map.json' else v4.previous.pairs(d);documents[n]=(b,pairs)
   for pair in pairs:index[pair].add(n)
 queue=deque(archives);seen=set();obligations=[]
 while queue:
  pair=queue.popleft()
  if pair in seen:continue
  seen.add(pair);n,h=pair
  if pair not in archives:
   b=(R/n).read_bytes();assert sha(b)==h;archives[pair]=b
  for doc in sorted(index[pair]):
   b,_=documents[doc];side=(Path(doc).parent/'source-archive-map.json').as_posix()
   if side not in maps:
    oldmaps[side]=(R/side).read_bytes() if (R/side).exists() else None
    maps[side]=json.loads(oldmaps[side]) if oldmaps[side] else dict(version=v4.previous.VERSION,documents={},entries=[])
   addition=dict(version=v4.previous.VERSION,documents={doc:sha(b)},entries=[dict(original_path=n,sha256=h,archived_path=v4.previous.canonical(n,h))])
   for peer,(pb,pp) in documents.items():
    if Path(peer).parent==Path(doc).parent and pp:addition['documents'][peer]=sha(pb)
   maps[side]=v4.union(maps[side],addition)
   obligations.append(dict(document=doc,original_path=n,old_sha256=h,outcome='passed'))
   if oldmaps[side] is not None:queue.append((side,sha(oldmaps[side])))
 maprows=[]
 for n,m in sorted(maps.items()):
  b=(json.dumps(m,indent=2)+'\n').encode();prior=oldmaps[n]
  if b==prior:continue
  candidate='candidates/'+n;put(candidate,b)
  if prior is not None:put('prior-map-bytes/'+n,prior)
  maprows.append(dict(original_path=n,old_sha256=sha(prior) if prior else None,new_sha256=sha(b),candidate=candidate))
 ar=[]
 for (n,h),b in sorted(archives.items()):
  canonical=v4.previous.canonical(n,h);snapshot='snapshots/'+canonical;put(snapshot,b);exists=(R/canonical).exists()
  if exists:assert sha((R/canonical).read_bytes())==h
  ar.append(dict(original_path=n,old_sha256=h,canonical_archive=canonical,snapshot=snapshot,already_present=exists))
 priorpositive={(r['document'],r['original_path'],r['old_sha256']) for r in oldchecks['checks']}
 extra={ (r['document'],r['original_path'],r['old_sha256']):r for r in obligations if (r['document'],r['original_path'],r['old_sha256']) not in priorpositive}
 # New map documents must retain every current actual mapped-entry binding.
 priorcandidates={r['original_path']:r['new_sha256'] for r in oldplan['maps']}
 delta={r['original_path'] for r in maprows if priorcandidates.get(r['original_path'])!=r['new_sha256']}
 for side in delta:
  m=maps[side]
  for doc in m['documents']:
   if doc not in documents:continue
   for e in m['entries']:
    pair=(e['original_path'],e['sha256'])
    if pair in documents[doc][1]:extra[(doc,*pair)]=dict(document=doc,original_path=pair[0],old_sha256=pair[1],outcome='passed')
 with tempfile.TemporaryDirectory(dir=H,prefix='.overlay-') as tmp:
  overlay=Path(tmp)
  def stage(n,b):
   p=overlay/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  for row in maprows:stage(row['original_path'],(H/row['candidate']).read_bytes())
  for row in ar:stage(row['canonical_archive'],archives[(row['original_path'],row['old_sha256'])])
  for row in oldplan['replacements']:stage(row['original_path'],(R/row['future_copy']).read_bytes())
  for key,row in extra.items():
   doc,n,h=key;stage(doc,documents[doc][0]);put('receipt-bytes/'+doc,documents[doc][0])
   if not (overlay/n).exists() and (R/n).is_file():stage(n,(R/n).read_bytes())
   checked_receipt(overlay,doc,n,h)
 # End guards prevent stale proposal creation.
 for row in read(P/'SOURCE_PINS.json')['files']:assert sha((R/row['original_path']).read_bytes())==row['old_sha256'],row['original_path']
 for n,(b,_) in documents.items():assert (R/n).read_bytes()==b,n
 for n,b in oldmaps.items():assert ((R/n).read_bytes() if (R/n).exists() else None)==b,n
 writes=[dict(original_path=r['original_path'],old_sha256=r['old_sha256'],new_sha256=r['new_sha256'],operation='replace_existing_map' if r['old_sha256'] else 'create_new_map') for r in maprows]
 writes += [dict(original_path=r['canonical_archive'],old_sha256=None,new_sha256=r['old_sha256'],operation='create_canonical_snapshot') for r in ar if not r['already_present']]
 save('PLAN.json',dict(**{k:v for k,v in oldplan.items() if k not in ['maps','archives','closure']},maps=maprows,archives=ar,closure=dict(scanned_json_documents=len(documents),pairs=len(seen),obligations=len(obligations)),supplement=dict(previous_revision='revision-v4',changed_candidates=sorted(delta),new_checks=len(extra))))
 save('APPLY_WHITELIST.json',dict(writes=writes,future_source_installs=oldplan['replacements']))
 allchecks={**{(r['document'],r['original_path'],r['old_sha256']):r for r in oldchecks['checks']},**extra}
 save('CHECK_RESULTS.json',dict(**{k:v for k,v in oldchecks.items() if k not in ['checks','distinct_checked']},checks=list(allchecks.values()),distinct_checked=len(allchecks),supplement_actual_api_checks=list(extra.values())))
 save('COMPOSITION_PARTITION.json',dict(previous_revision='revision-v4',previous_freeze=sha((P/'SOURCE_FREEZE.json').read_bytes()),unchanged_v4_candidates=[n for n in maps if n not in delta],additive_candidate_deltas=sorted(delta),previous_complete_composition=read(P/'COMPOSITION_PARTITION.json')))
 pins={r['original_path']:r['old_sha256'] for r in read(P/'SOURCE_PINS.json')['files']};pins.update({n:sha(b) for n,(b,_) in documents.items()});pins.update({n:sha(b) for n,b in oldmaps.items() if b is not None})
 save('SOURCE_PINS.json',dict(files=[dict(original_path=n,old_sha256=h) for n,h in sorted(pins.items())]))
 save('SUPPLEMENT_RESULTS.json',dict(passed=True,new_checked=len(extra),checks=list(extra.values()),changed_candidates=sorted(delta),production_writes=0))
 print(json.dumps(dict(maps=len(maprows),archives=len(ar),metadata_writes=len(writes),new_checks=len(extra),total_retained_actual_checks=len(allchecks))))
if __name__=='__main__':main()
