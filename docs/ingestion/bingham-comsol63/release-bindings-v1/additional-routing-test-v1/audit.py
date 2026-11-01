"""Read-only new single-test target audit; no base HEAD/nine-source assertion."""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[5];OUT=pathlib.Path(__file__).resolve().parent
TARGET='tests/test_j2_main_routing.mjs';EXPECTED='9d047d8f3b03bfb802302bd2552568c6704368b7bb504561cfb1183e50583069';sha=lambda b:hashlib.sha256(b).hexdigest();assert sha((ROOT/TARGET).read_bytes())==EXPECTED
sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
EXCLUDE={'source-snapshots','source-snapshot','snapshots','frozen','frozen-sources','frozen-source','reviewed-sources','receipt-bytes','context','isolated','proposal-inputs','interface-review','initial-proposal','prior-v1','prior-v2','prior-map-bytes','candidates','planned-sidecars','proposed','prepared-v1'}
def copied(name):return any(x in EXCLUDE or 'context' in x for x in pathlib.Path(name).parts) or name.startswith('docs/ingestion/bingham-comsol63/release-bindings-v1/')
def pairs(node):
 if isinstance(node,dict):
  for p,h in node.items():
   if isinstance(h,str) and len(h)==64 and all(c in '0123456789abcdef' for c in h):yield p,h
  p=node.get('path')
  if isinstance(p,str):
   for k in ['sha256','hash']:
    if isinstance(node.get(k),str) and len(node[k])==64:yield p,node[k]
  for v in node.values():yield from pairs(v)
 elif isinstance(node,list):
  for v in node:yield from pairs(v)
def candidates(patterns):
 args=['rg','-l','-F','-g','*.json']
 for p in patterns:args+=['-e',p]
 q=subprocess.run(args+['catalogue','docs','tools','schemas','tests'],cwd=ROOT,capture_output=True,text=True);assert q.returncode in (0,1),q.stderr
 return q.stdout.splitlines()
primary=[];copied_mentions=[];secondary=[];historical=[];unresolved=[]
def row(doc,p,h):
 b=(ROOT/doc).read_bytes();r={'document':doc,'document_sha256':sha(b),'original_path':p,'sha256':h,'sidecar':str(pathlib.Path(doc).parent/'source-archive-map.json')}
 try:
  selected=checked_receipt(ROOT,doc,p,h);r['resolution']='live' if selected==ROOT/p else 'archived';r['resolved_path']=selected.relative_to(ROOT).as_posix()
 except Exception as e:r['resolution']='unresolved';r['error']=str(e)
 return r
for doc in candidates([TARGET,EXPECTED]):
 if doc.endswith('/source-archive-map.json'):continue
 v=json.loads((ROOT/doc).read_text())
 for p,h in set(pairs(v)):
  if p!=TARGET:continue
  r={'document':doc,'original_path':p,'sha256':h}
  if copied(doc):copied_mentions.append(r);continue
  rr=row(doc,p,h)
  if h!=EXPECTED:historical.append(rr)
  elif rr['resolution']=='live':primary.append(rr)
  elif rr['resolution']=='unresolved':unresolved.append(rr)
# Reverse closure of currently live map hashes; never repair a different historical identity.
maps={r['sidecar'] for r in primary};seen=set()
while True:
 live={m:sha((ROOT/m).read_bytes()) for m in maps if (ROOT/m).is_file()};changed=False
 for doc in candidates(live.values()):
  if copied(doc) or doc.endswith('/source-archive-map.json'):continue
  v=json.loads((ROOT/doc).read_text())
  for p,h in set(pairs(v)):
   if live.get(p)!=h or (doc,p,h) in seen:continue
   seen.add((doc,p,h));rr=row(doc,p,h)
   if rr['resolution']=='live':
    secondary.append(rr)
    if rr['sidecar'] not in maps:maps.add(rr['sidecar']);changed=True
   elif rr['resolution']=='unresolved':unresolved.append(rr)
 if not changed:break
maprows=[]
for m in sorted(maps):
 p=ROOT/m;v=json.loads(p.read_text()) if p.exists() else {'documents':{},'entries':[]};docs={r['document']:r['document_sha256'] for r in primary+secondary if r['sidecar']==m};conflicts=[{'document':d,'pin':v['documents'][d],'actual':h} for d,h in docs.items() if d in v['documents'] and v['documents'][d]!=h];siblings=[]
 for f in p.parent.glob('*.json'):
  if f==p:continue
  b=f.read_bytes();node=json.loads(b)
  if isinstance(node,dict) and (isinstance(node.get('files'),dict) or isinstance(node.get('dependencies'),dict)):siblings.append({'document':f.relative_to(ROOT).as_posix(),'sha256':sha(b)})
 maprows.append({'sidecar':m,'exists':p.exists(),'before_sha256':sha(p.read_bytes()) if p.exists() else None,'document_conflicts':conflicts,'siblings':siblings})
plan={'target':TARGET,'target_sha256':EXPECTED,'primary':primary,'secondary':secondary,'copied_mentions':copied_mentions,'historical_noncurrent':historical,'unresolved':unresolved,'maps':maprows,'summary':{'primary_live':len(primary),'secondary_live':len(secondary),'maps':len(maprows),'copied_mentions':len(copied_mentions),'historical_other_hashes':len(historical),'unresolved':len(unresolved)}}
(OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan['summary'],indent=2))
