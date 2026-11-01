"""Read-only exact-origin/source-binding plan. Writes only this new audit packet."""
import collections,functools,gzip,hashlib,io,json,re,subprocess,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];W=Path('/Users/bmar5496/code/constitutive-atlas');D=Path('docs/ingestion/kelvin-voigt-comsol63');REMOTE='ec47f3e47b41d01a51c0cd1ef0bfecb344def694';PREVIOUS='462a450c69b0fd481fc99b67e8c42f03f82e0e97'
TARGETS={'web/app.js','tools/build_web.py','.github/workflows/verify.yml','catalogue/manifest.json','catalogue/approved-models.json','IMPLEMENTATION_PLAN.md','ROADMAP.md','docs/STATUS.md','tests/test_j2_main_routing.mjs'}
sha=lambda data:hashlib.sha256(data).hexdigest()
def encode(x):return(json.dumps(x,indent=2)+'\n').encode()
def archive(path,payload):
 with path.open('wb')as f:
  with gzip.GzipFile(fileobj=f,mode='wb',mtime=0,filename='')as gz:
   with tarfile.open(fileobj=gz,mode='w')as t:
    for name,data in sorted(payload.items()):
     z=tarfile.TarInfo(name);z.mode=0o644;z.size=len(data);t.addfile(z,io.BytesIO(data))
def excluded(name):
 return any(s in{'source-snapshots','frozen-sources','prior','prior-source','source','source-mirror','planned-sidecars','proposal-inputs','context','isolated','premerge','candidates','snapshots','prior-map-bytes','origin-before'}or re.fullmatch(r'.*-context-v\d+|prior-v\d+',s)for s in Path(name).parts)
HEX=re.compile('[0-9a-f]{64}\\Z')
def pairs(n):
 if isinstance(n,dict):
  for path,h in n.items():
   if isinstance(h,str)and HEX.fullmatch(h)and(path in TARGETS or path.endswith('/source-archive-map.json'))and not excluded(path):yield path,h
  path=n.get('path')
  if isinstance(path,str)and(path in TARGETS or path.endswith('/source-archive-map.json'))and not excluded(path):
   for k in['sha256','hash']:
    if isinstance(n.get(k),str)and HEX.fullmatch(n[k]):yield path,n[k]
  for x in n.values():yield from pairs(x)
 elif isinstance(n,list):
  for x in n:yield from pairs(x)
