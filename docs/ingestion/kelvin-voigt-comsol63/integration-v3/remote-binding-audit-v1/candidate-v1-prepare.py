"""Remote-rebase binding plan only; writes solely this portable audit directory."""
import collections,gzip,hashlib,io,json,re,subprocess,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];WORKSPACE=Path('/Users/bmar5496/code/constitutive-atlas');D=Path('docs/ingestion/kelvin-voigt-comsol63');REMOTE='462a450c69b0fd481fc99b67e8c42f03f82e0e97';BASE='b529a0efc3415b2bc567178a68174575c220cadc'
TARGETS={'web/app.js','tools/build_web.py','.github/workflows/verify.yml','catalogue/manifest.json','catalogue/approved-models.json','IMPLEMENTATION_PLAN.md','ROADMAP.md','docs/STATUS.md','tests/test_j2_main_routing.mjs'}
OVERLAPMAPS={str(Path('docs/ingestion/duncan-chang-1970/release-v2')/x/'source-archive-map.json')for x in['.','postapply']}
HEX=re.compile('[0-9a-f]{64}\\Z');cache={};localcache={}
def sha(b):return hashlib.sha256(b).hexdigest()
def gitdata(p):
 if p not in cache:cache[p]=subprocess.check_output(['git','show',REMOTE+':'+p],stderr=subprocess.DEVNULL)
 return cache[p]
def localdata(p):
 if p not in localcache:
  pre=R/D/'integration-v3/premerge'/p
  localcache[p]=pre.read_bytes()if p in OVERLAPMAPS and pre.exists()else(R/p).read_bytes()
 return localcache[p]
def excluded(n):
 return any(p in{'source-snapshots','frozen-sources','receipt-bytes','prior-source','source','source-mirror','planned-sidecars','proposal-inputs','context','isolated','premerge','candidates','snapshots','prior-map-bytes'}or re.fullmatch(r'.*-context-v\d+',p)or re.fullmatch(r'prior-v\d+',p)for p in Path(n).parts)
def valid(h):return isinstance(h,str)and HEX.fullmatch(h)
def pairs(n,loc=()):
 if isinstance(n,dict):
  for p,h in n.items():
   if valid(h)and(p in TARGETS or p.endswith('/source-archive-map.json')):yield p,h,loc+(p,),'key'
  p=n.get('path')
  if isinstance(p,str)and(p in TARGETS or p.endswith('/source-archive-map.json')):
   for key in['sha256','hash']:
    if valid(n.get(key)):yield p,n[key],loc+(key,),'path'
  for k,v in n.items():yield from pairs(v,loc+(k,))
 elif isinstance(n,list):
  for i,v in enumerate(n):yield from pairs(v,loc+(i,))
def classify(doc,path,h,kind):
 reader=gitdata if kind=='remote'else localdata;selected=path;side=str(Path(doc).parent/'source-archive-map.json')
 try:
  data=reader(doc)
  try:m=json.loads(reader(side))
  except(subprocess.CalledProcessError,FileNotFoundError):m=None
  if m:
   assert m['version']=='immutable-source-archive-map-0.1'
   assert m['documents'].get(doc)==sha(data),'document guard missing/mismatch'
   matches=[e for e in m['entries']if e.get('original_path')==path and e.get('sha256')==h];assert len(matches)<=1
   if matches:selected=matches[0]['archived_path'];assert selected=='catalogue/source-snapshots/'+h+'/'+path
  assert sha(reader(selected))==h,'source hash mismatch'
  return {'resolution':'live'if selected==path else'archived','resolved_path':selected}
 except Exception as e:return {'resolution':'unresolved','error':str(e)}
def scan_document(doc,kind):
 data=(gitdata if kind=='remote'else localdata)(doc);node=json.loads(data);group=collections.defaultdict(list)
 for p,h,loc,shape in pairs(node):
  if doc.endswith('/source-archive-map.json'):continue
  group[p,h].append({'pointer':'/'+'/'.join(str(v)for v in loc),'shape':shape})
 return [dict(document=doc,document_sha256=sha(data),original_path=p,sha256=h,locations=locations,namespace=kind,**classify(doc,p,h,kind))for(p,h),locations in group.items()]
