"""Narrow source-only test correction and immutable receipt preservation proposal."""
from pathlib import Path
from collections import defaultdict,deque
import hashlib,json,sys,importlib.util,tempfile
H=Path(__file__).resolve().parent;R=H.parents[4]
sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
spec=importlib.util.spec_from_file_location('preservation',H.parent/'shared-hook-install-v1/revision-v3/plan_preservation.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(n,b):
 t=H/n;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(b)
def save(n,v):put(n,(json.dumps(v,indent=2)+'\n').encode())
def main():
 name='tests/test_laboratory_profile_policy.mjs';old=(R/name).read_bytes();assert sha(old)=='97ac72c2118161bf188748048b22b637e64f880c9ce8cbab5a72f23faf0b5392'
 assert old.count(b'complete thirteen model')==1 and old.count(b'.cases.length,35)')==2
 new=old.replace(b'complete thirteen model',b'complete fourteen model').replace(b'.cases.length,35)',b'.cases.length,36)')
 put('test-before.mjs',old);put('test-proposed.mjs',new)
 docs={};index=defaultdict(set);skip=(H.relative_to(R).as_posix()+'/',(H.parent/'shared-hook-install-v1').relative_to(R).as_posix()+'/',(H.parent/'profile-install-v1').relative_to(R).as_posix()+'/','catalogue/source-snapshots/')
 for directory in ['docs','catalogue']:
  for f in sorted((R/directory).rglob('*.json')):
   n=f.relative_to(R).as_posix()
   if n.startswith(skip):continue
   try:data=f.read_bytes();value=json.loads(data)
   except (ValueError,UnicodeDecodeError):continue
   pairs=set() if f.name=='source-archive-map.json' else p.pairs(value);docs[n]=(data,pairs)
   for pair in pairs:index[pair].add(n)
 q=deque([(name,sha(old))]);seen=set();maps={};priors={};archives={};bindings=[]
 while q:
  original,expected=q.popleft()
  if (original,expected) in seen:continue
  seen.add((original,expected));data=(R/original).read_bytes();assert sha(data)==expected
  archives[(original,expected)]=data
  for doc in sorted(index[(original,expected)]):
   docbytes,_=docs[doc];side=(Path(doc).parent/'source-archive-map.json').as_posix()
   if side not in maps:
    priors[side]=(R/side).read_bytes() if (R/side).exists() else None
    maps[side]=json.loads(priors[side]) if priors[side] else dict(version=p.VERSION,documents={},entries=[])
   m=maps[side];assert m['version']==p.VERSION
   for peer,(raw,pp) in docs.items():
    if Path(peer).parent==Path(doc).parent and pp:
     assert peer not in m['documents'] or m['documents'][peer]==sha(raw),(side,peer,'existing pin mismatch')
     m['documents'][peer]=sha(raw)
   entries=m['entries'];matched=[e for e in entries if e.get('original_path')==original and e.get('sha256')==expected]
   canonical=p.canonical(original,expected)
   assert len(matched)<=1
   if matched:assert matched[0]['archived_path']==canonical
   else:entries.append(dict(original_path=original,sha256=expected,archived_path=canonical))
   bindings.append(dict(document=doc,original_path=original,old_sha256=expected,outcome='passed'))
   if priors[side] is not None:q.append((side,sha(priors[side])))
 rows=[]
 for n,m in sorted(maps.items()):
  candidate=(json.dumps(m,indent=2)+'\n').encode();before=priors[n]
  if candidate==before:continue
  put('candidates/'+n,candidate)
  if before is not None:put('prior-map-bytes/'+n,before)
  rows.append(dict(original_path=n,old_sha256=sha(before) if before else None,new_sha256=sha(candidate),candidate='candidates/'+n))
 ar=[]
 for (n,h),data in sorted(archives.items()):
  canonical=p.canonical(n,h);exists=(R/canonical).exists()
  if exists:assert sha((R/canonical).read_bytes())==h
  put('snapshots/'+canonical,data);ar.append(dict(original_path=n,old_sha256=h,canonical_archive=canonical,snapshot='snapshots/'+canonical,already_present=exists))
 # Check all obligations and genuine existing entry pairs under changed candidate maps.
 checks={(r['document'],r['original_path'],r['old_sha256']):r for r in bindings}
 for n,m in maps.items():
  for doc in m['documents']:
   if doc not in docs:continue
   for e in m['entries']:
    pair=(e['original_path'],e['sha256'])
    if pair in docs[doc][1]:checks[(doc,*pair)]=dict(document=doc,original_path=pair[0],old_sha256=pair[1],outcome='passed')
 with tempfile.TemporaryDirectory(dir=H,prefix='.overlay-') as td:
  overlay=Path(td)
  def stage(n,b):
   t=overlay/n;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(b)
  stage(name,new)
  for n,m in maps.items():stage(n,(json.dumps(m,indent=2)+'\n').encode())
  for (n,h),b in archives.items():stage(p.canonical(n,h),b)
  for doc,n,h in checks:
   stage(doc,docs[doc][0]);put('receipt-bytes/'+doc,docs[doc][0])
   if n!=name and (R/n).is_file():stage(n,(R/n).read_bytes())
   for e in maps[(Path(doc).parent/'source-archive-map.json').as_posix()]['entries']:
    a=e['archived_path']
    if (R/a).is_file() and not (overlay/a).exists():stage(a,(R/a).read_bytes())
   checked_receipt(overlay,doc,n,h)
 for n,(b,_) in docs.items():assert (R/n).read_bytes()==b,n
 for n,b in priors.items():assert ((R/n).read_bytes() if (R/n).exists() else None)==b,n
 writes=[dict(original_path=r['original_path'],old_sha256=r['old_sha256'],new_sha256=r['new_sha256'],operation='replace_existing_map' if r['old_sha256'] else 'create_new_map') for r in rows]
 writes += [dict(original_path=r['canonical_archive'],old_sha256=None,new_sha256=r['old_sha256'],operation='create_canonical_snapshot') for r in ar if not r['already_present']]
 proposal=dict(passed=True,scope='Exactly three static positive test tokens; policy/cases/catalogue/negative assertions unchanged',source=dict(original_path=name,old_sha256=sha(old),new_sha256=sha(new),before_copy='test-before.mjs',future_copy='test-proposed.mjs'),maps=rows,archives=ar,scan=dict(json_documents=len(docs),immutable_consumers=len(bindings),transitive_pairs=len(seen)),checks=list(checks.values()),production_writes=0)
 save('PROPOSAL.json',proposal);save('APPLY_WHITELIST.json',dict(metadata_writes=writes,source_replacement=proposal['source']))
 save('SOURCE_PINS.json',dict(files=[dict(original_path=n,old_sha256=sha(b)) for n,(b,_) in sorted(docs.items())]))
 print(json.dumps(dict(maps=len(rows),archives=len(ar),metadata_writes=len(writes),bindings=len(bindings),checks=len(checks),old_sha256=sha(old),new_sha256=sha(new))))
if __name__=='__main__':main()
