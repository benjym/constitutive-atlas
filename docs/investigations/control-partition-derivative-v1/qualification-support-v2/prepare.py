"""Prepare isolated support context only; no compiler, model or artifact execution."""
import hashlib,json,re,subprocess
from collections import deque
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];CAP=OUT.parent
BASE='3873a48b256ed37cbc78378ee6b41d73139676f8'
DEST=Path('/private/tmp/atlas-control-partition-support-v1/source')
SOURCE_RECEIPT=ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v5/source-freeze.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def git(*args,input=None):return subprocess.check_output(['git',*args],cwd=ROOT,input=input)
def safe(p):
 q=Path(p);return not q.is_absolute() and '..'not in q.parts and str(q)not in ['.','']
paths=set(git('ls-tree','-r','--name-only',BASE).decode().splitlines());cache={}
def fetch(p):
 if p not in paths:return None
 if p not in cache:cache[p]=git('show',BASE+':'+p)
 return cache[p]
receipt=json.loads(SOURCE_RECEIPT.read_text());old=Path(receipt['source_directory']);selected=json.loads((CAP/'qualification-support-v1/support-selection.json').read_text())['files']
assert sha(SOURCE_RECEIPT.read_bytes())=='4bdaf4c5ac59324a644d533e2699d32b2272036803e9927968552e86ebb5dea8'
DEST.mkdir(parents=True,exist_ok=True) # Resume is read/byte-verify only; install always refuses differing existing bytes.
def install(p,b):
 assert safe(p),p
 q=DEST/p
 if q.exists():assert q.read_bytes()==b,'refuse overwrite: '+p
 else:q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
for p,h in receipt['source_files'].items():
 b=(old/p).read_bytes();assert sha(b)==h,p;install(p,b)
ordered=sorted(selected)
raw=git('cat-file','--batch',input=''.join(BASE+':'+p+'\n'for p in ordered).encode());offset=0;overlap=[]
for p in ordered:
 end=raw.index(b'\n',offset);size=int(raw[offset:end].split()[2]);offset=end+1;b=raw[offset:offset+size];offset+=size+1
 assert sha(b)==selected[p]['sha256'],p;cache[p]=b
 if p in receipt['source_files']:overlap.append(dict(path=p,baseline_sha256=sha(b),preserved_sha256=sha((DEST/p).read_bytes()),equal=(DEST/p).read_bytes()==b))
 else:install(p,b)
save('overlaps.json',dict(count=len(overlap),entries=overlap,preserved_every_source_receipt_byte=True))
plan=json.loads((CAP/'release-bindings-v2/archive-plan.json').read_text());archives=[]
for item in plan['canonical_old_bytes']:
 commit,path=item['git_source'].split(':',1);b=git('show',commit+':'+path);assert sha(b)==item['sha256'],path;install(item['canonical_archive'],b);archives.append(dict(path=item['canonical_archive'],sha256=sha(b),source=item['git_source']))
save('installed-plan-archives.json',archives)
# Named documentary closure only, rooted at the nine registry entries. No scan of nested archives.
registry=json.loads((DEST/'catalogue/approved-models.json').read_text())['models']
needles=['power-creep','burgers','sls','j2-linear','orthotropic','maxwell','norsand','lade-duncan','hill']
approvals=[a for a in registry if any(n in a['model_id']for n in needles) and a.get('review',{}).get('kind')=='agent-model-review']
assert len(approvals)==9,[a['model_id']for a in approvals]
queue=deque();seen=set();edges=[];gaps=[];routes=[];loaded=set()
hexpat=re.compile(r'^[0-9a-f]{64}$')
def pins(node):
 found=[]
 if isinstance(node,dict):
  p=node.get('path')
  if isinstance(p,str)and safe(p):
   for k in ['sha256','hash','definition_sha256']:
    h=node.get(k)
    if isinstance(h,str)and hexpat.fullmatch(h):found.append((p,h));break
  for p,h in node.items():
   if isinstance(p,str)and '/'in p and safe(p)and isinstance(h,str)and hexpat.fullmatch(h):found.append((p,h))
   if isinstance(h,(dict,list)):found+=pins(h)
 elif isinstance(node,list):
  for v in node:found+=pins(v)
 return list(dict.fromkeys(found))
for a in approvals:
 for p,h in pins(a):queue.append(('catalogue/approved-models.json',p,h))
# Explicit guards' textual/interface inputs absent from registry pin traversal.
explicit=['docs/admission/maxwell-agent-v2/approval.json','docs/ingestion/maxwell-itasca900/atlas-controller-v1/independent-review/receipt.json','docs/reviews/maxwell-checklist-v2/README.md','docs/ingestion/norsand-1993/supplied-original-v2/source-receipt.json','docs/ingestion/norsand-1993/approval-v1/REPORT.md']
for p in explicit:
 b=fetch(p)
 if b is not None:queue.append(('explicit-guard-input',p,sha(b)))
