"""Read-only exact-commit reverse receipt edges and minimal additive proposals."""
import argparse,collections,hashlib,json,re,subprocess
from pathlib import Path
TARGETS=['web/app.js','tools/build_web.py','.github/workflows/verify.yml','catalogue/manifest.json','catalogue/approved-models.json','catalogue/publications.json','IMPLEMENTATION_PLAN.md','ROADMAP.md','docs/STATUS.md']
HEX=re.compile('[0-9a-f]{64}\\Z')
def sha(b):return hashlib.sha256(b).hexdigest()
def valid(x):return isinstance(x,str)and bool(HEX.fullmatch(x))
def pairs(n,parts=()):
 if isinstance(n,dict):
  for k,v in n.items():
   if valid(v)and(k in TARGETS or k.endswith('/source-archive-map.json')):yield k,v,parts+(k,),'key'
  for pk in ['path','original_path']:
   k=n.get(pk)
   if isinstance(k,str)and(k in TARGETS or k.endswith('/source-archive-map.json')):
    for hk in ['sha256','hash']:
     if valid(n.get(hk)):yield k,n[hk],parts+(hk,),pk
  for k,v in n.items():yield from pairs(v,parts+(k,))
 elif isinstance(n,list):
  for i,v in enumerate(n):yield from pairs(v,parts+(i,))
