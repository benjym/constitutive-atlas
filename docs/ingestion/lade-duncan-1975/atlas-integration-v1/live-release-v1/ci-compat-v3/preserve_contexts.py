from pathlib import Path
import json,hashlib,collections
r=Path('/private/tmp/atlas-lade-release-v1');shared=Path('/Users/bmar5496/code/constitutive-atlas');h=Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1');sha=lambda b:hashlib.sha256(b).hexdigest()
# Remove only the unused candidate mapping, retaining its exact candidate bytes privately.
p=r/h/'source-archive-map.json';b=p.read_bytes();j=json.loads(b);j['entries']=[e for e in j['entries'] if e['original_path']!='docs/reviews/tresca-v5-source-integration-v1/source-archive-map.json'];p.write_text(json.dumps(j,indent=2)+'\n')
jsons={};reverse=collections.defaultdict(set)
def pairs(node):
 out=set()
 if isinstance(node,dict):
  for k,v in node.items():
   if isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v) and '/' in k:out.add((k,v))
  if isinstance(node.get('path'),str):
   for key in ['sha256','hash']:
    v=node.get(key)
    if isinstance(v,str) and len(v)==64:out.add((node['path'],v))
  for v in node.values():out|=pairs(v)
 elif isinstance(node,list):
  for v in node:out|=pairs(v)
 return out
for p in r.rglob('*.json'):
 rel=p.relative_to(r)
 if any(k in rel.parts for k in ['.git','.local','node_modules','__pycache__']) or str(rel).startswith('catalogue/source-snapshots/') or p.name=='source-archive-map.json':continue
 try:j=json.loads(p.read_text())
 except (ValueError,UnicodeError):continue
 jsons[str(rel)]=j
 for pair in pairs(j):reverse[pair].add(str(rel))
import sys;sys.path.insert(0,str(r));from atlas.evidence import checked_receipt
baseline_maps={};changed={};done=[]
def archived(path,pin):
 q=r/'catalogue/source-snapshots'/pin/path
 assert q.exists() and sha(q.read_bytes())==pin,(path,pin)
 return q.relative_to(r).as_posix()
def add(doc,path,pin):
 side=str(Path(doc).parent/'source-archive-map.json');p=r/side
 if side not in baseline_maps:
  if p.exists():
   b=p.read_bytes();base=sha(b);canonical=r/'catalogue/source-snapshots'/base/side;canonical.parent.mkdir(parents=True,exist_ok=True)
   if canonical.exists():assert canonical.read_bytes()==b
   else:canonical.write_bytes(b)
   baseline_maps[side]=base;changed[side]=base
  else:baseline_maps[side]=None
 j=json.loads(p.read_text()) if p.exists() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 for q in p.parent.glob('*.json'):
  if q.name!='source-archive-map.json':j['documents'].setdefault(q.relative_to(r).as_posix(),sha(q.read_bytes()))
 assert j['documents'][doc]==sha((r/doc).read_bytes()),('existing stale document',doc)
 entry={'original_path':path,'sha256':pin,'archived_path':archived(path,pin)}
 same=[e for e in j['entries'] if e['original_path']==path and e['sha256']==pin]
 if same:assert same==[entry]
 else:j['entries'].append(entry)
 p.write_text(json.dumps(j,indent=2)+'\n');checked_receipt(r,doc,path,pin);done.append({'document':doc,'path':path,'sha256':pin})
rows=json.loads((shared/h/'independent-review/ci-compat-v3/DIRECT_CLASSIFICATION.json').read_text())['rows']
for row in rows:
 if row['baseline_prior_original_hash']=='pass':add(row['document'],row['path'],row['sha256'])
seen=set()
while True:
 new=[(p,pin) for p,pin in changed.items() if (p,pin) not in seen]
 if not new:break
 for path,pin in new:
  seen.add((path,pin))
  for doc in reverse[(path,pin)]:
   try:checked_receipt(r,doc,path,pin)
   except ValueError:add(doc,path,pin)
# Every original positive directpair must pass after all context updates.
for row in rows:
 if row['baseline_prior_original_hash']=='pass':checked_receipt(r,row['document'],row['path'],row['sha256'])
files={side:sha((r/side).read_bytes()) for side in baseline_maps}
(r/h/'ci-compat-v3/CONTEXT_REPAIR.json').write_text(json.dumps({'scope':'Preserve126 previouslypositive direct receipts and transitive changedsidecar consumers; original7files andeverychangedsidecar canonical; no originalreceipts/thresholds rewritten','checks':len(done),'maps':files,'prior_map_hashes':baseline_maps,'resolved':done},indent=2)+'\n')
print('Resolved',len(done),'checks;',len(files),'maps')
