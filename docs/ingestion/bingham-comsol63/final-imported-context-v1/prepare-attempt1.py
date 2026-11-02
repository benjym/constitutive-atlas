"""Prospective full imported-tree receipt preservation. No build/engine/install."""
from pathlib import Path
import ast,collections,difflib,gzip,hashlib,json,os,re,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CLONE=Path('/private/tmp/atlas-bingham-final-context-v1')
DRAFT=ROOT/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1';ADMISSION=ROOT/'docs/ingestion/bingham-comsol63/actual-integration-v3-candidates-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
encode=lambda o:(json.dumps(o,indent=2)+'\n').encode()
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() or p.is_symlink():p.unlink() # Detach fixture hardlink before any write.
 p.write_bytes(b)
def saved(n,o):put(HERE/n,encode(o))
def zipped(n,o):put(HERE/n,gzip.compress(encode(o),mtime=0))
def safe(n):return isinstance(n,str) and not Path(n).is_absolute() and '..' not in Path(n).parts
valid=lambda x:isinstance(x,str) and bool(re.fullmatch('[0-9a-f]{64}',x))
# Reuse accepted scanner owner-context classification, do not execute draft authoring.
tree=ast.parse((DRAFT/'audit_preservation.py').read_text())
EXCLUDED=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='excluded' for t in n.targets))
EXCLUDED|={'final-imported-context-v1','actual-integration-v3-candidates-v1','qualified-engine-candidate-v5','qualified-engine-evidence-v5','package-inputs-v3-preparation-v1'}
def excluded(n):return sorted(set(Path(n).parts)&EXCLUDED | {x for x in Path(n).parts if re.fullmatch(r'prior-v\d+',x)})
def pairs(node):
 if isinstance(node,dict):
  for k,v in node.items():
   if valid(v) and ('/' in k or '.' in k or (ROOT/k).is_file()):yield k,v
  if isinstance(node.get('path'),str):
   for k in ['sha256','hash']:
    if valid(node.get(k)):yield node['path'],node[k]
  for v in node.values():yield from pairs(v)
 elif isinstance(node,list):
  for v in node:yield from pairs(v)
PRUNE={'.git','.local','__pycache__','node_modules','consumer-context','routing-context','regression-context','final-imported-context-v1'}
def files(root):
 for folder,dirs,names in os.walk(root):
  dirs[:]=sorted(d for d in dirs if d not in PRUNE and not d.startswith('.mock-') and not d.startswith('build-') and not d.startswith('.venv'))
  for name in sorted(names):
   p=Path(folder)/name
   if not p.is_symlink() and p.is_file() and p.suffix not in {'.pyc'}:yield p
if CLONE.exists():raise SystemExit('Refusing existing private clone; retain prior attempt separately')
CLONE.mkdir();inventory={}
for p in files(ROOT):
 n=p.relative_to(ROOT).as_posix()
 if n.split('/')[0] not in {'atlas','catalogue','cmake','cpp','docs','models','runtimes','schemas','tests','tools','web','.github'} and '/' in n:continue
 inventory[n]=sha(p);target=CLONE/n;target.parent.mkdir(parents=True,exist_ok=True);os.link(p,target)
zipped('imported-input-inventory.json.gz',inventory)
composition=json.loads((DRAFT/'COMPOSITION.json').read_text());receipt=json.loads((ADMISSION/'RECEIPT.json').read_text());selected={};sources={}
for folder,key in [('candidates','candidate_files'),('preservation-candidates','preservation_files')]:
 for n,h in composition[key].items():
  p=DRAFT/folder/n;assert sha(p)==h,(n,h);selected[n]=h;sources[n]=str(p)
for n,h in receipt['outputs'].items():
 p=ADMISSION/n;assert sha(p)==h
 if n in selected:assert selected[n]==h
 selected[n]=h;sources[n]=str(p)
