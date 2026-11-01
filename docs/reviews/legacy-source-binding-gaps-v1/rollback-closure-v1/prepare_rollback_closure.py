"""Read-only proposal for exact-byte archival redirects; never changes repository."""
from pathlib import Path
import json,hashlib,subprocess,re,collections,time
root=Path('/Users/bmar5496/code/constitutive-atlas').resolve();out=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1/rollback-plan-v1');out.mkdir(exist_ok=True);HEX=re.compile(r'[0-9a-f]{64}\Z');excluded={'source-snapshots','source-snapshot','snapshots','frozen','frozen-sources','reviewed-sources'}
sha=lambda b:hashlib.sha256(b).hexdigest()
files=subprocess.check_output(['rg','--files','catalogue','docs','tools','schemas','tests','-g','*.json'],cwd=root,text=True).splitlines();refs=[];scanned=[];errors=[]
def pairs(n):
 if isinstance(n,dict):
  for k,v in n.items():
   if k.endswith('/source-archive-map.json') and isinstance(v,str) and HEX.fullmatch(v):yield k,v,'direct-map'
  for pk in ['path','original_path']:
   path=n.get(pk)
   if isinstance(path,str) and path.endswith('/source-archive-map.json'):
    for hk in ['sha256','hash']:
     if isinstance(n.get(hk),str) and HEX.fullmatch(n[hk]):yield path,n[hk],pk+'-object'
  for v in n.values():
   if isinstance(v,(dict,list)):yield from pairs(v)
 elif isinstance(n,list):
  for v in n:
   if isinstance(v,(dict,list)):yield from pairs(v)
for rel in files:
 p=root/rel
 if any(x in excluded for x in Path(rel).parts):continue
 if not p.resolve().is_relative_to(root):errors.append({'file':rel,'error':'external symlink excluded'});continue
 raw=p.read_bytes()
 # All JSON escaped ASCII forms use \u; escaped / leaves the basename literal.
 if b'source-archive-map.json' not in raw and b'\\u' not in raw:continue
 try:n=json.loads(raw)
 except Exception as e:errors.append({'file':rel,'error':str(e)});continue
 scanned.append({'file':rel,'digest':sha(raw),'bytes':len(raw)})
 grouped=collections.defaultdict(set)
 for path,h,shape in pairs(n):grouped[(path,h)].add(shape)
 for (path,h),shapes in grouped.items():refs.append({'document':rel,'document_digest':sha(raw),'target':path,'expected_digest':h,'shapes':sorted(shapes)})
print(json.dumps({'indexed_documents':len(scanned),'map_reference_pairs':len(refs),'errors':len(errors)}),flush=True)
proposals={};before={};queue=[];blockers=[];redirects=[]
def load_map(rel):
 if rel in proposals:return proposals[rel]
 p=root/rel
 if p.exists():
  if not p.resolve().is_relative_to(root):raise ValueError('map external symlink '+rel)
  raw=p.read_bytes();x=json.loads(raw);assert x.get('version')=='immutable-source-archive-map-0.1';before[rel]=raw
 else:x={'version':'immutable-source-archive-map-0.1','semantics':'Exact prior file identities preserved; original evidence documents unchanged.','documents':{},'entries':[]};before[rel]=None
 proposals[rel]=x;queue.append(rel);return x

def add_entry(maprel,doc,dh,path,h):
 x=load_map(maprel);dp=x.setdefault('documents',{});old=dp.get(doc)
 if old is not None and old!=dh:blockers.append({'map':maprel,'document':doc,'error':'existing document pin differs; do not overwrite','old_digest':old,'current_digest':dh});return
 dp[doc]=dh;matches=[e for e in x['entries'] if e.get('original_path')==path and e.get('sha256')==h];archive='catalogue/source-snapshots/'+h+'/'+path
 if matches:
  if len(matches)!=1 or matches[0].get('archived_path')!=archive:blockers.append({'map':maprel,'error':'ambiguous or noncanonical existing redirect','target':path})
 else:x['entries'].append({'original_path':path,'sha256':h,'archived_path':archive});redirects.append({'map':maprel,'document':doc,'target':path,'digest':h})
source='atlas/compiler.py';h='d241f835c39e4129d1b550e25d5bfad3a70c9b70a3f4dbbc15938d19c7856b60';source_raw=(root/'catalogue/investigations/solver-rollback-v1/frozen/atlas/compiler.py').read_bytes();assert sha(source_raw)==h
for suffix,docname in [('', 'protocol.json'),('native/','receipt.json'),('wasm/','receipt.json')]:
 base='catalogue/investigations/solver-rollback-v1/'+suffix;doc=base+docname;add_entry(base+'source-archive-map.json',doc,sha((root/doc).read_bytes()),source,h)
processed=set()
while queue:
 target=queue.pop(0)
 if target in processed:continue
 processed.add(target);raw=before[target]
 if raw is None:continue
 digest=sha(raw)
 for r in refs:
  if r['target']!=target or r['expected_digest']!=digest:continue
  # Existing sidecar original_path descriptors already select canonical snapshots.
  if not any(s in r['shapes'] for s in ['direct-map','path-object']):continue
  doc=r['document'];maprel=str(Path(doc).parent/'source-archive-map.json');add_entry(maprel,doc,r['document_digest'],target,digest)
mutations=[];archives=[]
for rel,x in sorted(proposals.items()):
 raw=(json.dumps(x,indent=2)+'\n').encode();old=before[rel]
 if raw==old:continue
 target=out/'proposed'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);mutations.append({'file':rel,'before_digest':sha(old) if old is not None else None,'after_digest':sha(raw),'bytes':len(raw)})
 if old is not None:
  dest=out/'archives'/'catalogue/source-snapshots'/sha(old)/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(old);archives.append({'original_file':rel,'digest':sha(old),'archive_file':'catalogue/source-snapshots/'+sha(old)+'/'+rel})
dest=out/'archives'/'catalogue/source-snapshots'/h/source;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source_raw);archives.append({'original_file':source,'digest':h,'archive_file':'catalogue/source-snapshots/'+h+'/'+source})
result={'status':'PROPOSAL ONLY; no installation or verification pass inferred','scope':'All JSON documents enumerated by rg under catalogue/docs/tools/schemas/tests, excluding named snapshot/frozen path components. Prefilter literal sidecar basename or JSON unicode escapes; parse recursively for direct/path/original_path hash pairs. Symlink escapes excluded and recorded. Embedded encoded JSON payloads not decoded.','enumerated_json':len(files),'scanned_documents':scanned,'references':refs,'errors':errors,'mutations':mutations,'archives':archives,'redirects_added':redirects,'blockers':blockers,'summary':{'proposed_maps':len(mutations),'new_maps':sum(r['before_digest'] is None for r in mutations),'archives':len(archives),'redirects_added':len(redirects),'blockers':len(blockers),'errors':len(errors)},'next':'Revalidate complete input freeze, canonical archive collisions/containment, exact old success preservation and every proposed redirect in an isolated overlay; install only after these checks pass.'};(out/'PLAN.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['summary']),flush=True)
