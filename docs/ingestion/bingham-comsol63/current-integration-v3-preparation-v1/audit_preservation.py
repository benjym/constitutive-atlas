"""Source-only current-hash reverse closure and complete sibling receipt replay.

Writes candidates/fixtures only inside this packet. Never installs shared paths.
"""
from pathlib import Path
import collections,gzip,hashlib,json,os,re,subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE='docs/ingestion/bingham-comsol63/'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
valid=lambda x:isinstance(x,str) and bool(re.fullmatch('[0-9a-f]{64}',x))
def pairs(node):
 if isinstance(node,dict):
  for k,v in node.items():
   if valid(v) and ('/' in k or '.' in k or (ROOT/k).is_file()):yield k,v
  if isinstance(node.get('path'),str):
   for f in ['sha256','hash']:
    if valid(node.get(f)):yield node['path'],node[f]
  for v in node.values():yield from pairs(v)
 elif isinstance(node,list):
  for v in node:yield from pairs(v)
def put(name,data):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(data)
def encoded(x):return (json.dumps(x,indent=2)+'\n').encode()
def safe(name):
 p=Path(name)
 return not p.is_absolute() and '..' not in p.parts and (ROOT/p).resolve().is_relative_to(ROOT)
excluded={'source-snapshots','source-snapshot','snapshots','frozen','frozen-sources','reviewed-sources','frozen-source-archive-v1','tree','consumer-context','regression-context','before','candidates','preservation-candidates','receipt-bytes','context','isolated','proposal-inputs','interface-review','archival-inputs','superseded-implementation-v1','superseded-assessor-v1','current-preservation-v2','release-bindings-v1','current-integration-preparation-v1','interface-v3-preparation-v1','interface-v3-workflow-preservation-v1','interface-v3-preservation-correction-v1','interface-v4-preparation-v1','current-integration-v3-preparation-v1','current-profile-v2-preparation-v1'}
def exclusion(name):
 parts=Path(name).parts
 return sorted(excluded.intersection(parts) | {x for x in parts if re.fullmatch(r'prior-v\d+',x)})
inputs=json.loads((HERE/'INPUTS.json').read_text())['release_inputs']
target_names=json.loads((HERE/'INPUTS.json').read_text())['archive_targets']
targets={n:inputs[n] for n in target_names}
for n,h in targets.items():assert sha(ROOT/n)==h,n
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
primary=[];reverse=[];mentions={};maps=set();scanned=set();rounds=[]
for iteration in range(20):
 active=targets if iteration==0 else {n:sha(ROOT/n) for n in maps-scanned if (ROOT/n).is_file()}
 if not active:break
 scanned.update(active)
 command=['rg','-l','-F','-g','*.json']
 for h in sorted(set(active.values())):command+=['-e',h]
 command+=['catalogue','docs','tools','tests','schemas']
 run=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
 if run.returncode not in [0,1]:raise ValueError(run.stderr)
 count=0
 for n in sorted(set(run.stdout.splitlines())):
  excluded_by=exclusion(n)
  mentions[n]={'sha256':sha(ROOT/n),'excluded_by':excluded_by}
  if excluded_by:continue
  node=json.loads((ROOT/n).read_text())
  for path,h in sorted(set(pairs(node))):
   if path not in active or h!=active[path]:continue
   # A sidecar's own original_path fields are not recognized receipt pairs.
   row={'document':n,'document_sha256':sha(ROOT/n),'original_path':path,'sha256':h,'round':iteration}
   (primary if iteration==0 else reverse).append(row);count+=1
   maps.add((Path(n).parent/'source-archive-map.json').as_posix())
 rounds.append({'round':iteration,'searched_inputs':active,'recognized_pairs':count})