for n,h in selected.items():put(CLONE/n,Path(sources[n]).read_bytes())
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review
review='catalogue/agent-reviews/bingham-comsol63-agent-v1.json';assert sha(ROOT/review)=='61022026949f2ce9b9a536ab564239edd97ac0b5b3ba66f4ffe3f0066aa6b836'
def outcome(root,d,n,h):
 try:
  p=checked_receipt(root,d,n,h);return {'ok':True,'resolved':p.relative_to(root).as_posix(),'sha256':sha(p)}
 except Exception as e:return {'ok':False,'error_type':type(e).__name__,'error':str(e).replace(str(root),'<ROOT>')}
documents={};excluded_docs={};edges=[]
for n in inventory:
 if not n.endswith('.json') or n.endswith('/source-archive-map.json'):continue
 ex=excluded(n)
 if ex:excluded_docs[n]=ex;continue
 try:node=json.loads((ROOT/n).read_text())
 except (UnicodeError,json.JSONDecodeError):continue
 found=sorted(set(pairs(node)))
 if not found:continue
 documents[n]=inventory[n]
 for path,h in found:edges.append({'document':n,'original_path':path,'sha256':h,'before':outcome(ROOT,n,path,h)})
print(json.dumps({'input_files':len(inventory),'active_receipt_documents':len(documents),'recognized_pairs':len(edges),'excluded_copied_namespace_json':len(excluded_docs)}),flush=True)
# Additive maps only. Existing document pins/entries are never replaced.
changes={};archive_origins={};sourced=[]
def change_map(doc,path=None,h=None,source=None,reason='preservation'):
 n=(Path(doc).parent/'source-archive-map.json').as_posix();live=CLONE/n
 old=json.loads(live.read_text()) if live.exists() else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 new=json.loads(json.dumps(old))
 for sibling in live.parent.glob('*.json'):
  sn=sibling.relative_to(CLONE).as_posix()
  if sibling.name!='source-archive-map.json' and sn not in new['documents']:new['documents'][sn]=sha(sibling)
 if path is not None:
  archived='catalogue/source-snapshots/'+h+'/'+path;entry={'original_path':path,'sha256':h,'archived_path':archived}
  found=[x for x in new['entries'] if x.get('original_path')==path and x.get('sha256')==h]
  if found:assert found==[entry],(doc,path,'conflicting original map')
  else:new['entries'].append(entry)
  ap=CLONE/archived
  if ap.exists():assert sha(ap)==h
  else:
   assert source is not None and sha(source)==h,(path,h,source)
   put(ap,source.read_bytes());archive_origins[archived]={'source':str(source),'sha256':h,'reason':reason}
 if new==old:return False
 if n not in changes:
  original=ROOT/n
  changes[n]={'before_sha256':sha(original) if original.exists() else None,'reasons':[]}
  if original.exists():
   archived='catalogue/source-snapshots/'+sha(original)+'/'+n
   put(CLONE/archived,original.read_bytes());archive_origins[archived]={'source':str(original),'sha256':sha(original),'reason':'immutable previous sidecar bytes'}
 changes[n]['reasons'].append({'document':doc,'path':path,'sha256':h,'reason':reason})
 put(live,encode(new));return True
# Canonical actual E5 document must be explicitly recognized by its sibling sidecar.
change_map(review,reason='actual canonical accepted Bingham E5 document')
# Restore only declared source-capsule records, using exact known source bytes.
PROVIDERS=[Path('/private/tmp/atlas-time-profile-v2'),Path('/private/tmp/atlas-bingham-delivery-v1'),Path('/private/tmp/atlas-bingham-release-v2')]
def provider(path,h):
 for candidate in [ROOT/'catalogue/source-snapshots'/h/path,CLONE/'catalogue/source-snapshots'/h/path]+[r/path for r in PROVIDERS]:
  if candidate.is_file() and sha(candidate)==h:return candidate
 return None
