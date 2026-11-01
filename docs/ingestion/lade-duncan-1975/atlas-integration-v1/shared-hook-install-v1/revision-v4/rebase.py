"""Nonmutating additive rebase; previous complete replay is composed with affected checks."""
from pathlib import Path
from collections import defaultdict, deque
import hashlib, json, sys, tempfile, importlib.util
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
PREV=HERE.parent/'revision-v3'
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
spec=importlib.util.spec_from_file_location('previous_planner',PREV/'plan_preservation.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
sha=lambda data:hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_bytes())
def save(name,value):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def rel(p):return p.relative_to(ROOT).as_posix()
def copy(name,data):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return p.relative_to(HERE).as_posix()
def union(base,addition):
 assert base['version']==addition['version']=='immutable-source-archive-map-0.1'
 result=json.loads(json.dumps(base))
 for k,v in addition['documents'].items():
  assert k not in result['documents'] or result['documents'][k]==v,(k,'document conflict')
  result['documents'][k]=v
 keyed={(e['original_path'],e['sha256']):e for e in result['entries']}
 assert len(keyed)==len(result['entries'])
 for e in addition['entries']:
  key=(e['original_path'],e['sha256']);assert key not in keyed or keyed[key]==e,(key,'entry conflict')
  if key not in keyed:result['entries'].append(e);keyed[key]=e
 return result