def main():
 a=argparse.ArgumentParser();a.add_argument('--commit',default='b529a0ef');a.add_argument('--tree',required=True,type=Path);a.add_argument('--output',required=True,type=Path);o=a.parse_args();o.output.mkdir(parents=True,exist_ok=True)
 commit=subprocess.check_output(['git','rev-parse',o.commit],text=True).strip();listing=subprocess.check_output(['git','ls-tree','-r',commit],text=True)
 objects={line.split('\t',1)[1]:line.split()[2]for line in listing.splitlines()if line.split()[1]=='blob'};cache={}
 def data(name):
  if name in cache:return cache[name]
  if name not in objects:raise FileNotFoundError(name)
  p=o.tree/name
  try:b=p.read_bytes()
  except OSError:b=b''
  if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=objects[name]:b=subprocess.check_output(['git','show',commit+':'+name])
  if name in TARGETS or name.endswith('/source-archive-map.json'):cache[name]=b
  return b
 def node(name):return json.loads(data(name))
 sourcepins={p:sha(data(p))for p in TARGETS}
 scans=[];excluded=[];parseerrors=[];edges=[];frozenowners={}
 for name in sorted(objects):
  if not name.endswith('.json'):continue
  parts=Path(name).parts
  if parts[:2]==('catalogue','source-snapshots') or 'frozen-sources'in parts:
   excluded.append(name);continue
  b=data(name)
  if not any(t.encode()in b for t in TARGETS)and b'/source-archive-map.json'not in b:continue
  try:n=json.loads(b)
  except Exception as e:parseerrors.append({'document':name,'error':str(e)});continue
  scans.append(name);group=collections.defaultdict(list)
  for path,h,location,shape in pairs(n):
   # original_path objects are sidecar metadata, not accepted receipt pairs.
   if name.endswith('/source-archive-map.json')and path in TARGETS:continue
   group[(path,h)].append({'pointer':'/'+'/'.join(str(x).replace('~','~0').replace('/','~1')for x in location),'shape':shape})
  for(path,h),locations in sorted(group.items()):
   row=dict(document=name,document_sha256=sha(b),original_path=path,sha256=h,locations=locations)
   originalonly=all(x['shape']=='original_path'for x in locations)
   sidecar=str(Path(name).parent/'source-archive-map.json');selected=path
   try:
    if originalonly:
     archive='catalogue/source-snapshots/'+h+'/'+path
     if archive in objects and sha(data(archive))==h:selected=archive
    elif sidecar in objects:
     m=node(sidecar)
     if m.get('version')!='immutable-source-archive-map-0.1':raise ValueError('unsupported archive map')
     if m.get('documents',{}).get(name)!=sha(b):raise ValueError('document missing/changed in sibling sidecar')
     matches=[x for x in m['entries']if x.get('original_path')==path and x.get('sha256')==h]
     if len(matches)>1:raise ValueError('ambiguous archive map')
     if matches:
      selected='catalogue/source-snapshots/'+h+'/'+path
      if matches[0].get('archived_path')!=selected:raise ValueError('invalid archive location')
    if sha(data(selected))!=h:raise ValueError('selected source hash mismatch')
    row['resolution']=('live-sidecar-entry'if originalonly else'live')if selected==path else('archived-sidecar-entry'if originalonly else'archived');row['resolved_path']=selected
   except Exception as e:row.update(resolution='unresolved',error=str(e))
   row['expected_equals_baseline']=h==sha(data(path))if path in objects else False
   edges.append(row)
 primary=[x for x in edges if x['original_path']in TARGETS]
 required=[x for x in primary if x['resolution']=='live']
 maps={str(Path(x['document']).parent/'source-archive-map.json')for x in required}
 while True:
  extra=[x for x in edges if x['original_path']in maps and x['resolution']=='live'and x not in required]
  before=len(maps);required+=extra;maps.update(str(Path(x['document']).parent/'source-archive-map.json')for x in extra)
  if len(maps)==before:break
 proposals={};archives={}
 for row in required:
  path=row['original_path'];h=row['sha256'];archives[(path,h)]={'original_path':path,'sha256':h,'archived_path':'catalogue/source-snapshots/'+h+'/'+path,'already_present':('catalogue/source-snapshots/'+h+'/'+path)in objects}
 for name in sorted(maps):
  exists=name in objects;m=node(name)if exists else{'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
  oldentries=len(m['entries']);olddocs=len(m['documents']);parent=Path(name).parent
  relevant=[x for x in required if str(Path(x['document']).parent/'source-archive-map.json')==name]
  # Coverage includes unchanged sibling file/dependency manifests, as required by archive tests.
  for sib in objects:
   if Path(sib).parent!=parent or not sib.endswith('.json')or sib==name:continue
   try:n=node(sib)
   except Exception:continue
   qualifies=isinstance(n,dict)and(isinstance(n.get('files'),dict)or isinstance(n.get('dependencies'),dict)or(bool(n)and all(valid(h)for h in n.values())))
   if qualifies:m['documents'][sib]=sha(data(sib))
  for row in relevant:
   m['documents'][row['document']]=row['document_sha256'];entry={k:archives[(row['original_path'],row['sha256'])][k]for k in['original_path','sha256','archived_path']}
   matches=[x for x in m['entries']if x.get('original_path')==entry['original_path']and x.get('sha256')==entry['sha256']]
   if not matches:m['entries'].append(entry)
   else:assert len(matches)==1 and matches[0]==entry
  dest=o.output/'planned-sidecars'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(m,indent=2)+'\n')
  proposals[name]=dict(existed=exists,baseline_sha256=sha(data(name))if exists else None,proposed_sha256=sha(dest.read_bytes()),entries_added=len(m['entries'])-oldentries,documents_added=len(m['documents'])-olddocs)
  if exists:
   h=sha(data(name));archive='catalogue/source-snapshots/'+h+'/'+name;archives[(name,h)]={'original_path':name,'sha256':h,'archived_path':archive,'already_present':archive in objects}
 summary=dict(baseline=commit,tracked_json=sum(x.endswith('.json')for x in objects),candidate_documents=len(scans),excluded_namespace_json=len(excluded),primary_pairs=len(primary),primary_resolution_counts=dict(collections.Counter(x['resolution']for x in primary)),new_required_primary_edges=sum(x['original_path']in TARGETS for x in required),new_required_secondary_edges=sum(x['original_path']not in TARGETS for x in required),sidecars_to_change=len(proposals),canonical_snapshots=len(archives),parse_errors=len(parseerrors))
 inventory=dict(summary=summary,baseline_source_pins=sourcepins,namespace_policy='Exclude canonical catalogue/source-snapshots and owner-bound frozen-sources trees. Other copied source/proposal namespaces remain visible but do not become required live edges unless the original resolver actually selects the live source.',primary_edges=primary,secondary_edges=[x for x in edges if x['original_path']not in TARGETS],required_additive_edges=required,sidecar_proposals=proposals,canonical_archives=sorted(archives.values(),key=lambda x:x['archived_path']),excluded_namespace_documents=excluded,parse_errors=parseerrors)
 (o.output/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