while queue and len(seen)<6000:
 document,p,h=queue.popleft();key=(document,p,h)
 if key in seen:continue
 seen.add(key);canonical='catalogue/source-snapshots/'+h+'/'+p
 live=DEST/p;b=live.read_bytes()if live.is_file()and sha(live.read_bytes())==h else None;location=p if b is not None else None
 if b is None:
  candidate=fetch(p)
  if candidate is not None and sha(candidate)==h:
   if not live.exists():install(p,candidate);location=p;b=candidate
   else:install(canonical,candidate);location=canonical;b=candidate
 if b is None:
  candidate=(DEST/canonical).read_bytes()if (DEST/canonical).is_file()else fetch(canonical)
  if candidate is not None and sha(candidate)==h:install(canonical,candidate);location=canonical;b=candidate
 edge=dict(document=document,path=p,sha256=h,selected_location=location)
 edges.append(edge)
 if b is None:gaps.append(dict(edge,reason='Exact bytes unavailable at baseline live/canonical paths or named installed archive plan'));continue
 # Restore published sidecar byte-for-byte when present. Never synthesize or edit maps.
 sidecar=str(Path(document).parent/'source-archive-map.json')
 if document!='explicit-guard-input'and safe(sidecar):
  mapping=fetch(sidecar)
  if mapping is not None and not(DEST/sidecar).exists():install(sidecar,mapping)
 if location!=p:
  routed=False;reason='No original matching sidecar entry; canonical bytes alone do not redirect guards'
  if (DEST/sidecar).is_file():
   m=json.loads((DEST/sidecar).read_text())
   matches=[x for x in m.get('entries',[])if x.get('original_path')==p and x.get('sha256')==h and x.get('archived_path')==canonical]
   docfile=DEST/document
   routed=bool(len(matches)==1 and docfile.is_file()and m.get('documents',{}).get(document)==sha(docfile.read_bytes()))
   if not routed:reason='Published sidecar does not bind this document/path/hash pair (existing maps preserved)'
  routes.append(dict(edge,routed=routed,reason=None if routed else reason))
 # JSON traversal follows exact hash edges, with cycle guard and bounded size.
 if location not in loaded and p.endswith('.json'):
  loaded.add(location)
  try:node=json.loads(b)
  except (ValueError,UnicodeDecodeError):continue
  for target,digest in pins(node):queue.append((p,target,digest))
save('documentary-closure.json',dict(base=BASE,root_models=[a['model_id']for a in approvals],edges=edges,missing_bytes=gaps,archived_routing=routes,queue_remaining=len(queue),bound=6000,complete=False,scope='Bounded recursive exact path/hash edges of nine approvals and explicit guard receipts; semantic checker-specific and unpinned dependencies require review. Existing maps/receipts are never edited.'))
# Recompute actual matching file sets on the isolated source, including new cpp fixture.
files={p.relative_to(DEST).as_posix():sha(p.read_bytes())for p in DEST.rglob('*')if p.is_file()}
maxwell={p for p in files if (p.startswith('atlas/')and p.endswith('.py')or p.startswith('cpp/')and p.endswith(('.cpp','.hpp'))or p.startswith('schemas/')and p.endswith('.json')or p.startswith('cpp/scalar-functions/'))and '__pycache__'not in p.split('/')}
maxwell|={'cmake/maxwell/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'}
norsand={p for p in files if (p.startswith('atlas/')and p.endswith('.py')or p.startswith('cpp/include/atlas/')and p.endswith('.hpp')or p.startswith('schemas/')and p.endswith('.json')or p.startswith('cpp/scalar-functions/'))and '__pycache__'not in p.split('/')}
norsand|={'cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'}
save('patched-source-manifests.json',dict(source_directory=str(DEST),profiles={name:dict(files={p:files[p]for p in sorted(names)},sha256=sha(json.dumps({p:files[p]for p in sorted(names)},sort_keys=True,separators=(',',':')).encode()))for name,names in [('maxwell',maxwell),('norsand',norsand)]}))
assert all(sha((old/p).read_bytes())==h and sha((DEST/p).read_bytes())==h for p,h in receipt['source_files'].items())
save('source-freeze.json',dict(identity='generic-control-qualification-support-source-v2',source_directory=str(DEST),runtime_receipt_sha256=sha(SOURCE_RECEIPT.read_bytes()),baseline=BASE,selected_manifest_sha256=sha((CAP/'qualification-support-v1/manifest.json').read_bytes()),source_files=files,source_file_count=len(files),original582_reverified_after_preparation=True,overlap_differences=[x for x in overlap if not x['equal']],historical_closure_complete=False))
print(json.dumps(dict(source_files=len(files),overlap=len(overlap),preserved_differences=[x['path']for x in overlap if not x['equal']],archive_targets=len(archives),closure_edges=len(edges),missing_bytes=len(gaps),unrouted=sum(not x['routed']for x in routes),remaining=len(queue),maxwell=len(maxwell),norsand=len(norsand))))