def main():
 assert not(B/'plan.json').exists(),'Create-only packet'
 # Snapshot complete preproposal model namespaces, not loose archival proposals.
 snapshot={};unstable=[]
 for namespace,base in [('isolated',R),('model-workspace',W)]:
  for f in sorted((base/D).rglob('*')):
   if not f.is_file()or B in f.parents or 'integration-v4'in f.relative_to(base/D).parts:continue
   data=f.read_bytes()
   if f.read_bytes()!=data:unstable.append(str(f));continue
   snapshot[namespace+'/'+str(f.relative_to(base))]=data
 for path in sorted(TARGETS):snapshot['isolated/'+path]=(R/path).read_bytes()
 for pattern in ['web/kelvin-voigt-*.mjs','tools/*kelvin_voigt*','tests/*kelvin_voigt*','models/kelvin-voigt-comsol63-deviatoric-zero-spin-ode.json']:
  for f in R.glob(pattern):
   if f.is_file():snapshot['isolated/'+str(f.relative_to(R))]=f.read_bytes()
 archive(B/'preproposal-own-context.tar.gz',snapshot);(B/'preproposal-members.json').write_bytes(encode({p:sha(v)for p,v in sorted(snapshot.items())}));(B/'preproposal.json').write_bytes(encode({'identity':'kelvin-pre-origin-ec47-own-context-v1','archive_sha256':sha((B/'preproposal-own-context.tar.gz').read_bytes()),'members_sha256':sha((B/'preproposal-members.json').read_bytes()),'members':len(snapshot),'unstable_not_snapshotted':unstable,'scope':'Complete existing model packet namespaces plus current isolated shared targets and Kelvin source files; snapshot precedes proposals'}));assert not unstable
 objects={line.split('\t',1)[1]:line.split()[2]for line in subprocess.check_output(['git','-C',str(W),'ls-tree','-r',REMOTE],text=True).splitlines()};changed=set(subprocess.check_output(['git','-C',str(W),'diff','--name-only',PREVIOUS,REMOTE],text=True).splitlines())
 proc=subprocess.Popen(['git','-C',str(W),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 cache={}
 def gitdata(path):
  if path not in objects:raise FileNotFoundError(path)
  if path not in cache:
   proc.stdin.write((objects[path]+'\n').encode());proc.stdin.flush();head=proc.stdout.readline().split();assert head[1]==b'blob';cache[path]=proc.stdout.read(int(head[2]));assert proc.stdout.read(1)==b'\n'
  return cache[path]
 own={name.removeprefix('isolated/'):data for name,data in snapshot.items()if name.startswith('isolated/')};copy_needed={};conflicts=[]
 for name,data in snapshot.items():
  if not name.startswith('model-workspace/'):continue
  path=name.removeprefix('model-workspace/')
  if not path.endswith('.json')or excluded(path)or'release-bindings-v1'in Path(path).parts:continue
  if path not in own:own[path]=data;copy_needed[path]=sha(data)
  elif own[path]!=data:conflicts.append({'path':path,'isolated_sha256':sha(own[path]),'model_workspace_sha256':sha(data),'selected':'isolated original; root drift not used'})
 def localdata(path):
  if path in own:return own[path]
  return(R/path).read_bytes()
 def classify(doc,path,h,reader):
  selected=path
  try:
   try:m=json.loads(reader(str(Path(doc).parent/'source-archive-map.json')))
   except FileNotFoundError:m=None
   if m:
    assert m['version']=='immutable-source-archive-map-0.1';assert m['documents'].get(doc)==sha(reader(doc))
    matches=[x for x in m['entries']if x['original_path']==path and x['sha256']==h];assert len(matches)<=1
    if matches:selected=matches[0]['archived_path'];assert selected=='catalogue/source-snapshots/'+h+'/'+path
   assert sha(reader(selected))==h
   return{'resolution':'live'if selected==path else'archived','resolved_path':selected}
  except Exception as e:return{'resolution':'unresolved','error':str(e)}
 rows=[];remote_docs=[p for p in objects if p.endswith('.json')and not excluded(p)];own_docs=[p for p in own if p.endswith('.json')and not excluded(p)and'release-bindings-v1'not in Path(p).parts]
 for namespace,docs,reader in [('remote',remote_docs,gitdata),('own',own_docs,localdata)]:
  for doc in sorted(docs):
   if doc.endswith('/source-archive-map.json'):continue
   try:node=json.loads(reader(doc))
   except(json.JSONDecodeError,UnicodeDecodeError):continue
   for path,h in sorted(set(pairs(node))):rows.append({'namespace':namespace,'document':doc,'document_sha256':sha(reader(doc)),'original_path':path,'sha256':h,**classify(doc,path,h,reader)})
 mapnames=set()
 for path in objects:
  if not path.endswith('/source-archive-map.json')or excluded(path):continue
  try:old=localdata(path)
  except FileNotFoundError:continue
  if old!=gitdata(path):mapnames.add(path)
 required=[r for r in rows if r['resolution']=='live'and r['original_path']in TARGETS]
 mapnames.update(str(Path(r['document']).parent/'source-archive-map.json')for r in required)
 def proposed(name):
  m={'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]};priors=[]
  for reader in[gitdata,localdata]:
   try:prior=json.loads(reader(name));priors.append(prior)
   except FileNotFoundError:continue
   assert prior['version']==m['version']
   for doc,h in prior['documents'].items():assert doc not in m['documents']or m['documents'][doc]==h,('conflicting original receipt',name,doc);m['documents'][doc]=h
   for entry in prior['entries']:
    same=[x for x in m['entries']if(x['original_path'],x['sha256'])==(entry['original_path'],entry['sha256'])]
    if same:assert same==[entry]
    else:m['entries'].append(entry)
  if not priors:
   for docs,reader in[(remote_docs,gitdata),(own_docs,localdata)]:
    for doc in docs:
     if Path(doc).parent==Path(name).parent:m['documents'][doc]=sha(reader(doc))
  for r in required:
   if str(Path(r['document']).parent/'source-archive-map.json')!=name:continue
   assert r['document']not in m['documents']or m['documents'][r['document']]==r['document_sha256'];m['documents'][r['document']]=r['document_sha256'];e={'original_path':r['original_path'],'sha256':r['sha256'],'archived_path':'catalogue/source-snapshots/'+r['sha256']+'/'+r['original_path']}
   if e not in m['entries']:m['entries'].append(e)
  return encode(m)
 while True:
  proposals={name:proposed(name)for name in sorted(mapnames)};new=[]
  for r in rows:
   if r in required or r['resolution']!='live'or r['original_path']not in proposals:continue
   if sha(proposals[r['original_path']])!=r['sha256']:new.append(r)
  if not new:break
  required+=new;mapnames.update(str(Path(r['document']).parent/'source-archive-map.json')for r in new)
 payload={};archives={};mapplan={}
 def add(path,h,reader):
  name='catalogue/source-snapshots/'+h+'/'+path;data=reader(path);assert sha(data)==h;payload['prior-bytes/'+name]=data;archives[name]={'original_path':path,'sha256':h,'archived_path':name}
 for r in required:add(r['original_path'],r['sha256'],gitdata if r['namespace']=='remote'else localdata)
 for path in TARGETS:
  for reader in[gitdata,localdata]:add(path,sha(reader(path)),reader)
 for name,data in proposals.items():
  prior={}
  for ns,reader in[('remote',gitdata),('isolated',localdata)]:
   try:old=reader(name);prior[ns+'_sha256']=sha(old)
   except FileNotFoundError:prior[ns+'_sha256']=None;continue
   if old!=data:add(name,sha(old),reader)
  mapplan[name]=dict(prior,proposed_sha256=sha(data));payload['proposed-sidecars/'+name]=data
 plan={'identity':'kelvin-origin-ec47-binding-plan-v1','remote':REMOTE,'previous_origin':PREVIOUS,'scope':'Read-only prospective shared-file/map merge; no source/map installation authorized','source_predecessors':{p:{'remote':sha(gitdata(p)),'isolated':sha(localdata(p))}for p in sorted(TARGETS)},'required_edges':required,'map_proposals':mapplan,'canonical_archives':list(archives.values()),'own_receipt_copy_prerequisites':copy_needed,'own_json_namespace_differences':conflicts,'summary':{'remote_json_scanned':len(remote_docs),'own_json_scanned':len(own_docs),'all_inventory_pairs':len(rows),'resolved_before_change':sum(r['resolution']!='unresolved'for r in rows),'unresolved_before_change':sum(r['resolution']=='unresolved'for r in rows),'required_edges':len(required),'map_contexts':len(proposals),'predecessor_snapshots':len(archives),'remote_primary_edges':sum(r['namespace']=='remote'and r['original_path']in TARGETS for r in required),'own_primary_edges':sum(r['namespace']=='own'and r['original_path']in TARGETS for r in required),'reverse_map_edges':sum(r['original_path']not in TARGETS for r in required)}}
 inventory={'rows':rows};payload['inventory.json.gz']=gzip.compress(encode(inventory),mtime=0);payload['plan.json']=encode(plan);(B/'plan.json').write_bytes(payload['plan.json']);(B/'members.json').write_bytes(encode({k:sha(v)for k,v in sorted(payload.items())}));archive(B/'preservation-plan.tar.gz',payload);(B/'artifact.json').write_bytes(encode({'archive_sha256':sha((B/'preservation-plan.tar.gz').read_bytes()),'members_sha256':sha((B/'members.json').read_bytes()),'plan_sha256':sha(payload['plan.json'])}));print(json.dumps(plan['summary'],indent=2))
 # Virtual merge: copied prerequisites, both canonical namespaces and new maps; every original resolved receipt must replay unchanged.
 errors=[];checked=0
 for row in rows:
  if row['resolution']=='unresolved':continue
  base=gitdata if row['namespace']=='remote'else localdata
  def merged(path):
   if 'proposed-sidecars/'+path in payload:return payload['proposed-sidecars/'+path]
   if 'prior-bytes/'+path in payload:return payload['prior-bytes/'+path]
   if path.startswith('catalogue/source-snapshots/'):
    try:return localdata(path)
    except FileNotFoundError:return gitdata(path)
   if path in TARGETS:return b'prospective final merged shared source bytes'
   return base(path)
  after=classify(row['document'],row['original_path'],row['sha256'],merged)
  if after['resolution']=='unresolved':errors.append(dict(row,virtual_error=after['error']))
  else:checked+=1
 result={'identity':'kelvin-origin-ec47-virtual-bindings-v1','archive_sha256':sha((B/'preservation-plan.tar.gz').read_bytes()),'checked':checked,'errors':errors,'passed':not errors};(B/'virtual-check.json').write_bytes(encode(result));print('Virtual',checked,'errors',len(errors));proc.stdin.close();proc.wait();assert not errors
if __name__=='__main__':main()
