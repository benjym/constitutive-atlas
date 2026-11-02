"""Pure archive-first proposal: reads live owned evidence; writes only this packet.
No apply mode. Never changes ledgers, receipt documents, maps, Git or processes.
"""
from pathlib import Path
import hashlib,json
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');PACKET='docs/ingestion/hypoplastic-interface-2016/';OUT=Path(__file__).resolve().parent
DOCS=[PACKET+'DELIVERY.md',PACKET+'CHECKLIST.md']
def sha(b):return hashlib.sha256(b).hexdigest()
def contains(value,path,digest):
 if isinstance(value,dict):
  if value.get(path)==digest or value.get('path')==path and any(value.get(k)==digest for k in ['sha256','hash']):return True
  return any(contains(v,path,digest) for v in value.values())
 return isinstance(value,list) and any(contains(v,path,digest) for v in value)
old={name:sha((ROOT/name).read_bytes()) for name in DOCS};consumers=[];groups={}
for p in sorted((ROOT/PACKET).rglob('*.json')):
 if 'ledger-update-v1' in p.parts or p.name=='source-archive-map.json':continue
 try:value=json.loads(p.read_text())
 except (OSError,UnicodeError,json.JSONDecodeError):continue
 matches=[name for name,digest in old.items() if contains(value,name,digest)]
 if not matches:continue
 name=p.relative_to(ROOT).as_posix();consumer={'path':name,'sha256':sha(p.read_bytes()),'documents':matches,'notes':'Historical direct-hash inventories/run records remain valid in their original frozen source context; this sidecar adds recoverability, not automatic adaptation of direct-hash scripts.'}
 consumers.append(consumer);mp=p.parent/'source-archive-map.json';mapname=mp.relative_to(ROOT).as_posix()
 if mapname not in groups:
  original=mp.read_bytes() if mp.exists() else None
  mapping=json.loads(original) if original else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
  assert mapping['version']=='immutable-source-archive-map-0.1'
  groups[mapname]={'original_bytes':original,'mapping':mapping,'consumers':[]}
 group=groups[mapname];m=group['mapping'];assert name not in m['documents'] or m['documents'][name]==consumer['sha256'],('Existing consumer pin drift',name)
 m['documents'][name]=consumer['sha256'];group['consumers'].append(name)
 for doc in matches:
  archive='catalogue/source-snapshots/'+old[doc]+'/'+doc
  pair=[e for e in m['entries'] if e.get('original_path')==doc and e.get('sha256')==old[doc]]
  assert len(pair)<=1
  if pair:assert pair[0]['archived_path']==archive
  else:m['entries'].append({'original_path':doc,'sha256':old[doc],'archived_path':archive})
# A sidecar applies to all receipt documents in its directory. Register every
# current JSON sibling so adding this sidecar cannot invalidate another receipt.
for name,group in groups.items():
 for sibling in sorted((ROOT/name).parent.glob('*.json')):
  if sibling.name=='source-archive-map.json':continue
  json.loads(sibling.read_text())
  rel=sibling.relative_to(ROOT).as_posix();digest=sha(sibling.read_bytes())
  pins=group['mapping']['documents']
  assert rel not in pins or pins[rel]==digest, ('Existing sibling pin drift',rel)
  pins[rel]=digest
archives=[]
for doc,digest in old.items():
 target='catalogue/source-snapshots/'+digest+'/'+doc
 if (ROOT/target).exists():assert sha((ROOT/target).read_bytes())==digest
 archives.append({'source':doc,'sha256':digest,'canonical_target':target,'operation':'Create exact-byte archive before any map/ledger replacement; never overwrite an existing different archive.'})
map_proposals=[]
for name,group in sorted(groups.items()):
 original=group['original_bytes']
 if original is not None:
  digest=sha(original);archives.append({'source':name,'sha256':digest,'canonical_target':'catalogue/source-snapshots/'+digest+'/'+name,'operation':'Preserve existing map exact bytes before replacing its sidecar.'})
 content=(json.dumps(group['mapping'],indent=2)+'\n').encode();target=OUT/'proposed-maps-v2'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
 map_proposals.append({'path':name,'exists_now':original is not None,'old_sha256':sha(original) if original is not None else None,'proposed_sha256':sha(content),'proposal_file':target.relative_to(ROOT).as_posix(),'ledger_consumers':group['consumers'],'documents':dict(group['mapping']['documents'])})
assert any(c['path']==PACKET+'tracking-review-v1/decision.json' for c in consumers)
report={'status':'proposal-only; no live changes applied','live_ledger_pins':old,'scan_scope':PACKET,'consumer_count':len(consumers),'consumers':consumers,'archive_first_operations':archives,'sidecar_proposals':map_proposals,'protected': ['tracking-review-v1/decision.json','E5 review/model/approval/qualified source','current root DELIVERY.md and CHECKLIST.md'],'application_order':['Coordinator confirms current source/docs and consumers still match these pins; recapture if they changed.','Create and verify all canonical exact-byte archives before replacing any live file.','Atomically install proposed additive sidecars, preserving old sidecar bytes first if any.','For every consumer/path/hash, use checked_receipt with original expected hashes and prove exact archive bytes.','Only then atomically replace ledgers with separately reviewed successor drafts; never repin receipt documents.','Re-run source-only archived receipt resolution; retain old historical direct-hash scripts/results in original commit context.','Actual build/material/browser/package calls await coordinator slot release; this proposal never executes them.'],'git_build_material_browser_calls':0,'live_mutations':0}
(OUT/'preservation-proposal-v2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'ledger_pins':old,'consumers':len(consumers),'maps':len(map_proposals),'archive_operations':len(archives),'live_mutations':0},indent=2))
