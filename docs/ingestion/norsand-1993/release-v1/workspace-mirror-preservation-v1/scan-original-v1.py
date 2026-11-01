"""Read-only recursive receipt binding inventory; no payload JSON decoding."""
import argparse,collections,hashlib,json,re,sys
from pathlib import Path
TARGETS={'atlas/dsl.py','atlas/compiler.py','atlas/history_compiler.py','atlas/model.py'}
ROOTS=('catalogue','docs','tools','schemas','tests')
EXCLUDE_PARTS={'source-snapshots','source-snapshot','snapshots','frozen','frozen-sources','reviewed-sources'}
HEX=re.compile(r'[a-f0-9]{64}\Z')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def valid(x):return isinstance(x,str) and bool(HEX.fullmatch(x))
def pointer(parts):return '/'+ '/'.join(str(p).replace('~','~0').replace('/','~1') for p in parts)
def pairs(node,parts=(),secondary=False):
 if isinstance(node,dict):
  for k,v in node.items():
   if valid(v) and (k in TARGETS or secondary and k.endswith('/source-archive-map.json')):yield k,v,pointer(parts+(k,)),'direct-map'
  keys=('path','original_path') if secondary else ('path',)
  for pathkey in keys:
   path=node.get(pathkey)
   if isinstance(path,str) and (path in TARGETS or secondary and path.endswith('/source-archive-map.json')):
    for hk in ('sha256','hash'):
     if valid(node.get(hk)):yield path,node[hk],pointer(parts+(hk,)),pathkey+'-object'
  for k,v in node.items():yield from pairs(v,parts+(k,),secondary)
 elif isinstance(node,list):
  for i,v in enumerate(node):yield from pairs(v,parts+(i,),secondary)

def scan(root):
 root=Path(root).resolve();sys.path.insert(0,str(root))
 from atlas.evidence import checked_receipt
 live={t:digest(root/t) for t in sorted(TARGETS)}
 primary=[];secondary=[];excluded=[];errors=[];scanned=[]
 for base in ROOTS:
  for p in sorted((root/base).rglob('*.json')):
   rel=p.relative_to(root).as_posix()
   if any(part in EXCLUDE_PARTS for part in p.relative_to(root).parts):excluded.append(rel);continue
   try:node=json.loads(p.read_text())
   except Exception as e:errors.append({'document':rel,'error':str(e)});continue
   scanned.append(rel)
   # Source-archive-map entries are not primary source receipts.
   for sec in (False,True):
    if not sec and p.name=='source-archive-map.json':continue
    grouped=collections.defaultdict(list)
    for path,h,loc,shape in pairs(node,secondary=sec):
     if sec and not path.endswith('/source-archive-map.json'):continue
     grouped[(path,h)].append({'pointer':loc,'shape':shape})
    for (path,h),locations in sorted(grouped.items()):
     if Path(path).is_absolute() or '..' in Path(path).parts: continue
     row={'document':rel,'document_sha256':digest(p),'original_path':path,'sha256':h,'locations':locations}
     try:
      selected=checked_receipt(root,rel,path,h)
      row['resolved_path']=selected.relative_to(root).as_posix()
      row['resolution']='live' if selected==root/path else 'archived'
     except Exception as e:
      # Historical sidecar entries use original_path, not the supported primary receipt path-object shape.
      if sec and all(x['shape']=='original_path-object' for x in locations):
       archive=root/'catalogue/source-snapshots'/h/path
       if archive.is_file() and digest(archive)==h:
        row['resolution']='archived-sidecar-entry';row['resolved_path']=archive.relative_to(root).as_posix()
       elif (root/path).is_file() and digest(root/path)==h:row['resolution']='live-sidecar-entry';row['resolved_path']=path
       else:row['resolution']='unresolved';row['error']=str(e)
      else:row['resolution']='unresolved';row['error']=str(e)
     if not sec:
      row['expected_equals_current_live']=h==live[path]
      sidecar=p.parent/'source-archive-map.json'
      row['sibling_sidecar']=sidecar.relative_to(root).as_posix() if sidecar.exists() else None
     (secondary if sec else primary).append(row)
 # Any map selected for archival additions changes bytes. Compute reverse edge closure requiring attention.
 affected={str(Path(row['document']).parent/'source-archive-map.json') for row in primary if row['expected_equals_current_live'] or row['resolution']=='unresolved'}
 initial=sorted(affected)
 changed=True
 while changed:
  changed=False
  for row in secondary:
   if row['original_path'] in affected and row['document'].endswith('/source-archive-map.json') and row['document'] not in affected:
    affected.add(row['document']);changed=True
 for row in secondary:row['references_potentially_mutated_sidecar']=row['original_path'] in affected
 # Retain the exact reverse-reference closure only; unrelated sidecar references do not participate in this mutation.
 secondary=[row for row in secondary if row['references_potentially_mutated_sidecar']]
 return {'scope':{'roots':ROOTS,'excluded_path_parts':sorted(EXCLUDE_PARTS),'primary_shapes':['recursive exact direct path->64-lowercase-hex','recursive {path:...,sha256/hash:...}'],'excluded_primary':['source-archive-map.json sidecars','snapshot/frozen trees','JSON text embedded in capsule payload encodings (not decoded)'],'secondary':'direct/path/original_path references ending /source-archive-map.json; excludes snapshot trees'},'live_source_identities':[{'original_path':path,'sha256':h} for path,h in live.items()],'checked_receipt_source_sha256':digest(root/'atlas/evidence.py'),'scanned_json_files':scanned,'excluded_json_files':excluded,'parse_errors':errors,'primary_references':primary,'secondary_source_map_references':secondary,'potential_new_or_extended_sidecars':initial,'sidecar_reverse_reference_closure':sorted(affected),'summary':{'scanned_json':len(scanned),'excluded_json':len(excluded),'primary_document_source_pairs':len(primary),'primary_documents':len({x['document'] for x in primary}),'primary_resolution_counts':dict(collections.Counter(x['resolution'] for x in primary)),'primary_live_hash_pairs':sum(x['expected_equals_current_live'] for x in primary),'primary_unresolved':sum(x['resolution']=='unresolved' for x in primary),'secondary_pairs':len(secondary),'secondary_resolution_counts':dict(collections.Counter(x['resolution'] for x in secondary)),'secondary_potential_attention':sum(x['references_potentially_mutated_sidecar'] for x in secondary)}}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('--output',required=True);a=p.parse_args()
 result=scan(a.root);Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result['summary'],indent=2,sort_keys=True))