def main():
 plan=read(PREV/'PLAN.json');checks=read(PREV/'CHECK_RESULTS.json');pins=read(PREV/'SOURCE_PINS.json')
 for row in read(PREV/'SOURCE_FREEZE.json')['files']:assert sha((ROOT/row['original_path']).read_bytes())==row['old_sha256']
 frozen={r['original_path']:r['old_sha256'] for r in pins['files']}
 drift=[dict(original_path=n,old_sha256=h,current_sha256=sha((ROOT/n).read_bytes())) for n,h in frozen.items() if sha((ROOT/n).read_bytes())!=h]
 assert len(drift)==10,drift
 replacements={r['original_path']:r for r in plan['replacements']}
 for n,r in replacements.items():assert sha((ROOT/n).read_bytes())==r['old_sha256'];assert sha((ROOT/r['future_copy']).read_bytes())==r['new_sha256']
 # Every original v3 candidate and snapshot remains frozen in place.
 maps={r['original_path']:read(PREV/r['candidate']) for r in plan['maps']}
 oldmaps={n:(ROOT/n).read_bytes() if (ROOT/n).exists() else None for n in maps}
 merges=[]
 for n,mapping in list(maps.items()):
  current=oldmaps[n]
  if current is not None:
   maps[n]=union(json.loads(current),mapping)
   oldrow=next(r for r in plan['maps'] if r['original_path']==n)
   if sha(current)!=oldrow['old_sha256']:
    if oldrow['old_sha256'] is not None:
     before=json.loads((PREV/'prior-map-bytes'/n).read_bytes())
     assert union(json.loads(current),before)==json.loads(current),'peer changed old data'
    merges.append(n)
 assert len(merges)==8,merges
 archives={(r['original_path'],r['old_sha256']):(PREV/r['snapshot']).read_bytes() for r in plan['archives']}
 documents={};index=defaultdict(set);excluded=rel(HERE.parent)+'/'
 for directory in ['docs','catalogue']:
  for p in sorted((ROOT/directory).rglob('*.json')):
   n=rel(p)
   if n.startswith(excluded) or n.startswith('catalogue/source-snapshots/') or n.startswith(previous.A+'profile-install-v1/'):continue
   try:data=p.read_bytes();v=json.loads(data)
   except (ValueError,UnicodeDecodeError):continue
   pairs=set() if p.name=='source-archive-map.json' else previous.pairs(v)
   documents[n]=(data,pairs)
   for pair in pairs:index[pair].add(n)
 queue=deque(archives);seen=set();obligations=[]
 # Existing current maps about to change need their own exact historical preservation.
 for n,data in oldmaps.items():
  if data is not None:queue.append((n,sha(data)))
 while queue:
  pair=queue.popleft()
  if pair in seen:continue
  seen.add(pair);n,h=pair
  if pair not in archives:
   data=(ROOT/n).read_bytes();assert sha(data)==h;archives[pair]=data
  for doc in sorted(index[pair]):
   data,_=documents[doc];side=(Path(doc).parent/'source-archive-map.json').as_posix()
   if side not in maps:
    oldmaps[side]=(ROOT/side).read_bytes() if (ROOT/side).exists() else None
    maps[side]=json.loads(oldmaps[side]) if oldmaps[side] else dict(version=previous.VERSION,documents={},entries=[])
   addition=dict(version=previous.VERSION,documents={doc:sha(data)},entries=[dict(original_path=n,sha256=h,archived_path=previous.canonical(n,h))])
   # Preserve all recognized current documents gated by this sidecar.
   for peer,(raw,pairs) in documents.items():
    if Path(peer).parent==Path(doc).parent and pairs:addition['documents'][peer]=sha(raw)
   maps[side]=union(maps[side],addition)
   obligations.append(dict(document=doc,original_path=n,old_sha256=h,outcome='passed'))
   if oldmaps[side] is not None:queue.append((side,sha(oldmaps[side])))
 maprows=[]
 for n,m in sorted(maps.items()):
  data=(json.dumps(m,indent=2)+'\n').encode();old=oldmaps[n]
  if old==data:continue
  candidate=copy('candidates/'+n,data)
  if old is not None:copy('prior-map-bytes/'+n,old)
  maprows.append(dict(original_path=n,old_sha256=sha(old) if old else None,new_sha256=sha(data),candidate=candidate))
 archive_rows=[]
 for (n,h),data in sorted(archives.items()):
  assert sha(data)==h;canonical=previous.canonical(n,h);present=(ROOT/canonical).exists()
  if present:assert sha((ROOT/canonical).read_bytes())==h
  snapshot=copy('snapshots/'+canonical,data)
  archive_rows.append(dict(original_path=n,old_sha256=h,canonical_archive=canonical,snapshot=snapshot,already_present=present))
 prior_candidates={r['original_path']:r['new_sha256'] for r in plan['maps']}
 changedmaps={r['original_path'] for r in maprows if prior_candidates.get(r['original_path'])!=r['new_sha256']};driftnames={r['original_path'] for r in drift}
 affected=[];composed=[]
 for row in checks['checks']:
  if row['outcome']!='passed':continue
  side=(Path(row['document']).parent/'source-archive-map.json').as_posix()
  (affected if side in changedmaps or side in driftnames or row['original_path'] in driftnames or row['document'] in driftnames else composed).append(row)
 # Include every current binding under candidate maps, plus all transitive new obligations.
 extra=list(obligations)
 for n,m in maps.items():
  if n not in changedmaps:continue
  for doc in m['documents']:
   if doc not in documents:continue
   for e in m['entries']:
    pair=(e['original_path'],e['sha256'])
    if pair in documents[doc][1]:extra.append(dict(document=doc,original_path=pair[0],old_sha256=pair[1],outcome='passed'))
 todo={(r['document'],r['original_path'],r['old_sha256']):r for r in affected+extra}
 checked=[];diagnostics=[]
 affected_keys={(r['document'],r['original_path'],r['old_sha256']) for r in affected}
 with tempfile.TemporaryDirectory(dir=HERE,prefix='.overlay-') as tmp:
  overlay=Path(tmp)
  def put(n,data):
   p=overlay/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  for r in maprows:put(r['original_path'],(HERE/r['candidate']).read_bytes())
  for r in archive_rows:put(r['canonical_archive'],archives[(r['original_path'],r['old_sha256'])])
  for n,r in replacements.items():put(n,(ROOT/r['future_copy']).read_bytes())
  for key,row in todo.items():
   doc,n,h=key
   for source in [doc,n]:
    if not (overlay/source).exists() and (ROOT/source).is_file():put(source,(ROOT/source).read_bytes())
   side=(Path(doc).parent/'source-archive-map.json').as_posix()
   if not (overlay/side).exists() and (ROOT/side).is_file():put(side,(ROOT/side).read_bytes())
   if (overlay/side).exists():
    for e in read(overlay/side)['entries']:
     if e['original_path']==n and e['sha256']==h:
      a=e['archived_path']
      if not (overlay/a).exists() and (ROOT/a).is_file():put(a,(ROOT/a).read_bytes())
   try:checked_receipt(overlay,doc,n,h);checked.append(row)
   except Exception as error:
    baseline='passed'
    try:checked_receipt(ROOT,doc,n,h)
    except Exception as old:baseline=str(old)
    assert baseline!='passed',(row,str(error))
    assert key not in affected_keys,(row,str(error))
    diagnostics.append(dict(**{k:v for k,v in row.items() if k!='outcome'},outcome=str(error),current_baseline=baseline))
 save('TRUE_DELTA_MAPS.json',dict(paths=sorted(changedmaps),previous_candidates=prior_candidates))
 # Prove frozen non-drift guards and scanned document bytes remain unchanged at end.
 for n,h in frozen.items():assert sha((ROOT/n).read_bytes())==next((d['current_sha256'] for d in drift if d['original_path']==n),h),n
 for n,(data,_) in documents.items():assert (ROOT/n).read_bytes()==data,n
 for n,data in oldmaps.items():assert ((ROOT/n).read_bytes() if (ROOT/n).exists() else None)==data,n
 writes=[dict(original_path=r['original_path'],old_sha256=r['old_sha256'],new_sha256=r['new_sha256'],operation='replace_existing_map' if r['old_sha256'] else 'create_new_map') for r in maprows]
 writes += [dict(original_path=r['canonical_archive'],old_sha256=None,new_sha256=r['old_sha256'],operation='create_canonical_snapshot') for r in archive_rows if not r['already_present']]
 for doc in {r['document'] for r in checks['checks'] if r['outcome']=='passed'} | {r['document'] for r in checked}:
  copy('receipt-bytes/'+doc,(ROOT/doc).read_bytes())
 save('COMPOSITION_PARTITION.json',dict(composed=composed,affected=affected,unchanged_checker=dict(original_path='atlas/evidence.py',old_sha256=sha((ROOT/'atlas/evidence.py').read_bytes()))))
 save('PLAN.json',dict(passed=True,scope='Nonmutating additive composition; no installation or scientific approval',issues=[],failed=[],replacements=plan['replacements'],maps=maprows,archives=archive_rows,merged_concurrent_maps=merges,closure=dict(scanned_json_documents=len(documents),pairs=len(seen),obligations=len(obligations))))
 save('APPLY_WHITELIST.json',dict(writes=writes,future_source_installs=plan['replacements']))
 save('CHECK_RESULTS.json',dict(passed=True,previous_full_replay=rel(PREV/'CHECK_RESULTS.json'),previous_passing=43760,unchanged_composed_predicates=len(composed),affected_previous_predicates=len(affected),distinct_checked=len(checked),checks=checked,additional_preexisting_diagnostics=diagnostics,retained_previous_diagnostics=checks['preexisting_peer_failures'],composition='Unchanged receipt/source/sidecar bytes retain v3 results. Every predicate involving a changed sidecar or drifted source/document is rechecked. All current recognized pairs under candidate sidecars and transitive preservation obligations checked; baseline failures separately retained.'))
 save('DRIFT.json',dict(inputs=drift,outside_write_paths=[r for r in drift if r['original_path'] not in changedmaps],production_writes=0))
 # Exact current live guard set; descriptive names avoid accidental receipt recursion.
 current={n:sha((ROOT/n).read_bytes()) for n in frozen}
 current.update({n:sha(data) for n,(data,_) in documents.items()})
 current.update({n:sha(data) for n,data in oldmaps.items() if data is not None})
 save('SOURCE_PINS.json',dict(files=[dict(original_path=n,old_sha256=h) for n,h in sorted(current.items())]))
 save('PRIOR_IDENTITY.json',dict(files=[dict(original_path=rel(PREV/n),old_sha256=sha((PREV/n).read_bytes())) for n in ['SOURCE_FREEZE.json','PLAN.json','APPLY_WHITELIST.json','CHECK_RESULTS.json']],coordinator_helper=dict(original_path=rel(HERE.parent/'coordinator-install-v1/install.py'),old_sha256=sha((HERE.parent/'coordinator-install-v1/install.py').read_bytes()))))
 print(json.dumps(dict(maps=len(maprows),archives=len(archive_rows),writes=len(writes),affected=len(affected),composed=len(composed),checked=len(checked),diagnostics=len(diagnostics))))
if __name__=='__main__':main()