capsule_docs=[];capsule_gaps=[]
for d in documents:
 if not (d.startswith('docs/ingestion/bingham-comsol63/execution-') or d.startswith('docs/investigations/physical-time-v2-')):continue
 if not (Path(d).name.startswith(('freeze','FREEZE','source-bindings'))):continue
 capsule_docs.append(d)
 for n,h in sorted(set(pairs(json.loads((ROOT/d).read_text())))):
  if not safe(n) or not (n=='CMakeLists.txt' or n.startswith(('atlas/','cpp/','schemas/','cmake/','runtimes/','tests/','tools/','models/','docs/'))):continue
  if outcome(CLONE,d,n,h)['ok']:continue
  src=provider(n,h)
  if src:
   change_map(d,n,h,src,'source capsule exact-byte restoration');sourced.append({'document':d,'path':n,'sha256':h,'provider':str(src)})
  else:capsule_gaps.append({'document':d,'path':n,'sha256':h})
# Replay every active original consumer; repair only original passes using its
# actual resolved immutable bytes. Iterate for reverse edges to changed sidecars.
rounds=[]
for iteration in range(20):
 repaired=0
 for e in edges:
  if not e['before']['ok']:continue
  d,n,h=e['document'],e['original_path'],e['sha256'];after=outcome(CLONE,d,n,h)
  if after['ok'] and after['sha256']==h:continue
  if not safe(n):raise ValueError(('unsafe original passing edge',e))
  src=ROOT/e['before']['resolved'];repaired+=change_map(d,n,h,src,'preserve previously passing edge')
 rounds.append({'iteration':iteration,'map_extensions':repaired});print(rounds[-1],flush=True)
 if repaired==0:break
else:raise ValueError('Reverse closure failed to terminate')
summary=collections.Counter();failures=[]
for e in edges:
 a=outcome(CLONE,e['document'],e['original_path'],e['sha256']);b=e['before'];e['after']=a
 if b['ok']:
  if a['ok'] and a['sha256']==b['sha256']:summary['preserved_pass']+=1
  else:summary['newly_broken']+=1;failures.append(e)
 elif a['ok']:summary['restored_prior_failure']+=1
 elif a==b:summary['retained_failure']+=1
 else:summary['changed_failure']+=1;failures.append(e)
summary.update({'pairs':len(edges),'documents':len(documents),'maps_changed':len(changes),'source_capsule_restorations':len(sourced),'source_capsule_gaps':len(capsule_gaps),'newly_broken':summary['newly_broken'],'changed_failure':summary['changed_failure']})
zipped('REPLAY.json.gz',{'summary':dict(summary),'edges':edges,'failures':failures,'rounds':rounds,'excluded_copied_namespaces':excluded_docs,'exclusion_parts':sorted(EXCLUDED)})
saved('SOURCE-CAPSULES.json',{'documents':capsule_docs,'restored':sourced,'gaps':capsule_gaps})
# Every new/changed map and every selected old-byte archive is a proposal, not install.
proposals={}
for n in changes:
 proposals[n]=sha(CLONE/n)
 before=(ROOT/n).read_text() if (ROOT/n).exists() else ''
 put(HERE/'diffs'/(n+'.diff'),''.join(difflib.unified_diff(before.splitlines(True),(CLONE/n).read_text().splitlines(True),fromfile='before/'+n,tofile='proposed/'+n)).encode())
for n in archive_origins:proposals[n]=sha(CLONE/n)
for n,h in proposals.items():put(HERE/'preservation-candidates'/n,(CLONE/n).read_bytes())
saved('PRESERVATION.json',{'maps':changes,'files':proposals,'archive_origins':archive_origins})
saved('COMPOSITION.json',{'selected_source_and_admission_files':selected,'selected_file_sources':sources,'preservation_files':proposals,'private_context':str(CLONE),'source_root':str(ROOT),'installed':False,'compiled_calls':0})
saved('SUMMARY.json',dict(summary));print(json.dumps(dict(summary),indent=2),flush=True)
# Normal scientific envelope validation is separate from receipt pair enumeration.
try:
 v=validate_review(CLONE/review,root=CLONE,for_approval=True);check={'passed':True,'artifacts':len(v['artifacts'])}
except Exception as e:check={'passed':False,'error_type':type(e).__name__,'error':str(e)}
saved('E5-VALIDATION.json',check);print('E5',check,flush=True)
zipped('prospective-context-inventory.json.gz',{p.relative_to(CLONE).as_posix():sha(p) for p in files(CLONE)})
if failures:raise SystemExit('Replay differences retained; do not install')
