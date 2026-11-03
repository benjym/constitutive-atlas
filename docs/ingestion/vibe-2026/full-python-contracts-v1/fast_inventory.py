"""Read-only indexed receipt inventory, avoiding repeated large JSON traversals."""
from pathlib import Path
import hashlib,json,subprocess

def inventory(root,scanner):
 root=Path(root);cache={};digests={}
 def digest(p):
  key=str(p)
  if key not in digests:digests[key]=hashlib.sha256(p.read_bytes()).hexdigest()
  return digests[key]
 def read(p):
  key=str(p)
  if key not in cache:cache[key]=json.loads(p.read_text())
  return cache[key]
 args=['rg','-l','-F',*[v for t in sorted(scanner.TARGETS) for v in ('-e',t)],'-e','source-archive-map.json','--glob','*.json',*scanner.ROOTS]
 proc=subprocess.run(args,cwd=root,capture_output=True,text=True);assert proc.returncode in(0,1)
 live={t:digest(root/t) for t in scanner.TARGETS};primary=[];secondary=[];errors=[];scanned=[]
 for rel in proc.stdout.splitlines():
  if any(part in scanner.EXCLUDE_PARTS for part in Path(rel).parts):continue
  p=root/rel
  try:node=read(p)
  except Exception as exc:errors.append({'document':rel,'error':str(exc)});continue
  scanned.append(rel)
  for sec in (False,True):
   if not sec and p.name=='source-archive-map.json':continue
   grouped={}
   for path,h,loc,shape in scanner.pairs(node,secondary=sec):
    if sec and not path.endswith('/source-archive-map.json'):continue
    grouped.setdefault((path,h),[]).append({'pointer':loc,'shape':shape})
   for (path,h),locations in grouped.items():
    row={'document':rel,'document_sha256':digest(p),'original_path':path,'sha256':h,'locations':locations}
    if sec:secondary.append(row);continue
    row['expected_equals_current_live']=h==live[path];sidecar=p.parent/'source-archive-map.json';row['sibling_sidecar']=str(sidecar.relative_to(root)) if sidecar.exists() else None
    try:
     selected=root/path
     if sidecar.exists():
      mapping=read(sidecar);assert mapping['version']=='immutable-source-archive-map-0.1';assert mapping['documents'].get(rel)==digest(p),'original evidence document changed after archival'
      matches=[x for x in mapping['entries'] if x['original_path']==path and x['sha256']==h];assert len(matches)<=1
      if matches:
       canonical='catalogue/source-snapshots/'+h+'/'+path;assert matches[0]['archived_path']==canonical;selected=root/canonical
     assert digest(selected)==h,'evidence source hash mismatch'
     row.update(resolution='live' if selected==root/path else 'archived',resolved_path=str(selected.relative_to(root)))
    except Exception as exc:row.update(resolution='unresolved',error=str(exc))
    primary.append(row)
 return {'scope':{'roots':scanner.ROOTS,'excluded_path_parts':sorted(scanner.EXCLUDE_PARTS),'method':'rg literal candidate filtering then exact recursive pair index; cached per-document/map hashes; no payload JSON decoding'},'live_source_identities':[{'original_path':k,'sha256':v} for k,v in live.items()],'scanned_json_files':scanned,'parse_errors':errors,'primary_references':primary,'secondary_source_map_references':secondary}