else:raise ValueError('Reverse closure did not terminate')
# Existing live Bingham sidecars are included as unchanged consumer context;
# no v2 maps or old global inventories are transplanted into this current tree.
proof_maps=maps | {p.relative_to(ROOT).as_posix() for p in (ROOT/BASE).rglob('source-archive-map.json') if not exclusion(p.relative_to(ROOT).as_posix())}
print(json.dumps({'recognized_primary':len(primary),'recognized_reverse':len(reverse),'changed_maps':len(maps)}),flush=True)
docs={};map_info=[];redirects={(r['original_path'],r['sha256']) for r in primary+reverse}
for n in sorted(proof_maps):
 live=ROOT/n
 old=json.loads(live.read_text()) if live.exists() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 new=json.loads(json.dumps(old));siblings=sorted(live.parent.glob('*.json'))
 for document in siblings:
  if document.name=='source-archive-map.json':continue
  name=document.relative_to(ROOT).as_posix();docs[name]=sha(document)
  if n in maps:
   if name in new['documents']:assert new['documents'][name]==docs[name],name
   new['documents'][name]=docs[name]
 if n in maps:
  for r in primary+reverse:
   if (Path(r['document']).parent/'source-archive-map.json').as_posix()!=n:continue
   entry={'original_path':r['original_path'],'sha256':r['sha256'],'archived_path':'catalogue/source-snapshots/'+r['sha256']+'/'+r['original_path']}
   same=[e for e in new['entries'] if e['original_path']==entry['original_path'] and e['sha256']==entry['sha256']]
   if same:assert same==[entry]
   else:new['entries'].append(entry)
   archived=HERE/'preservation-candidates'/entry['archived_path']
   if not archived.exists():put('preservation-candidates/'+entry['archived_path'],(ROOT/r['original_path']).read_bytes())
  if live.exists():
   put('before/'+n,live.read_bytes())
   archive='catalogue/source-snapshots/'+sha(live)+'/'+n
   if not (HERE/'preservation-candidates'/archive).exists():put('preservation-candidates/'+archive,live.read_bytes())
  put('preservation-candidates/'+n,encoded(new))
 map_info.append({'path':n,'changed':n in maps,'before_sha256':sha(live) if live.exists() else None,'after_sha256':hashlib.sha256(encoded(new)).hexdigest() if n in maps else sha(live),'old_documents':len(old['documents']),'documents':len(new['documents']),'old_entries':len(old['entries']),'entries':len(new['entries']),'siblings':len(siblings)-(1 if live.exists() else 0)})
# Fixture contains only candidate bytes, source receipts and referenced source/archive
# files. Other immutable bytes are hardlinks; never write through those links.
fixture=HERE/'consumer-context'
def link(name):
 if not safe(name):return
 src=ROOT/name;dst=fixture/name
 if dst.exists() or dst.is_symlink():return
 if src.is_file():dst.parent.mkdir(parents=True,exist_ok=True);os.link(src.resolve(),dst)
for folder in ['candidates','preservation-candidates']:
 for source in sorted((HERE/folder).rglob('*')):
  if source.is_file():put('consumer-context/'+source.relative_to(HERE/folder).as_posix(),source.read_bytes())
for n in docs:link(n)
for n in proof_maps:
 link(n)
 mapping=json.loads((fixture/n).read_text())
 for e in mapping['entries']:link(e['archived_path'])
edges=[]
for document,digest in sorted(docs.items()):
 for path,h in sorted(set(pairs(json.loads((ROOT/document).read_text())))):
  edges.append({'document':document,'document_sha256':digest,'original_path':path,'sha256':h});link(path)
# Existing unrelated archive maps referred to by direct receipt pairs need their
# own bytes only; no alternate document context is synthesized for them.
def outcome(root,e):
 try:
  value=checked_receipt(root,e['document'],e['original_path'],e['sha256'])
  return {'ok':True,'sha256':sha(value),'resolved':value.relative_to(root).as_posix()}
 except Exception as error:return {'ok':False,'error_type':type(error).__name__,'error':str(error).replace(str(root),'<ROOT>')}
summary=collections.Counter();failures=[]
for e in edges:
 before=outcome(ROOT,e);after=outcome(fixture,e);e['before']=before;e['after']=after
 changed=(e['original_path'],e['sha256']) in redirects
 if before['ok']:
  good=after['ok'] and before['sha256']==after['sha256'];summary['before_pass']+=1
  summary['redirected_pass' if changed else 'unchanged_pass']+=int(good)
 else:
  summary['before_fail']+=1;good=not after['ok'] and before['error_type']==after['error_type'] and before['error']==after['error'];summary['retained_failures']+=int(good)
 if not good:failures.append(e)
 if before['ok'] and not after['ok']:summary['newly_broken']+=1
summary.update({'primary_edges':len(primary),'reverse_edges':len(reverse),'affected_maps':len(maps),'proof_maps':len(proof_maps),'sibling_documents':len(docs),'pairs_tested':len(edges),'failures':len(failures),'newly_broken':summary['newly_broken']})
proof={'kind':'bingham-v4-profile-source-preservation-v1','targets':targets,'primary':primary,'reverse':reverse,'rounds':rounds,'maps':map_info,'documents':docs,'summary':dict(summary),'failures':failures,'edges':edges,'exclusions':sorted(excluded),'excluded_mentions':{n:v for n,v in mentions.items() if v['excluded_by']},'installed':False,'compiled_execution':False,'receipt_pair_shapes':['direct path→SHA256','recursive {path,sha256/hash}'],'transition_fields':'path/before/after changes are immutable transition audit records, not recognized checked_receipt pairs; retained unchanged'}
put('PROOF.json.gz',gzip.compress(encoded(proof),mtime=0));put('SUMMARY.json',encoded(proof['summary']))
put('binding-mentions.json.gz',gzip.compress(encoded(mentions),mtime=0))
put('consumer-context-inventory.json.gz',gzip.compress(encoded({x.relative_to(fixture).as_posix():sha(x) for x in fixture.rglob('*') if x.is_file()}),mtime=0))
print(json.dumps(proof['summary'],indent=2))
if failures:raise SystemExit('Preservation mismatches retained; do not install')