def main():
 assert not(B/'plan.json').exists(),'Create-only audit'
 objects={l.split('\t',1)[1]:l.split()[2]for l in subprocess.check_output(['git','ls-tree','-r',REMOTE],text=True).splitlines()};changed=set(subprocess.check_output(['git','diff','--name-only',BASE,REMOTE],text=True).splitlines())
 previous=json.loads(gzip.decompress((WORKSPACE/D/'release-bindings-v1/inventory-scope-v2.json.gz').read_bytes()));rows=[];seen=set()
 for old in previous['primary_edges']+previous['secondary_edges']:
  doc=old['document'];p=old['original_path'];h=old['sha256']
  if doc in changed or doc not in objects or excluded(doc)or excluded(p)or doc.endswith('/source-archive-map.json'):continue
  if p not in TARGETS and not p.endswith('/source-archive-map.json'):continue
  # Only supported primary receipt shapes count as live edges.
  if all(z['shape']=='original_path'for z in old['locations']):continue
  key=(doc,p,h)
  if key in seen:continue
  seen.add(key);rows.append(dict(document=doc,document_sha256=sha(gitdata(doc)),original_path=p,sha256=h,locations=old['locations'],namespace='remote',**classify(doc,p,h,'remote')))
 newdocs=[p for p in changed if p in objects and p.endswith('.json')and not excluded(p)]
 for doc in sorted(newdocs):rows+=scan_document(doc,'remote')
 # Own uncommitted receipt closure is independent of origin's historical receipt namespace.
 own=[]
 for p in sorted((R/D).rglob('*.json')):
  doc=str(p.relative_to(R))
  if excluded(doc)or B in p.parents or any(v in p.parts for v in['release-bindings-v1','interface-v3']):continue
  try:own+=scan_document(doc,'isolated')
  except(json.JSONDecodeError,UnicodeDecodeError):continue
 sources={p:sha(gitdata(p))for p in sorted(TARGETS)}
 required=[r for r in rows if r['original_path']in TARGETS and r['resolution']=='live'];maps=set(OVERLAPMAPS)|{str(Path(r['document']).parent/'source-archive-map.json')for r in required}
 while True:
  extra=[r for r in rows+own if r['original_path']in maps and r['resolution']=='live'and r not in required];before=len(maps);required+=extra;maps.update(str(Path(r['document']).parent/'source-archive-map.json')for r in extra)
  if len(maps)==before:break
 archives={};payloads={};proposals={};unioncontexts={}
 def add_archive(p,h,kind):
  archive='catalogue/source-snapshots/'+h+'/'+p;data=(gitdata if kind=='remote'else localdata)(p);assert sha(data)==h
  if archive in archives:assert payloads['prior-bytes/'+archive]==data;return
  archives[archive]={'original_path':p,'sha256':h,'archived_path':archive,'origin_namespace':kind,'already_present_in_remote':archive in objects};payloads['prior-bytes/'+archive]=data
 for r in required:add_archive(r['original_path'],r['sha256'],r['namespace'])
 for name in sorted(maps):
  try:remote=json.loads(gitdata(name));remote_sha=sha(gitdata(name))
  except subprocess.CalledProcessError:remote=None;remote_sha=None
  try:local=json.loads(localdata(name));local_sha=sha(localdata(name))
  except FileNotFoundError:local=None;local_sha=None
  m={'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
  for prior in[remote,local]:
   if not prior:continue
   assert prior['version']==m['version']
   for doc,h in prior['documents'].items():
    assert doc not in m['documents']or m['documents'][doc]==h,('Conflicting prior document pin',name,doc)
    m['documents'][doc]=h
   for entry in prior['entries']:
    same=[e for e in m['entries']if e['original_path']==entry['original_path']and e['sha256']==entry['sha256']]
    if same:assert same==[entry]
    else:m['entries'].append(entry)
  # A wholly new sidecar guards every original sibling JSON; register all unchanged siblings.
  if not remote and not local:
   for doc in objects:
    if Path(doc).parent==Path(name).parent and doc.endswith('.json')and doc!=name:m['documents'][doc]=sha(gitdata(doc))
   parent=R/Path(name).parent
   if parent.exists():
    for p in sorted(parent.glob('*.json')):m['documents'][str(p.relative_to(R))]=sha(p.read_bytes())
  for r in required:
   if str(Path(r['document']).parent/'source-archive-map.json')!=name:continue
   assert r['document']not in m['documents']or m['documents'][r['document']]==r['document_sha256']
   m['documents'][r['document']]=r['document_sha256'];entry={k:archives['catalogue/source-snapshots/'+r['sha256']+'/'+r['original_path']][k]for k in['original_path','sha256','archived_path']}
   if entry not in m['entries']:m['entries'].append(entry)
  data=(json.dumps(m,indent=2)+'\n').encode();payloads['proposed-sidecars/'+name]=data;proposals[name]={'remote_sha256':remote_sha,'isolated_premerge_sha256':local_sha,'proposed_sha256':sha(data),'merged_remote_and_isolated_maps':bool(remote and local and remote_sha!=local_sha),'documents':len(m['documents']),'entries':len(m['entries'])}
  # Retain both exact predecessors even if a predecessor currently has no live reverse pin.
  if remote:add_archive(name,remote_sha,'remote')
  if local:add_archive(name,local_sha,'isolated')
 plan={'identity':'kelvin-origin-rebase-binding-plan-v3','baseline_previous':BASE,'remote':REMOTE,'scope':'Prospective only; preserve remote and Kelvin integration receipt namespaces; no shared map mutation','planned_source_predecessors':sources,'required_additive_edges':required,'sidecar_proposals':proposals,'canonical_archives':list(archives.values()),'new_or_changed_remote_json_scanned':len(newdocs),'previous_inventory_reused':'Exact old inventory plus every new/changed remote JSON; all candidate original receipt pairs re-resolved against remote bytes/maps','summary':{'remote_primary_edges':sum(r['namespace']=='remote'and r['original_path']in TARGETS for r in required),'remote_reverse_map_edges':sum(r['namespace']=='remote'and r['original_path']not in TARGETS for r in required),'own_reverse_map_edges':sum(r['namespace']=='isolated'for r in required),'proposed_maps':len(proposals),'prior_byte_snapshots':len(archives),'untouched_preexisting_unresolved':sum(r['resolution']=='unresolved'for r in rows)}}
 (B/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');payloads['plan.json']=(B/'plan.json').read_bytes();inventory={'remote_rows':rows,'own_rows':own,'namespace_exclusion':'Explicit immutable copy markers in prepare.py; no live-root changes to copied historical closures'};payloads['inventory.json.gz']=gzip.compress(json.dumps(inventory,indent=2).encode(),mtime=0)
 (B/'members.json').write_text(json.dumps({k:sha(v)for k,v in sorted(payloads.items())},indent=2)+'\n')
 with(B/'preservation-plan.tar.gz').open('wb')as f:
  with gzip.GzipFile(fileobj=f,mode='wb',mtime=0,filename='')as gz:
   with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT)as tar:
    for name,data in sorted(payloads.items()):
     info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;tar.addfile(info,io.BytesIO(data))
 print(json.dumps(plan['summary'],indent=2))
if __name__=='__main__':main()
